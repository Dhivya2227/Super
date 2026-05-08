import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import (search_jobs, get_all_jobs, apply_for_job, save_job,
                      get_applications_by_user, get_saved_jobs,
                      upsert_seeker_profile, get_seeker_profile)
from utils.helpers import (prediction_badge, format_timestamp, metric_card,
                            save_uploaded_file, paginate)

SKILLS_LIST = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'Machine Learning',
               'Data Analysis', 'AWS', 'Docker', 'Kubernetes', 'DevOps', 'UI/UX Design',
               'Project Management', 'Marketing', 'Sales', 'Finance', 'HR', 'Content Writing']

def recommend_jobs(jobs, profile):
    """Simple keyword-based recommendation engine."""
    if not profile or not profile.get('skills'):
        return [j for j in jobs if j.get('prediction') == 'Genuine']
    
    user_skills = set(s.strip().lower() for s in profile['skills'].split(','))
    user_role = (profile.get('preferred_role') or '').lower()
    user_location = (profile.get('preferred_location') or '').lower()
    
    scored = []
    for job in jobs:
        if job.get('prediction') != 'Genuine':
            continue
        score = 0
        job_text = f"{job.get('title','')} {job.get('description','')} {job.get('skills','')}".lower()
        
        for skill in user_skills:
            if skill and skill in job_text:
                score += 2
        if user_role and user_role in job_text:
            score += 3
        if user_location and user_location in (job.get('location') or '').lower():
            score += 2
        scored.append((score, job))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [j for _, j in scored]

def render_seeker():
    user = st.session_state.get('user', {})
    if user.get('role') not in ('seeker', 'admin'):
        st.error("Access denied."); return

    profile = get_seeker_profile(user['id'])

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#065f46,#0f766e);padding:24px;border-radius:12px;margin-bottom:24px">
        <h1 style="color:white;margin:0;font-size:1.8rem">🔍 Job Seeker Portal</h1>
        <p style="color:#a7f3d0;margin:4px 0">Find verified, genuine opportunities curated by AI</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🔍 Search Jobs", "⭐ Recommended", "📋 My Applications", "💾 Saved Jobs", "👤 My Profile"])

    # ── Search Jobs ──────────────────────────────────────────────────────────
    with tabs[0]:
        st.subheader("🔍 Intelligent Job Search")
        
        with st.expander("🎛️ Advanced Filters", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                keyword = st.text_input("🔑 Keyword", placeholder="Role, skill, company...")
            with col2:
                location = st.text_input("📍 Location", placeholder="City, state...")
            with col3:
                pred_filter = st.selectbox("🤖 Verification Status",
                    ['', 'Genuine', 'Fake', 'Irrelevant'],
                    format_func=lambda x: 'All' if x == '' else x)
            
            col4, col5 = st.columns(2)
            with col4:
                emp_filter = st.selectbox("💼 Employment Type",
                    ['', 'Full-time', 'Part-time', 'Contract', 'Internship', 'Freelance', 'Remote'],
                    format_func=lambda x: 'Any' if x == '' else x)
            with col5:
                safe_only = st.checkbox("✅ Genuine jobs only", value=True)

        jobs = search_jobs(
            keyword=keyword,
            location=location,
            prediction='Genuine' if safe_only else pred_filter,
            employment_type=emp_filter
        )

        st.markdown(f"**{len(jobs)} job(s) found**")

        if not jobs:
            st.info("No jobs match your search. Try adjusting your filters.")
        else:
            for job in jobs[:20]:
                _render_job_card(job, user['id'])

    # ── Recommended Jobs ──────────────────────────────────────────────────────
    with tabs[1]:
        st.subheader("⭐ AI-Powered Recommendations")
        
        if not profile:
            st.warning("Complete your profile to get personalized job recommendations!")
        else:
            all_jobs = get_all_jobs()
            recommendations = recommend_jobs(all_jobs, profile)

            if not recommendations:
                st.info("No recommendations available. Update your profile with more skills.")
            else:
                st.markdown(f"**{len(recommendations)} recommended job(s) based on your profile**")
                for job in recommendations[:15]:
                    _render_job_card(job, user['id'])

    # ── Applications ──────────────────────────────────────────────────────────
    with tabs[2]:
        st.subheader("📋 My Applications")
        apps = get_applications_by_user(user['id'])

        if not apps:
            st.info("You haven't applied to any jobs yet.")
        else:
            status_counts = {}
            for app in apps:
                s = app.get('status', 'pending')
                status_counts[s] = status_counts.get(s, 0) + 1

            cols = st.columns(min(len(status_counts), 5))
            status_colors = {'pending': '#6b7280', 'reviewed': '#3b82f6', 'shortlisted': '#8b5cf6',
                            'hired': '#10b981', 'rejected': '#ef4444'}
            for col, (status, count) in zip(cols, status_counts.items()):
                with col:
                    metric_card(status.title(), count, icon='📊', color=status_colors.get(status, '#6b7280'))

            st.markdown("---")

            for app in apps:
                status = app.get('status', 'pending')
                color = status_colors.get(status, '#6b7280')
                st.markdown(f"""
                <div style="background:#1e293b;border:1px solid #334155;border-radius:10px;
                            padding:16px;margin-bottom:12px;border-left:4px solid {color}">
                    <div style="display:flex;justify-content:space-between">
                        <div>
                            <h4 style="color:white;margin:0">{app.get('title','N/A')}</h4>
                            <p style="color:#94a3b8;margin:4px 0;font-size:0.85rem">
                                🏢 {app.get('company','N/A')} | 📍 {app.get('location','N/A')}
                            </p>
                            <p style="color:#64748b;margin:0;font-size:0.8rem">
                                Applied: {format_timestamp(app.get('applied_at',''))}
                            </p>
                        </div>
                        <div style="text-align:right">
                            <span style="background:{color};color:white;padding:4px 12px;
                                        border-radius:20px;font-size:0.8rem;font-weight:600">
                                {status.upper()}
                            </span>
                            <br>
                            {prediction_badge(app.get('prediction','Pending'))}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Saved Jobs ────────────────────────────────────────────────────────────
    with tabs[3]:
        st.subheader("💾 Saved Jobs")
        saved = get_saved_jobs(user['id'])
        if not saved:
            st.info("No saved jobs. Click '💾 Save' on any job to bookmark it.")
        else:
            for job in saved:
                _render_job_card(job, user['id'], show_save=False)

    # ── Profile ───────────────────────────────────────────────────────────────
    with tabs[4]:
        st.subheader("👤 My Profile")
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                skills = st.text_area("💡 Skills (comma-separated)",
                    value=profile['skills'] if profile else '',
                    placeholder="Python, SQL, Machine Learning, Excel...",
                    height=100)
                preferred_role = st.text_input("🎯 Preferred Role",
                    value=profile['preferred_role'] if profile else '',
                    placeholder="Data Scientist, Software Engineer...")
            with col2:
                experience = st.text_input("📅 Years of Experience",
                    value=profile['experience'] if profile else '',
                    placeholder="e.g., 3 years")
                preferred_location = st.text_input("📍 Preferred Location",
                    value=profile['preferred_location'] if profile else '',
                    placeholder="Bangalore, Mumbai, Remote...")
            
            education = st.text_input("🎓 Education",
                value=profile['education'] if profile else '',
                placeholder="B.Tech Computer Science, IIT Delhi")
            
            resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=['pdf', 'doc', 'docx'])
            
            if st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True):
                resume_path = profile['resume_path'] if profile else ''
                if resume_file:
                    resume_path = save_uploaded_file(resume_file, 'resumes')
                
                upsert_seeker_profile(
                    user['id'], skills, experience, education,
                    preferred_location, preferred_role, resume_path
                )
                st.success("✅ Profile saved successfully!")
                st.rerun()

        if profile and profile.get('resume_path') and os.path.exists(profile['resume_path']):
            st.markdown(f"📄 Current resume: `{os.path.basename(profile['resume_path'])}`")


def _render_job_card(job, user_id, show_save=True):
    """Render a job card with apply and save buttons."""
    pred = job.get('prediction', 'Pending')
    colors = {'Genuine': '#10b981', 'Fake': '#ef4444', 'Irrelevant': '#f59e0b', 'Pending': '#6b7280'}
    color = colors.get(pred, '#6b7280')

    st.markdown(f"""
    <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;
                padding:20px;margin-bottom:12px;border-left:4px solid {color}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div style="flex:1">
                <h3 style="color:white;margin:0 0 4px 0">{job.get('title','N/A')}</h3>
                <p style="color:#94a3b8;margin:0 0 8px 0;font-size:0.9rem">
                    🏢 {job.get('company','N/A')} | 📍 {job.get('location','N/A')} | 
                    💰 {job.get('salary','Not disclosed')} | 💼 {job.get('employment_type','N/A')}
                </p>
                <p style="color:#cbd5e1;margin:0;font-size:0.85rem">
                    {str(job.get('description',''))[:200]}{'...' if len(str(job.get('description',''))) > 200 else ''}
                </p>
                <p style="color:#64748b;margin:8px 0 0 0;font-size:0.8rem">
                    🏷️ {job.get('skills','N/A')} | 📅 {job.get('experience','N/A')}
                </p>
            </div>
            <div style="margin-left:16px;text-align:right">
                <span style="background:{color};color:white;padding:4px 12px;
                            border-radius:20px;font-size:0.8rem;font-weight:600">{pred}</span>
                <p style="color:#64748b;margin:4px 0;font-size:0.75rem">
                    {float(job.get('confidence_score',0))*100:.0f}% confidence
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button(f"📝 Apply Now", key=f"apply_{job['id']}_{user_id}", type="primary"):
            st.session_state[f'apply_modal_{job["id"]}'] = True
    with col2:
        if show_save and st.button(f"💾 Save", key=f"save_{job['id']}_{user_id}"):
            ok, msg = save_job(user_id, job['id'])
            if ok:
                st.success(msg)
            else:
                st.info(msg)
    with col3:
        if st.button(f"👁️ View", key=f"view_{job['id']}_{user_id}"):
            st.session_state[f'view_job_{job["id"]}'] = not st.session_state.get(f'view_job_{job["id"]}', False)

    if st.session_state.get(f'view_job_{job["id"]}'):
        with st.expander("📋 Full Job Details", expanded=True):
            st.markdown(f"**Description:** {job.get('description','N/A')}")
            st.markdown(f"**Requirements:** {job.get('requirements','N/A')}")
            st.markdown(f"**Skills Required:** {job.get('skills','N/A')}")
            st.markdown(f"**Experience:** {job.get('experience','N/A')}")
            st.markdown(f"**Posted:** {format_timestamp(job.get('timestamp',''))}")

    if st.session_state.get(f'apply_modal_{job["id"]}'):
        with st.expander("📝 Submit Application", expanded=True):
            with st.form(f"apply_form_{job['id']}"):
                cover_letter = st.text_area("Cover Letter (optional)",
                    placeholder="Tell the recruiter why you're a great fit...", height=120)
                resume_file = st.file_uploader("Upload Resume", type=['pdf', 'doc', 'docx'],
                                               key=f"resume_{job['id']}")
                
                col_sub, col_can = st.columns(2)
                with col_sub:
                    if st.form_submit_button("🚀 Submit Application", type="primary"):
                        resume_path = ''
                        if resume_file:
                            resume_path = save_uploaded_file(resume_file, 'resumes')
                        ok, msg = apply_for_job(user_id, job['id'], resume_path, cover_letter)
                        if ok:
                            st.success("🎉 Application submitted successfully!")
                            st.session_state.pop(f'apply_modal_{job["id"]}', None)
                            st.rerun()
                        else:
                            st.warning(msg)
                with col_can:
                    if st.form_submit_button("Cancel"):
                        st.session_state.pop(f'apply_modal_{job["id"]}', None)
                        st.rerun()
