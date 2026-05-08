import streamlit as st
import pandas as pd
import plotly.express as px
import time, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import (get_company_by_user, create_company, update_company,
                      create_job, get_jobs_by_recruiter, update_job, delete_job,
                      get_job_by_id, get_applications_by_job, update_application_status,
                      log_prediction)
from predict import predict_job, get_risk_explanation, get_red_flags
from utils.helpers import metric_card, prediction_badge, risk_badge, format_timestamp

EMPLOYMENT_TYPES = ['Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance', 'Remote']
EXPERIENCE_LEVELS = ['Entry Level', '1-2 years', '2-5 years', '5-10 years', '10+ years']

def render_recruiter():
    user = st.session_state.get('user', {})
    if user.get('role') not in ('recruiter', 'admin'):
        st.error("Access denied."); return

    company = get_company_by_user(user['id'])

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1d4ed8,#0ea5e9);padding:24px;border-radius:12px;margin-bottom:24px">
        <h1 style="color:white;margin:0;font-size:1.8rem">🏢 Recruiter Dashboard</h1>
        <p style="color:#bae6fd;margin:4px 0">
            {company['company_name'] if company else 'Complete your company profile to start posting'}
        </p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🏢 Company Profile", "➕ Post Job", "💼 My Jobs", "📋 Applications", "📊 Analytics"])

    # ── Company Profile ──────────────────────────────────────────────────────
    with tabs[0]:
        st.subheader("🏢 Company Profile")
        with st.form("company_form"):
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company Name *", value=company['company_name'] if company else '')
                location = st.text_input("Location *", value=company['location'] if company else '')
            with col2:
                industry = st.text_input("Industry", value=company['industry'] if company else '')
                website = st.text_input("Website", value=company['website'] if company else '')
            description = st.text_area("Company Description", value=company['description'] if company else '', height=120)
            
            if st.form_submit_button("💾 Save Profile", type="primary"):
                if not company_name or not location:
                    st.error("Company name and location are required.")
                elif company:
                    update_company(user['id'], company_name, description, location, website, industry)
                    st.success("✅ Profile updated!")
                    st.rerun()
                else:
                    create_company(user['id'], company_name, description, location, website, industry)
                    st.success("✅ Company profile created!")
                    st.rerun()

    # ── Post Job ─────────────────────────────────────────────────────────────
    with tabs[1]:
        if not company:
            st.warning("⚠️ Please complete your company profile first before posting jobs.")
            return

        st.subheader("➕ Post a New Job")
        st.markdown("*The system will automatically analyze your job posting for authenticity using our AI model.*")

        with st.form("post_job_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Job Title *", placeholder="e.g., Senior Python Developer")
                salary = st.text_input("Salary Range", placeholder="e.g., ₹8-15 LPA")
                employment_type = st.selectbox("Employment Type", EMPLOYMENT_TYPES)
            with col2:
                location_job = st.text_input("Location *", placeholder="e.g., Bangalore, India")
                experience = st.selectbox("Experience Required", EXPERIENCE_LEVELS)
                skills = st.text_input("Key Skills", placeholder="Python, Django, REST API, AWS")

            description_job = st.text_area("Job Description *", height=150,
                placeholder="Describe the role, responsibilities, and what the candidate will be doing...")
            requirements = st.text_area("Requirements", height=100,
                placeholder="List the qualifications, certifications, and technical requirements...")

            submitted = st.form_submit_button("🚀 Post & Analyze Job", type="primary", use_container_width=True)

        if submitted:
            if not title or not description_job or not location_job:
                st.error("Job title, description, and location are required.")
            else:
                with st.spinner("🤖 AI is analyzing your job posting..."):
                    progress = st.progress(0)
                    for i in range(1, 101):
                        time.sleep(0.015)
                        progress.progress(i)
                    
                    result = predict_job(title, description_job, requirements, skills)
                    
                    job_id = create_job(
                        user['id'], title, description_job, requirements,
                        company['company_name'], salary, location_job,
                        employment_type, experience, skills,
                        result['prediction'], result['confidence']
                    )
                    
                    log_prediction(user['id'], 'post_job', result['prediction'],
                                  result['confidence'], job_id)

                pred = result['prediction']
                conf = result['confidence']
                colors = {'Genuine': '#10b981', 'Fake': '#ef4444', 'Irrelevant': '#f59e0b'}
                icons = {'Genuine': '✅', 'Fake': '🚨', 'Irrelevant': '⚠️'}
                color = colors.get(pred, '#6b7280')
                icon = icons.get(pred, '📊')

                st.markdown(f"""
                <div style="background:#1e293b;border:2px solid {color};border-radius:12px;padding:24px;margin-top:16px">
                    <div style="display:flex;align-items:center;gap:12px">
                        <span style="font-size:2.5rem">{icon}</span>
                        <div>
                            <h2 style="color:white;margin:0">AI Prediction: {pred}</h2>
                            <p style="color:#94a3b8;margin:4px 0">
                                Confidence: {conf*100:.1f}% | Risk Level: {result['risk_level']}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                explanations = get_risk_explanation(pred, conf)
                for exp in explanations:
                    st.markdown(f"<p style='color:#94a3b8;margin:4px 0'>{exp}</p>", unsafe_allow_html=True)

                red_flags = get_red_flags(title, description_job, requirements)
                if red_flags:
                    st.markdown("**🚩 Detected Red Flags:**")
                    for flag in red_flags:
                        st.markdown(f"<span style='background:#450a0a;color:#fca5a5;padding:2px 8px;border-radius:4px;margin:2px;display:inline-block'>{flag}</span>", unsafe_allow_html=True)

                if 'details' in result and result['details']:
                    st.markdown("**📊 Class Probabilities:**")
                    cols = st.columns(len(result['details']))
                    for col, (cls, prob) in zip(cols, result['details'].items()):
                        with col:
                            st.metric(cls, f"{prob*100:.1f}%")

    # ── My Jobs ──────────────────────────────────────────────────────────────
    with tabs[2]:
        st.subheader("💼 My Job Postings")
        jobs = get_jobs_by_recruiter(user['id'])

        if not jobs:
            st.info("No jobs posted yet. Go to 'Post Job' to create your first job listing.")
            return

        col1, col2 = st.columns(2)
        with col1:
            kw = st.text_input("🔍 Search my jobs", placeholder="Title, location...")
        with col2:
            pred_f = st.selectbox("Filter", ['All', 'Genuine', 'Fake', 'Irrelevant', 'Pending'])

        filtered_jobs = jobs
        if kw:
            filtered_jobs = [j for j in filtered_jobs if kw.lower() in j['title'].lower()
                            or kw.lower() in (j.get('location') or '').lower()]
        if pred_f != 'All':
            filtered_jobs = [j for j in filtered_jobs if j['prediction'] == pred_f]

        # Stats
        total = len(jobs)
        genuine = sum(1 for j in jobs if j['prediction'] == 'Genuine')
        fake = sum(1 for j in jobs if j['prediction'] == 'Fake')
        cols = st.columns(3)
        with cols[0]: metric_card("Total Posted", total, icon='💼', color='#6366f1')
        with cols[1]: metric_card("Genuine", genuine, icon='✅', color='#10b981')
        with cols[2]: metric_card("Flagged", fake, icon='🚨', color='#ef4444')

        st.markdown("---")

        for job in filtered_jobs:
            pred = job.get('prediction', 'Pending')
            colors = {'Genuine': '#10b981', 'Fake': '#ef4444', 'Irrelevant': '#f59e0b', 'Pending': '#6b7280'}
            color = colors.get(pred, '#6b7280')
            
            with st.container():
                st.markdown(f"""
                <div style="background:#1e293b;border:1px solid #334155;border-radius:10px;
                            padding:16px;margin-bottom:12px;border-left:4px solid {color}">
                    <div style="display:flex;justify-content:space-between">
                        <div>
                            <h4 style="color:white;margin:0">{job['title']}</h4>
                            <p style="color:#94a3b8;margin:4px 0;font-size:0.85rem">
                                📍 {job.get('location','N/A')} | 💰 {job.get('salary','N/A')} | 
                                🕒 {format_timestamp(job.get('timestamp',''))}
                            </p>
                        </div>
                        <div style="text-align:right">
                            <p style="color:white;margin:0;font-size:0.8rem">Prediction: <b>{pred}</b></p>
                            <p style="color:#94a3b8;margin:0;font-size:0.8rem">Confidence: {float(job.get('confidence_score',0))*100:.1f}%</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_e, col_d = st.columns([1, 1])
                with col_e:
                    if st.button(f"✏️ Edit", key=f"edit_{job['id']}"):
                        st.session_state[f'edit_job_{job["id"]}'] = True
                with col_d:
                    if st.button(f"🗑️ Delete", key=f"del_{job['id']}", type="secondary"):
                        delete_job(job['id'])
                        st.success("Job deleted.")
                        st.rerun()

                if st.session_state.get(f'edit_job_{job["id"]}'):
                    with st.form(f"edit_form_{job['id']}"):
                        st.markdown("**✏️ Edit Job**")
                        c1, c2 = st.columns(2)
                        with c1:
                            new_title = st.text_input("Title", value=job['title'])
                            new_salary = st.text_input("Salary", value=job.get('salary',''))
                            new_emp = st.selectbox("Employment Type", EMPLOYMENT_TYPES,
                                                  index=EMPLOYMENT_TYPES.index(job.get('employment_type','Full-time'))
                                                  if job.get('employment_type') in EMPLOYMENT_TYPES else 0)
                        with c2:
                            new_loc = st.text_input("Location", value=job.get('location',''))
                            new_exp = st.selectbox("Experience", EXPERIENCE_LEVELS,
                                                  index=EXPERIENCE_LEVELS.index(job.get('experience','Entry Level'))
                                                  if job.get('experience') in EXPERIENCE_LEVELS else 0)
                            new_skills = st.text_input("Skills", value=job.get('skills',''))
                        new_desc = st.text_area("Description", value=job.get('description',''), height=100)
                        new_req = st.text_area("Requirements", value=job.get('requirements',''), height=80)
                        
                        if st.form_submit_button("💾 Save Changes", type="primary"):
                            res = predict_job(new_title, new_desc, new_req, new_skills)
                            update_job(job['id'], new_title, new_desc, new_req, new_salary,
                                      new_loc, new_emp, new_exp, new_skills,
                                      res['prediction'], res['confidence'])
                            log_prediction(user['id'], 'edit_job', res['prediction'], res['confidence'], job['id'])
                            st.session_state.pop(f'edit_job_{job["id"]}', None)
                            st.success("✅ Job updated and re-analyzed!")
                            st.rerun()

    # ── Applications ─────────────────────────────────────────────────────────
    with tabs[3]:
        st.subheader("📋 Job Applications")
        jobs = get_jobs_by_recruiter(user['id'])
        if not jobs:
            st.info("No jobs posted yet.")
            return
        
        job_options = {j['id']: f"{j['title']} (ID: {j['id']})" for j in jobs}
        selected_job_id = st.selectbox("Select Job", list(job_options.keys()),
                                       format_func=lambda x: job_options[x])
        
        if selected_job_id:
            apps = get_applications_by_job(selected_job_id)
            if apps:
                st.markdown(f"**{len(apps)} application(s) received**")
                for app in apps:
                    with st.expander(f"👤 {app['name']} — {app['email']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Applied:** {format_timestamp(app['applied_at'])}")
                            st.write(f"**Status:** {app['status'].title()}")
                            if app.get('cover_letter'):
                                st.write("**Cover Letter:**")
                                st.text(app['cover_letter'][:500])
                        with col2:
                            new_status = st.selectbox(
                                "Update Status",
                                ['pending', 'reviewed', 'shortlisted', 'rejected', 'hired'],
                                index=['pending','reviewed','shortlisted','rejected','hired'].index(app['status']),
                                key=f"status_{app['id']}"
                            )
                            if st.button("Update", key=f"upd_{app['id']}"):
                                update_application_status(app['id'], new_status)
                                st.success("Status updated!")
                                st.rerun()
            else:
                st.info("No applications for this job yet.")

    # ── Analytics ────────────────────────────────────────────────────────────
    with tabs[4]:
        st.subheader("📊 My Job Analytics")
        jobs = get_jobs_by_recruiter(user['id'])
        if not jobs:
            st.info("No data available.")
            return
        
        df = pd.DataFrame(jobs)
        
        col1, col2 = st.columns(2)
        with col1:
            pred_counts = df['prediction'].value_counts().reset_index()
            pred_counts.columns = ['Prediction', 'Count']
            fig = px.pie(pred_counts, names='Prediction', values='Count',
                        title='My Jobs - Prediction Breakdown',
                        color='Prediction',
                        color_discrete_map={'Genuine':'#10b981','Fake':'#ef4444','Irrelevant':'#f59e0b','Pending':'#6b7280'},
                        hole=0.4)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if 'confidence_score' in df.columns:
                df['confidence_pct'] = df['confidence_score'] * 100
                fig2 = px.scatter(df, x='timestamp', y='confidence_pct', color='prediction',
                                 title='Confidence Scores Over Time',
                                 color_discrete_map={'Genuine':'#10b981','Fake':'#ef4444','Irrelevant':'#f59e0b'})
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig2, use_container_width=True)
