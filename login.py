import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import authenticate_user, create_user

def render_login():
    st.markdown("""
    <style>
    .auth-header {text-align:center;margin-bottom:2rem}
    .auth-header h1 {font-size:2rem;color:white;margin:0}
    .auth-header p {color:#94a3b8;margin:4px 0}
    .demo-box {background:#1e293b;border:1px solid #334155;border-radius:8px;padding:12px;margin-top:12px}
    .demo-box h4 {color:#7c3aed;margin:0 0 8px 0;font-size:0.85rem}
    .demo-box p {color:#94a3b8;margin:2px 0;font-size:0.8rem;font-family:monospace}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-header">
        <h1>🔐 Sign In</h1>
        <p>Access your recruitment intelligence platform</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("📧 Email Address", placeholder="you@example.com")
        password = st.text_input("🔑 Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                user = authenticate_user(email.strip(), password)
                if user:
                    st.session_state.user = user
                    st.session_state.logged_in = True
                    st.success(f"Welcome back, {user['name']}! 🎉")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")

    st.markdown("""
    <div class="demo-box">
        <h4>🧪 Demo Credentials</h4>
        <p>Admin: admin@recruit.ai / Admin@123</p>
        <p>Recruiter: recruiter@demo.com / Recruiter@123</p>
        <p>Job Seeker: seeker@demo.com / Seeker@123</p>
    </div>
    """, unsafe_allow_html=True)


def render_register():
    st.markdown("""
    <div style="text-align:center;margin-bottom:2rem">
        <h1 style="font-size:2rem;color:white;margin:0">📝 Create Account</h1>
        <p style="color:#94a3b8">Join the smart recruitment platform</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name", placeholder="John Doe")
        with col2:
            role = st.selectbox("🎭 Account Type", ["seeker", "recruiter"], 
                               format_func=lambda x: "Job Seeker" if x == "seeker" else "Recruiter/Company")
        
        email = st.text_input("📧 Email Address", placeholder="you@example.com")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("🔑 Password", type="password", placeholder="Min 6 characters")
        with col4:
            confirm = st.text_input("🔑 Confirm Password", type="password", placeholder="Repeat password")

        submitted = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

        if submitted:
            if not all([name, email, password, confirm]):
                st.error("Please fill in all fields.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif '@' not in email:
                st.error("Please enter a valid email address.")
            else:
                success, msg = create_user(name.strip(), email.strip(), password, role)
                if success:
                    st.success(f"Account created! Please sign in.")
                    st.session_state.auth_tab = 'login'
                    st.rerun()
                else:
                    st.error(msg)
