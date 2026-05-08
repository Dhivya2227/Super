import os
import pandas as pd
import streamlit as st
from datetime import datetime

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Prediction badge colors ─────────────────────────────────────────────────
PREDICTION_COLORS = {
    'Genuine':    '#10b981',
    'Fake':       '#ef4444',
    'Irrelevant': '#f59e0b',
    'Pending':    '#6b7280',
}

RISK_COLORS = {
    'Low':    '#10b981',
    'Medium': '#f59e0b',
    'High':   '#ef4444',
}

def prediction_badge(prediction):
    color = PREDICTION_COLORS.get(prediction, '#6b7280')
    return f'<span style="background:{color};color:white;padding:3px 10px;border-radius:12px;font-size:0.8rem;font-weight:600">{prediction}</span>'

def risk_badge(risk):
    color = RISK_COLORS.get(risk, '#6b7280')
    return f'<span style="background:{color};color:white;padding:3px 10px;border-radius:12px;font-size:0.8rem;font-weight:600">{risk} Risk</span>'

def save_uploaded_file(uploaded_file, subfolder=''):
    """Save uploaded file and return path."""
    save_dir = os.path.join(UPLOAD_DIR, subfolder)
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, uploaded_file.name)
    with open(path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return path

def paginate(items, page_size=10, key='page'):
    """Simple pagination utility."""
    total = len(items)
    total_pages = max(1, (total - 1) // page_size + 1)
    if key not in st.session_state:
        st.session_state[key] = 1
    page = st.session_state[key]
    start = (page - 1) * page_size
    end = start + page_size
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Prev", key=f"{key}_prev", disabled=(page <= 1)):
            st.session_state[key] = max(1, page - 1)
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align:center'>Page {page} of {total_pages} ({total} items)</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ▶", key=f"{key}_next", disabled=(page >= total_pages)):
            st.session_state[key] = min(total_pages, page + 1)
            st.rerun()
    
    return items[start:end]

def jobs_to_dataframe(jobs):
    """Convert jobs list to pandas DataFrame."""
    if not jobs:
        return pd.DataFrame()
    return pd.DataFrame(jobs)

def format_timestamp(ts):
    """Format timestamp for display."""
    if not ts:
        return 'N/A'
    try:
        dt = datetime.strptime(str(ts), '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d %b %Y, %I:%M %p')
    except Exception:
        return str(ts)

def check_login():
    """Verify user is logged in."""
    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("Please login to continue.")
        st.stop()
    return st.session_state.user

def require_role(*roles):
    """Check user has required role."""
    user = check_login()
    if user.get('role') not in roles:
        st.error("Access denied. Insufficient permissions.")
        st.stop()
    return user

def metric_card(title, value, delta=None, icon='📊', color='#6366f1'):
    delta_html = ''
    if delta is not None:
        arrow = '↑' if delta >= 0 else '↓'
        dcolor = '#10b981' if delta >= 0 else '#ef4444'
        delta_html = f'<p style="color:{dcolor};margin:0;font-size:0.85rem">{arrow} {abs(delta)}</p>'
    
    st.markdown(f"""
    <div style="background:var(--card-bg,#1e293b);border:1px solid var(--border,#334155);
                border-radius:12px;padding:20px;text-align:center;border-top:3px solid {color}">
        <div style="font-size:2rem">{icon}</div>
        <p style="color:#94a3b8;margin:4px 0;font-size:0.85rem">{title}</p>
        <h2 style="color:white;margin:4px 0;font-size:2rem;font-weight:700">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def job_card(job, show_apply=False, show_edit=False, user_id=None):
    """Render a job posting card."""
    pred = job.get('prediction', 'Pending')
    color = PREDICTION_COLORS.get(pred, '#6b7280')
    
    st.markdown(f"""
    <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;
                padding:20px;margin-bottom:16px;border-left:4px solid {color}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
                <h3 style="color:white;margin:0 0 4px 0">{job.get('title','')}</h3>
                <p style="color:#94a3b8;margin:0">🏢 {job.get('company','N/A')} &nbsp;|&nbsp; 
                   📍 {job.get('location','N/A')} &nbsp;|&nbsp;
                   💰 {job.get('salary','Not disclosed')}</p>
            </div>
            <div>{prediction_badge(pred)}</div>
        </div>
        <p style="color:#cbd5e1;margin:12px 0 0 0;font-size:0.9rem">
            {str(job.get('description',''))[:200]}{'...' if len(str(job.get('description',''))) > 200 else ''}
        </p>
        <p style="color:#64748b;margin:8px 0 0 0;font-size:0.8rem">
            🕒 {format_timestamp(job.get('timestamp',''))} &nbsp;|&nbsp;
            💼 {job.get('employment_type','N/A')} &nbsp;|&nbsp;
            📊 Confidence: {float(job.get('confidence_score', 0))*100:.0f}%
        </p>
    </div>
    """, unsafe_allow_html=True)
