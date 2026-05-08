"""
Detection of Fake and Irrelevant Job Posting Using Passive Aggressive Classifier Model
A smart AI-powered recruitment & job verification platform
"""
import streamlit as st
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RecruitAI — Smart Job Verification",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Base */
:root {
    --bg-primary:    #0a0f1e;
    --bg-secondary:  #0d1526;
    --card-bg:       #111827;
    --border:        #1e293b;
    --border-bright: #334155;
    --text-primary:  #f1f5f9;
    --text-muted:    #94a3b8;
    --accent:        #7c3aed;
    --accent-light:  #a78bfa;
    --success:       #10b981;
    --danger:        #ef4444;
    --warning:       #f59e0b;
    --info:          #0ea5e9;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #111827 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Main area */
.main .block-container {
    background-color: var(--bg-primary) !important;
    padding: 1rem 2rem !important;
    max-width: 1400px;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Inputs */
input, textarea, select {
    background-color: #1e293b !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
input:focus, textarea:focus { 
    border-color: var(--accent) !important; 
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: #1e293b !important;
    border: 1px solid var(--border-bright) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #334155 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111827 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    border: none !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background-color: #7c3aed !important;
    color: white !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--card-bg) !important;
    padding: 16px !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Alerts */
.stSuccess { background: #064e3b !important; color: #a7f3d0 !important; border-color: #10b981 !important; }
.stError   { background: #450a0a !important; color: #fca5a5 !important; border-color: #ef4444 !important; }
.stWarning { background: #451a03 !important; color: #fde68a !important; border-color: #f59e0b !important; }
.stInfo    { background: #0c4a6e !important; color: #bae6fd !important; border-color: #0ea5e9 !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1e293b !important;
    border-color: var(--border-bright) !important;
    color: var(--text-primary) !important;
}

/* Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #0ea5e9) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0f1e; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #7c3aed; }
</style>
""", unsafe_allow_html=True)

# ── Init ─────────────────────────────────────────────────────────────────────
from database import init_db
init_db()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'auth_tab' not in st.session_state:
    st.session_state.auth_tab = 'login'

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center;padding:20px 0 12px">
        <div style="font-size:3rem">🧠</div>
        <h2 style="color:white;margin:4px 0;font-size:1.3rem;font-weight:700">RecruitAI</h2>
        <p style="color:#7c3aed;margin:0;font-size:0.8rem;letter-spacing:2px;text-transform:uppercase">Smart Job Verification</p>
    </div>
    <hr style="border-color:#1e293b;margin:8px 0 16px">
    """, unsafe_allow_html=True)

    user = st.session_state.get('user')

    if user:
        # User info
        role_badges = {
            'admin':     ('🛡️', '#7c3aed', 'Administrator'),
            'recruiter': ('🏢', '#1d4ed8', 'Recruiter'),
            'seeker':    ('🔍', '#065f46', 'Job Seeker'),
        }
        icon, color, label = role_badges.get(user['role'], ('👤', '#6b7280', 'User'))
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e293b;border-radius:10px;
                    padding:12px;margin-bottom:16px;border-left:3px solid {color}">
            <div style="display:flex;align-items:center;gap:10px">
                <span style="font-size:1.5rem">{icon}</span>
                <div>
                    <p style="color:white;margin:0;font-weight:600;font-size:0.9rem">{user['name']}</p>
                    <p style="color:#64748b;margin:0;font-size:0.75rem">{label}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("<p style='color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>NAVIGATION</p>", unsafe_allow_html=True)

        role = user['role']
        nav_options = ['🏠 Home']
        if role == 'admin':
            nav_options += ['🛡️ Admin Panel', '📊 Analytics']
        if role in ('recruiter', 'admin'):
            nav_options += ['🏢 Recruiter Dashboard']
        if role in ('seeker', 'admin'):
            nav_options += ['🔍 Job Seeker Portal']
        nav_options += ['🤖 ML Predictor', 'ℹ️ About']

        for nav in nav_options:
            if st.button(nav, key=f"nav_{nav}", use_container_width=True):
                st.session_state.current_page = nav
                st.rerun()

        st.markdown("<hr style='border-color:#1e293b;margin:16px 0'>", unsafe_allow_html=True)
        
        # Model status
        model_exists = os.path.exists('model.joblib') and os.path.exists('vectorizer.joblib')
        status_color = '#10b981' if model_exists else '#f59e0b'
        status_text = 'Model Loaded' if model_exists else 'Training Required'
        st.markdown(f"""
        <div style="background:#111827;border:1px solid #1e293b;border-radius:8px;padding:10px;margin-bottom:12px">
            <p style="color:#64748b;margin:0;font-size:0.75rem">🤖 AI Model Status</p>
            <p style="color:{status_color};margin:4px 0;font-size:0.85rem;font-weight:600">{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not model_exists:
            if st.button("⚡ Train Model", use_container_width=True):
                with st.spinner("Training AI model..."):
                    from train_model import train_model
                    _, _, acc = train_model()
                    st.success(f"Model trained! Accuracy: {acc*100:.1f}%")
                    st.rerun()

        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    else:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1e293b;border-radius:10px;
                    padding:16px;text-align:center;margin-bottom:16px">
            <p style="color:#94a3b8;margin:0;font-size:0.9rem">Sign in to access all features</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="position:absolute;bottom:20px;left:0;right:0;text-align:center">
        <p style="color:#334155;font-size:0.7rem;margin:0">PAC Model v1.0 | Python + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# ── Main Content ──────────────────────────────────────────────────────────────
user = st.session_state.get('user')
current_page = st.session_state.get('current_page', '🏠 Home')

if not user:
    # ── Auth Page ──────────────────────────────────────────────────────────────
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        # Hero section
        st.markdown("""
        <div style="text-align:center;padding:40px 0 32px">
            <div style="font-size:4rem;margin-bottom:8px">🧠</div>
            <h1 style="color:white;font-size:2.5rem;font-weight:700;margin:0">
                RecruitAI
            </h1>
            <p style="color:#7c3aed;font-size:1rem;letter-spacing:3px;text-transform:uppercase;margin:4px 0">
                Smart Job Verification Platform
            </p>
            <p style="color:#94a3b8;font-size:1rem;margin:16px 0;max-width:480px;margin:16px auto">
                Detection of Fake and Irrelevant Job Postings using 
                <strong style="color:#a78bfa">Passive Aggressive Classifier</strong> AI
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Feature pills
        features = ["✅ Fake Job Detection", "🤖 ML-Powered", "📊 Real-time Analytics", "🔐 Role-based Access"]
        st.markdown(
            "<div style='text-align:center;margin-bottom:24px'>" +
            "".join(f"<span style='background:#1e293b;border:1px solid #334155;color:#a78bfa;"
                    f"padding:4px 12px;border-radius:20px;margin:3px;font-size:0.8rem;display:inline-block'>{f}</span>"
                    for f in features) +
            "</div>",
            unsafe_allow_html=True
        )

        # Auth tabs
        tab_labels = ["🔐 Sign In", "📝 Register"]
        auth_tab = st.session_state.get('auth_tab', 'login')
        tab_idx = 0 if auth_tab == 'login' else 1
        
        tab1, tab2 = st.tabs(tab_labels)
        with tab1:
            from pages.login import render_login
            render_login()
        with tab2:
            from pages.login import render_register
            render_register()

    # Landing stats
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    landing_stats = [
        ("🎯", "Passive Aggressive", "Classifier Model"),
        ("🧬", "NLP Pipeline", "NLTK Preprocessing"),
        ("📊", "Multi-role", "Access Control"),
        ("⚡", "Real-time", "Predictions"),
    ]
    for col, (icon, title, sub) in zip([col1, col2, col3, col4], landing_stats):
        with col:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e293b;border-radius:10px;
                        padding:20px;text-align:center">
                <div style="font-size:2rem">{icon}</div>
                <h4 style="color:white;margin:8px 0 4px;font-size:1rem">{title}</h4>
                <p style="color:#64748b;margin:0;font-size:0.8rem">{sub}</p>
            </div>
            """, unsafe_allow_html=True)

else:
    # ── Authenticated Pages ────────────────────────────────────────────────────
    
    if current_page == '🏠 Home':
        from database import get_stats
        stats = get_stats()
        role = user['role']
        role_greetings = {
            'admin':     ("Welcome back, Administrator!", "You have full platform access.", '#7c3aed'),
            'recruiter': ("Welcome back, Recruiter!", "Manage your job postings and applicants.", '#1d4ed8'),
            'seeker':    ("Welcome back, Job Seeker!", "Discover genuine opportunities.", '#065f46'),
        }
        title, subtitle, color = role_greetings.get(role, ("Welcome!", "", '#6b7280'))
        
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{color},{color}88);
                    padding:32px;border-radius:16px;margin-bottom:28px">
            <h1 style="color:white;margin:0;font-size:2rem">{title}</h1>
            <p style="color:rgba(255,255,255,0.8);margin:8px 0 0">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats
        cols = st.columns(4)
        with cols[0]: st.metric("Total Jobs", stats['total_jobs'])
        with cols[1]: st.metric("✅ Genuine", stats['genuine_jobs'])
        with cols[2]: st.metric("🚨 Fake", stats['fake_jobs'])
        with cols[3]: st.metric("⚠️ Irrelevant", stats['irrelevant_jobs'])

        st.markdown("---")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        cols2 = st.columns(3)
        
        if role in ('seeker', 'admin'):
            with cols2[0]:
                if st.button("🔍 Search Jobs", use_container_width=True, type="primary"):
                    st.session_state.current_page = '🔍 Job Seeker Portal'
                    st.rerun()
        
        if role in ('recruiter', 'admin'):
            with cols2[1]:
                if st.button("➕ Post a Job", use_container_width=True):
                    st.session_state.current_page = '🏢 Recruiter Dashboard'
                    st.rerun()
        
        with cols2[2]:
            if st.button("🤖 Test ML Model", use_container_width=True):
                st.session_state.current_page = '🤖 ML Predictor'
                st.rerun()

        # Platform info
        st.markdown("---")
        st.subheader("🧬 How Our AI Works")
        col1, col2, col3 = st.columns(3)
        steps = [
            ("1️⃣", "Text Processing", "Job text is cleaned using NLTK: tokenization, lemmatization, stopword removal"),
            ("2️⃣", "TF-IDF Vectorization", "Processed text is converted into numerical feature vectors"),
            ("3️⃣", "PAC Prediction", "Passive Aggressive Classifier predicts: Genuine, Fake, or Irrelevant"),
        ]
        for col, (num, title, desc) in zip([col1, col2, col3], steps):
            with col:
                st.markdown(f"""
                <div style="background:#111827;border:1px solid #1e293b;border-radius:12px;
                            padding:20px;height:140px">
                    <div style="font-size:1.5rem">{num}</div>
                    <h4 style="color:#a78bfa;margin:8px 0 6px">{title}</h4>
                    <p style="color:#64748b;margin:0;font-size:0.85rem">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

    elif current_page == '🛡️ Admin Panel' or current_page == '📊 Analytics':
        from pages.admin import render_admin
        render_admin()

    elif current_page == '🏢 Recruiter Dashboard':
        from pages.recruiter import render_recruiter
        render_recruiter()

    elif current_page == '🔍 Job Seeker Portal':
        from pages.seeker import render_seeker
        render_seeker()

    elif current_page == '🤖 ML Predictor':
        st.markdown("""
        <div style="background:linear-gradient(135deg,#312e81,#4c1d95);padding:24px;border-radius:12px;margin-bottom:24px">
            <h1 style="color:white;margin:0;font-size:1.8rem">🤖 ML Prediction Sandbox</h1>
            <p style="color:#c4b5fd;margin:4px 0">Test the Passive Aggressive Classifier in real-time</p>
        </div>
        """, unsafe_allow_html=True)

        from predict import predict_job, get_risk_explanation, get_red_flags
        import time

        col1, col2 = st.columns([3, 2])
        with col1:
            with st.form("ml_test_form"):
                title_input = st.text_input("Job Title *", placeholder="e.g., Python Developer")
                description_input = st.text_area("Job Description *", height=150,
                    placeholder="Describe the role, responsibilities...")
                requirements_input = st.text_area("Requirements", height=100,
                    placeholder="List qualifications and skills required...")
                skills_input = st.text_input("Skills", placeholder="Python, SQL, AWS...")
                
                predict_btn = st.form_submit_button("🚀 Run AI Prediction", type="primary", use_container_width=True)

        if predict_btn:
            if not title_input or not description_input:
                st.error("Job title and description are required.")
            else:
                with st.spinner("🤖 Running Passive Aggressive Classifier..."):
                    progress = st.progress(0)
                    status = st.empty()
                    steps_ml = [
                        (20, "🔤 Preprocessing text with NLTK..."),
                        (40, "🧹 Removing stopwords & lemmatizing..."),
                        (60, "📐 TF-IDF vectorization..."),
                        (80, "⚙️ Running PAC inference..."),
                        (100, "✅ Prediction complete!"),
                    ]
                    for prog, msg in steps_ml:
                        status.markdown(f"<p style='color:#a78bfa'>{msg}</p>", unsafe_allow_html=True)
                        progress.progress(prog)
                        time.sleep(0.3)

                result = predict_job(title_input, description_input, requirements_input, skills_input)

        with col2:
            st.subheader("📊 Prediction Result")
            
            if 'result' not in dir():
                st.markdown("""
                <div style="background:#111827;border:1px dashed #334155;border-radius:12px;
                            padding:40px;text-align:center">
                    <p style="color:#334155;font-size:3rem;margin:0">🤖</p>
                    <p style="color:#64748b">Submit a job to see prediction</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                pred = result['prediction']
                conf = result['confidence']
                colors = {'Genuine': '#10b981', 'Fake': '#ef4444', 'Irrelevant': '#f59e0b'}
                icons = {'Genuine': '✅', 'Fake': '🚨', 'Irrelevant': '⚠️'}
                color = colors.get(pred, '#6b7280')
                icon = icons.get(pred, '📊')

                st.markdown(f"""
                <div style="background:#111827;border:2px solid {color};border-radius:12px;
                            padding:24px;text-align:center;margin-bottom:16px">
                    <div style="font-size:3rem">{icon}</div>
                    <h2 style="color:{color};margin:8px 0">{pred}</h2>
                    <div style="background:#1e293b;border-radius:8px;padding:8px;margin:8px 0">
                        <p style="color:#94a3b8;margin:0;font-size:0.85rem">Confidence Score</p>
                        <h3 style="color:white;margin:4px 0">{conf*100:.1f}%</h3>
                    </div>
                    <p style="color:#94a3b8;margin:0;font-size:0.85rem">
                        Risk Level: <strong style="color:{color}">{result['risk_level']}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                if result.get('details'):
                    st.subheader("Class Probabilities")
                    for cls, prob in result['details'].items():
                        cls_color = colors.get(cls, '#6b7280')
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                            <span style="color:#94a3b8">{cls}</span>
                            <span style="color:{cls_color};font-weight:600">{prob*100:.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.progress(prob)

                explanations = get_risk_explanation(pred, conf)
                st.subheader("🔍 Analysis")
                for exp in explanations:
                    st.markdown(f"<p style='color:#94a3b8;margin:4px 0;font-size:0.85rem'>{exp}</p>", unsafe_allow_html=True)

                red_flags = get_red_flags(title_input, description_input, requirements_input)
                if red_flags:
                    st.subheader("🚩 Red Flags Detected")
                    for flag in red_flags:
                        st.markdown(f"<span style='background:#450a0a;color:#fca5a5;padding:3px 10px;border-radius:6px;display:inline-block;margin:2px;font-size:0.8rem'>{flag}</span>", unsafe_allow_html=True)

        # Pre-built test cases
        st.markdown("---")
        st.subheader("📋 Test Cases — Click to Load")
        col1, col2, col3 = st.columns(3)
        test_cases = [
            ("✅ Genuine Job", "Senior Software Engineer", 
             "We are looking for an experienced Python developer to join our product team at TechCorp. You will design and build RESTful APIs, work with cloud infrastructure on AWS, mentor junior developers, and contribute to our microservices architecture.",
             "5+ years Python experience, AWS certification, strong SQL skills, experience with Docker and Kubernetes, excellent communication skills"),
            
            ("🚨 Fake Job", "URGENT: Work From Home Data Entry",
             "MAKE MONEY FROM HOME! Earn Rs.5000 per day! No experience required! Call us immediately on WhatsApp! Limited seats available! 100% guaranteed income! Easy online job! Immediate joining! Send your Aadhar and bank details to our email.",
             "No qualification needed. All ages welcome. Just need WhatsApp. Pay Rs.500 registration fee to start."),
            
            ("⚠️ Irrelevant Post", "2BHK Flat for Rent",
             "Beautiful 2BHK apartment available for rent near metro station. Fully furnished with modern amenities. 24/7 security, gym, parking available. Contact the owner directly. No brokerage. Immediate possession available.",
             "Good tenant required. Family preferred. Contact on mobile."),
        ]
        for col, (label, t, d, r) in zip([col1, col2, col3], test_cases):
            with col:
                colors_map = {'✅': '#064e3b', '🚨': '#450a0a', '⚠️': '#451a03'}
                bg = colors_map.get(label[0], '#111827')
                st.markdown(f"""
                <div style="background:{bg};border:1px solid #334155;border-radius:10px;padding:16px;margin-bottom:8px">
                    <h4 style="color:white;margin:0 0 8px">{label}</h4>
                    <p style="color:#94a3b8;font-size:0.8rem;margin:0"><b>Title:</b> {t[:50]}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Load {label}", key=f"load_{label}", use_container_width=True):
                    st.session_state['prefill_title'] = t
                    st.session_state['prefill_desc'] = d
                    st.session_state['prefill_req'] = r
                    st.info("ℹ️ Copy the text above into the form and click 'Run AI Prediction'")

    elif current_page == 'ℹ️ About':
        st.markdown("""
        <div style="background:linear-gradient(135deg,#0f172a,#1e293b);padding:32px;border-radius:16px;margin-bottom:24px">
            <h1 style="color:white;margin:0;font-size:2rem">🧠 About RecruitAI</h1>
            <p style="color:#94a3b8;margin:8px 0">Detection of Fake and Irrelevant Job Postings Using Passive Aggressive Classifier</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("🎯 Project Objective")
            st.markdown("""
            This platform uses Machine Learning — specifically the **Passive Aggressive Classifier (PAC)** — 
            to automatically detect fake, fraudulent, and irrelevant job postings in real-time.

            **The problem it solves:**
            - Job seekers waste time on fraudulent postings
            - Personal data theft via fake job applications  
            - Financial scams disguised as employment opportunities
            - Spam and irrelevant listings polluting job boards

            **Our solution:** An end-to-end AI pipeline that analyzes job text and classifies each posting 
            as *Genuine*, *Fake*, or *Irrelevant* with a confidence score.
            """)

            st.subheader("🔬 ML Pipeline")
            pipeline_steps = [
                ("Data Collection", "Fake job postings dataset with 17,880+ records"),
                ("Text Preprocessing", "HTML removal, URL cleaning, lowercasing, punctuation removal"),
                ("NLP Processing", "NLTK tokenization, stopword removal, lemmatization"),
                ("Feature Extraction", "TF-IDF Vectorization (15,000 features, bigrams)"),
                ("Model Training", "Passive Aggressive Classifier with C=1.0"),
                ("Evaluation", "Train-test split 80/20, accuracy & classification report"),
                ("Deployment", "Joblib serialization, real-time Streamlit inference"),
            ]
            for step, detail in pipeline_steps:
                st.markdown(f"""
                <div style="background:#111827;border:1px solid #1e293b;border-radius:8px;
                            padding:12px;margin-bottom:8px;display:flex;align-items:center;gap:12px">
                    <span style="color:#7c3aed;font-weight:700;min-width:180px">{step}</span>
                    <span style="color:#94a3b8;font-size:0.9rem">{detail}</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.subheader("🛠️ Tech Stack")
            tech = [
                ("🐍", "Python 3.10+", "Core language"),
                ("🌊", "Streamlit", "Web framework"),
                ("🧬", "Scikit-learn", "Machine learning"),
                ("📝", "NLTK", "NLP processing"),
                ("📊", "Plotly", "Visualization"),
                ("🗄️", "SQLite3", "Database"),
                ("⚡", "Joblib", "Model serialization"),
                ("🐼", "Pandas", "Data processing"),
            ]
            for icon, name, desc in tech:
                st.markdown(f"""
                <div style="background:#111827;border:1px solid #1e293b;border-radius:8px;
                            padding:10px;margin-bottom:6px">
                    <span style="font-size:1.2rem">{icon}</span>
                    <span style="color:white;font-weight:600;margin-left:8px">{name}</span>
                    <br><span style="color:#64748b;font-size:0.8rem;margin-left:28px">{desc}</span>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("👥 User Roles")
            roles = [
                ("🛡️ Admin", "#7c3aed", "Full platform control, analytics, user management"),
                ("🏢 Recruiter", "#1d4ed8", "Post jobs, manage applicants, view predictions"),
                ("🔍 Job Seeker", "#065f46", "Search genuine jobs, apply, track applications"),
            ]
            for role_name, color, desc in roles:
                st.markdown(f"""
                <div style="background:#111827;border-left:3px solid {color};border-radius:8px;
                            padding:10px;margin-bottom:6px">
                    <p style="color:white;margin:0;font-weight:600">{role_name}</p>
                    <p style="color:#94a3b8;margin:2px 0;font-size:0.8rem">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
