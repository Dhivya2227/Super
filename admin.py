import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import (get_stats, get_all_users, get_all_jobs, delete_user, delete_job,
                      get_logs, get_prediction_distribution, get_jobs_over_time)
from utils.helpers import metric_card, prediction_badge, paginate, format_timestamp

def render_admin():
    user = st.session_state.get('user', {})
    if user.get('role') != 'admin':
        st.error("Access denied."); return

    st.markdown("""
    <div style="background:linear-gradient(135deg,#7c3aed,#4f46e5);padding:24px;border-radius:12px;margin-bottom:24px">
        <h1 style="color:white;margin:0;font-size:1.8rem">🛡️ Admin Control Center</h1>
        <p style="color:#c4b5fd;margin:4px 0">Platform analytics, user management & ML monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Dashboard", "👥 Users", "💼 Jobs", "🤖 ML Logs", "📈 Analytics"]
    )

    # ── Dashboard ───────────────────────────────────────────────────────────
    with tab1:
        stats = get_stats()
        cols = st.columns(4)
        metrics = [
            ("Total Jobs", stats['total_jobs'], '💼', '#6366f1'),
            ("Genuine Jobs", stats['genuine_jobs'], '✅', '#10b981'),
            ("Fake Jobs", stats['fake_jobs'], '🚨', '#ef4444'),
            ("Irrelevant", stats['irrelevant_jobs'], '⚠️', '#f59e0b'),
        ]
        for col, (title, val, icon, color) in zip(cols, metrics):
            with col:
                metric_card(title, val, icon=icon, color=color)

        st.markdown("<br>", unsafe_allow_html=True)
        cols2 = st.columns(3)
        metrics2 = [
            ("Recruiters", stats['total_recruiters'], '🏢', '#8b5cf6'),
            ("Job Seekers", stats['total_seekers'], '👤', '#06b6d4'),
            ("Applications", stats['total_applications'], '📋', '#f97316'),
        ]
        for col, (title, val, icon, color) in zip(cols2, metrics2):
            with col:
                metric_card(title, val, icon=icon, color=color)

        st.markdown("---")

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            pred_data = get_prediction_distribution()
            if pred_data:
                df_pred = pd.DataFrame(pred_data)
                fig = px.pie(
                    df_pred, names='prediction', values='count',
                    title='Job Prediction Distribution',
                    color='prediction',
                    color_discrete_map={'Genuine':'#10b981','Fake':'#ef4444','Irrelevant':'#f59e0b','Pending':'#6b7280'},
                    hole=0.4
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white', title_font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            time_data = get_jobs_over_time()
            if time_data:
                df_time = pd.DataFrame(time_data)
                fig2 = px.bar(
                    df_time, x='date', y='count', color='prediction',
                    title='Jobs Posted Over Time',
                    color_discrete_map={'Genuine':'#10b981','Fake':'#ef4444','Irrelevant':'#f59e0b'},
                    barmode='stack'
                )
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white', title_font_color='white',
                    xaxis=dict(gridcolor='#334155'), yaxis=dict(gridcolor='#334155')
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Fake vs Genuine gauge
        if stats['total_jobs'] > 0:
            fake_pct = (stats['fake_jobs'] / stats['total_jobs']) * 100
            fig3 = go.Figure(go.Indicator(
                mode='gauge+number+delta',
                value=fake_pct,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': 'Fake Job Rate (%)', 'font': {'color': 'white'}},
                delta={'reference': 20, 'increasing': {'color': '#ef4444'}, 'decreasing': {'color': '#10b981'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': 'white'},
                    'bar': {'color': '#ef4444'},
                    'bgcolor': '#1e293b',
                    'bordercolor': '#334155',
                    'steps': [
                        {'range': [0, 20], 'color': '#064e3b'},
                        {'range': [20, 50], 'color': '#78350f'},
                        {'range': [50, 100], 'color': '#7f1d1d'},
                    ],
                    'threshold': {'line': {'color': 'white', 'width': 3}, 'thickness': 0.75, 'value': 20}
                }
            ))
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', font_color='white', height=300
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── Users ───────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("👥 User Management")
        role_filter = st.selectbox("Filter by Role", ['All', 'admin', 'recruiter', 'seeker'])
        users = get_all_users(None if role_filter == 'All' else role_filter)

        if users:
            df_users = pd.DataFrame(users)[['id','name','email','role','created_at']]
            df_users.columns = ['ID','Name','Email','Role','Joined']
            
            search = st.text_input("🔍 Search users", placeholder="Name or email...")
            if search:
                mask = df_users['Name'].str.contains(search, case=False, na=False) | \
                       df_users['Email'].str.contains(search, case=False, na=False)
                df_users = df_users[mask]

            st.dataframe(df_users, use_container_width=True, hide_index=True)

            # Delete user
            with st.expander("🗑️ Delete User"):
                del_id = st.number_input("User ID to delete", min_value=1, step=1)
                if st.button("Delete User", type="primary"):
                    if del_id == user['id']:
                        st.error("Cannot delete your own account.")
                    else:
                        delete_user(del_id)
                        st.success(f"User {del_id} deleted.")
                        st.rerun()

            # Download
            csv = df_users.to_csv(index=False).encode()
            st.download_button("📥 Download Users CSV", csv, "users.csv", "text/csv")
        else:
            st.info("No users found.")

    # ── Jobs ────────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("💼 Job Management")
        jobs = get_all_jobs()
        
        col1, col2 = st.columns(2)
        with col1:
            kw = st.text_input("🔍 Search jobs", placeholder="Title, company...")
        with col2:
            pred_f = st.selectbox("Filter Prediction", ['All', 'Genuine', 'Fake', 'Irrelevant', 'Pending'])

        if jobs:
            df_jobs = pd.DataFrame(jobs)
            if kw:
                mask = (df_jobs['title'].str.contains(kw, case=False, na=False) |
                        df_jobs['company'].str.contains(kw, case=False, na=False))
                df_jobs = df_jobs[mask]
            if pred_f != 'All':
                df_jobs = df_jobs[df_jobs['prediction'] == pred_f]

            # Highlight fake jobs
            display_cols = ['id','title','company','location','prediction','confidence_score','timestamp']
            available = [c for c in display_cols if c in df_jobs.columns]
            
            def highlight_fake(row):
                if row.get('prediction') == 'Fake':
                    return ['background-color: #450a0a'] * len(row)
                elif row.get('prediction') == 'Irrelevant':
                    return ['background-color: #451a03'] * len(row)
                return [''] * len(row)

            st.dataframe(df_jobs[available], use_container_width=True, hide_index=True)

            with st.expander("🗑️ Delete Job"):
                del_job_id = st.number_input("Job ID to delete", min_value=1, step=1)
                if st.button("Delete Job", type="primary"):
                    delete_job(del_job_id)
                    st.success(f"Job {del_job_id} deleted.")
                    st.rerun()

            csv = df_jobs.to_csv(index=False).encode()
            st.download_button("📥 Download Jobs CSV", csv, "jobs.csv", "text/csv")
        else:
            st.info("No jobs found.")

    # ── ML Logs ─────────────────────────────────────────────────────────────
    with tab4:
        st.subheader("🤖 ML Prediction Logs")
        logs = get_logs(200)
        if logs:
            df_logs = pd.DataFrame(logs)
            display = ['id','name','email','action','prediction','confidence_result','timestamp']
            available = [c for c in display if c in df_logs.columns]
            st.dataframe(df_logs[available], use_container_width=True, hide_index=True)

            csv = df_logs.to_csv(index=False).encode()
            st.download_button("📥 Download Logs CSV", csv, "logs.csv", "text/csv")
        else:
            st.info("No prediction logs found.")

    # ── Analytics ────────────────────────────────────────────────────────────
    with tab5:
        st.subheader("📈 Advanced Analytics")
        jobs = get_all_jobs()
        if not jobs:
            st.info("No data available for analytics.")
            return
        
        df = pd.DataFrame(jobs)

        # Employment type distribution
        if 'employment_type' in df.columns:
            emp_counts = df['employment_type'].value_counts().reset_index()
            emp_counts.columns = ['Type','Count']
            fig = px.bar(emp_counts, x='Type', y='Count', title='Jobs by Employment Type',
                        color='Count', color_continuous_scale='Viridis')
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                             font_color='white', title_font_color='white')
            st.plotly_chart(fig, use_container_width=True)

        # Top locations
        if 'location' in df.columns:
            loc_counts = df['location'].value_counts().head(10).reset_index()
            loc_counts.columns = ['Location','Count']
            fig2 = px.bar(loc_counts, x='Count', y='Location', orientation='h',
                         title='Top 10 Job Locations', color='Count',
                         color_continuous_scale='Blues')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font_color='white', title_font_color='white')
            st.plotly_chart(fig2, use_container_width=True)

        # Confidence score distribution
        if 'confidence_score' in df.columns:
            fig3 = px.histogram(df, x='confidence_score', color='prediction',
                               title='Confidence Score Distribution',
                               nbins=20,
                               color_discrete_map={'Genuine':'#10b981','Fake':'#ef4444','Irrelevant':'#f59e0b'})
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font_color='white', title_font_color='white')
            st.plotly_chart(fig3, use_container_width=True)
