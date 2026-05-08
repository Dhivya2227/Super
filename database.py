import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "recruitment.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','recruiter','seeker')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            website TEXT,
            industry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruiter_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            requirements TEXT,
            company TEXT,
            salary TEXT,
            location TEXT,
            employment_type TEXT,
            experience TEXT,
            skills TEXT,
            prediction TEXT DEFAULT 'Pending',
            confidence_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recruiter_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            resume_path TEXT,
            cover_letter TEXT,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS seeker_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skills TEXT,
            experience TEXT,
            education TEXT,
            preferred_location TEXT,
            preferred_role TEXT,
            resume_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            prediction TEXT,
            confidence_result REAL,
            job_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed admin user
    c.execute("SELECT id FROM users WHERE email='admin@recruit.ai'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
            ("Admin", "admin@recruit.ai", hash_password("Admin@123"), "admin")
        )

    # Seed demo recruiter
    c.execute("SELECT id FROM users WHERE email='recruiter@demo.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
            ("TechCorp HR", "recruiter@demo.com", hash_password("Recruiter@123"), "recruiter")
        )
        rid = c.lastrowid
        c.execute(
            "INSERT INTO companies (user_id, company_name, description, location, industry) VALUES (?,?,?,?,?)",
            (rid, "TechCorp Solutions", "Leading technology company", "Bangalore, India", "IT")
        )

    # Seed demo seeker
    c.execute("SELECT id FROM users WHERE email='seeker@demo.com'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
            ("John Doe", "seeker@demo.com", hash_password("Seeker@123"), "seeker")
        )

    conn.commit()
    conn.close()

# ── Users ──────────────────────────────────────────────────────────────────
def create_user(name, email, password, role):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?,?,?,?)",
            (name, email, hash_password(password), role)
        )
        conn.commit()
        return True, "User created successfully"
    except sqlite3.IntegrityError:
        return False, "Email already exists"
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users(role=None):
    conn = get_connection()
    if role:
        rows = conn.execute("SELECT * FROM users WHERE role=?", (role,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# ── Companies ──────────────────────────────────────────────────────────────
def create_company(user_id, company_name, description, location, website, industry):
    conn = get_connection()
    conn.execute(
        "INSERT INTO companies (user_id,company_name,description,location,website,industry) VALUES (?,?,?,?,?,?)",
        (user_id, company_name, description, location, website, industry)
    )
    conn.commit()
    conn.close()

def get_company_by_user(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM companies WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_company(user_id, company_name, description, location, website, industry):
    conn = get_connection()
    conn.execute(
        "UPDATE companies SET company_name=?,description=?,location=?,website=?,industry=? WHERE user_id=?",
        (company_name, description, location, website, industry, user_id)
    )
    conn.commit()
    conn.close()

# ── Jobs ───────────────────────────────────────────────────────────────────
def create_job(recruiter_id, title, description, requirements, company, salary,
               location, employment_type, experience, skills, prediction, confidence_score):
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO jobs (recruiter_id,title,description,requirements,company,salary,
           location,employment_type,experience,skills,prediction,confidence_score)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (recruiter_id, title, description, requirements, company, salary,
         location, employment_type, experience, skills, prediction, confidence_score)
    )
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id

def get_all_jobs(status='active'):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM jobs WHERE status=? ORDER BY timestamp DESC", (status,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_jobs_by_recruiter(recruiter_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM jobs WHERE recruiter_id=? ORDER BY timestamp DESC", (recruiter_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_job_by_id(job_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_job(job_id, title, description, requirements, salary, location,
               employment_type, experience, skills, prediction, confidence_score):
    conn = get_connection()
    conn.execute(
        """UPDATE jobs SET title=?,description=?,requirements=?,salary=?,location=?,
           employment_type=?,experience=?,skills=?,prediction=?,confidence_score=?
           WHERE id=?""",
        (title, description, requirements, salary, location,
         employment_type, experience, skills, prediction, confidence_score, job_id)
    )
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = get_connection()
    conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

def search_jobs(keyword='', location='', prediction='', employment_type=''):
    conn = get_connection()
    query = "SELECT * FROM jobs WHERE status='active'"
    params = []
    if keyword:
        query += " AND (title LIKE ? OR description LIKE ? OR company LIKE ? OR skills LIKE ?)"
        params.extend([f'%{keyword}%'] * 4)
    if location:
        query += " AND location LIKE ?"
        params.append(f'%{location}%')
    if prediction:
        query += " AND prediction=?"
        params.append(prediction)
    if employment_type:
        query += " AND employment_type=?"
        params.append(employment_type)
    query += " ORDER BY timestamp DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Applications ───────────────────────────────────────────────────────────
def apply_for_job(user_id, job_id, resume_path, cover_letter):
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM applications WHERE user_id=? AND job_id=?", (user_id, job_id)
    ).fetchone()
    if existing:
        conn.close()
        return False, "Already applied"
    conn.execute(
        "INSERT INTO applications (user_id,job_id,resume_path,cover_letter) VALUES (?,?,?,?)",
        (user_id, job_id, resume_path, cover_letter)
    )
    conn.commit()
    conn.close()
    return True, "Applied successfully"

def get_applications_by_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.*, j.title, j.company, j.location, j.prediction
           FROM applications a JOIN jobs j ON a.job_id=j.id
           WHERE a.user_id=? ORDER BY a.applied_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_applications_by_job(job_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.*, u.name, u.email
           FROM applications a JOIN users u ON a.user_id=u.id
           WHERE a.job_id=? ORDER BY a.applied_at DESC""",
        (job_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_application_status(app_id, status):
    conn = get_connection()
    conn.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
    conn.commit()
    conn.close()

# ── Saved Jobs ─────────────────────────────────────────────────────────────
def save_job(user_id, job_id):
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM saved_jobs WHERE user_id=? AND job_id=?", (user_id, job_id)
    ).fetchone()
    if existing:
        conn.close()
        return False, "Already saved"
    conn.execute("INSERT INTO saved_jobs (user_id,job_id) VALUES (?,?)", (user_id, job_id))
    conn.commit()
    conn.close()
    return True, "Job saved"

def get_saved_jobs(user_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT j.* FROM saved_jobs s JOIN jobs j ON s.job_id=j.id
           WHERE s.user_id=? ORDER BY s.saved_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Seeker Profile ─────────────────────────────────────────────────────────
def upsert_seeker_profile(user_id, skills, experience, education, preferred_location, preferred_role, resume_path):
    conn = get_connection()
    existing = conn.execute("SELECT id FROM seeker_profiles WHERE user_id=?", (user_id,)).fetchone()
    if existing:
        conn.execute(
            """UPDATE seeker_profiles SET skills=?,experience=?,education=?,
               preferred_location=?,preferred_role=?,resume_path=? WHERE user_id=?""",
            (skills, experience, education, preferred_location, preferred_role, resume_path, user_id)
        )
    else:
        conn.execute(
            """INSERT INTO seeker_profiles (user_id,skills,experience,education,
               preferred_location,preferred_role,resume_path) VALUES (?,?,?,?,?,?,?)""",
            (user_id, skills, experience, education, preferred_location, preferred_role, resume_path)
        )
    conn.commit()
    conn.close()

def get_seeker_profile(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM seeker_profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# ── Logs ───────────────────────────────────────────────────────────────────
def log_prediction(user_id, action, prediction, confidence_result, job_id=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO logs (user_id,action,prediction,confidence_result,job_id) VALUES (?,?,?,?,?)",
        (user_id, action, prediction, confidence_result, job_id)
    )
    conn.commit()
    conn.close()

def get_logs(limit=100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT l.*, u.name, u.email FROM logs l LEFT JOIN users u ON l.user_id=u.id ORDER BY l.timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Analytics ──────────────────────────────────────────────────────────────
def get_stats():
    conn = get_connection()
    stats = {}
    stats['total_jobs'] = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    stats['fake_jobs'] = conn.execute("SELECT COUNT(*) FROM jobs WHERE prediction='Fake'").fetchone()[0]
    stats['genuine_jobs'] = conn.execute("SELECT COUNT(*) FROM jobs WHERE prediction='Genuine'").fetchone()[0]
    stats['irrelevant_jobs'] = conn.execute("SELECT COUNT(*) FROM jobs WHERE prediction='Irrelevant'").fetchone()[0]
    stats['total_recruiters'] = conn.execute("SELECT COUNT(*) FROM users WHERE role='recruiter'").fetchone()[0]
    stats['total_seekers'] = conn.execute("SELECT COUNT(*) FROM users WHERE role='seeker'").fetchone()[0]
    stats['total_applications'] = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    conn.close()
    return stats

def get_jobs_over_time():
    conn = get_connection()
    rows = conn.execute(
        "SELECT DATE(timestamp) as date, prediction, COUNT(*) as count FROM jobs GROUP BY DATE(timestamp), prediction ORDER BY date"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_prediction_distribution():
    conn = get_connection()
    rows = conn.execute(
        "SELECT prediction, COUNT(*) as count FROM jobs GROUP BY prediction"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
