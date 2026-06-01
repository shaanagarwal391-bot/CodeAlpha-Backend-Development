import os
import sqlite3
from flask import Flask, request, jsonify, abort

app = Flask(__name__)
DB_NAME = "job_board.db"

def get_db_connection():
    """Establishes a connection and explicitly enables Foreign Key support."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;") # Crucial for relational integrity
    return conn

def init_db():
    """Initializes the database structure cleanly."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Employers Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                website TEXT,
                description TEXT
            )
        ''')
        
        # 2. Job Listings Table 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                job_type TEXT NOT NULL,
                salary_range TEXT,
                FOREIGN KEY(employer_id) REFERENCES employers(id) ON DELETE CASCADE
            )
        ''')
        
        # 3. Candidates Table 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                skills TEXT,
                resume_text TEXT
            )
        ''')
        
        # 4. Job Applications Table 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                candidate_id INTEGER NOT NULL,
                cover_letter TEXT,
                status TEXT DEFAULT 'PENDING',
                FOREIGN KEY(job_id) REFERENCES job_listings(id) ON DELETE CASCADE,
                FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

def dict_factory(cursor, row):
    """Parses sqlite rows into readable dictionary objects."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
def home():
    return jsonify({"status": "Job Board API running successfully"}), 200

# ==============================================================================
# 🎯 ENDPOINT 1: POST & SEARCH JOBS 
# ==============================================================================
@app.route('/api/jobs', methods=['GET', 'POST'])
def handle_jobs():
    if request.method == 'POST':
        data = request.get_json() or {}
        
        required_fields = ('employer_id', 'title', 'description', 'location', 'job_type')
        if not all(k in data for k in required_fields):
            return jsonify({"error": "Missing required job listing parameters"}), 400
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO job_listings (employer_id, title, description, location, job_type, salary_range)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['employer_id'], data['title'], data['description'], data['location'], data['job_type'], data.get('salary_range')))
                conn.commit()
                job_id = cursor.lastrowid
            return jsonify({"message": "Job posted successfully", "job_id": job_id}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": f"Employer ID {data['employer_id']} does not exist."}), 400

    # GET request with search filters [cite: 51]
    search_query = request.args.get('search', '').strip()
    location_query = request.args.get('location', '').strip()

    with get_db_connection() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        query = "SELECT * FROM job_listings WHERE 1=1"
        params = []
        
        if search_query:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])
        if location_query:
            query += " AND location LIKE ?"
            params.append(f"%{location_query}%")
            
        cursor.execute(query, params)
        jobs = cursor.fetchall()

    return jsonify(jobs), 200

# ==============================================================================
# 🎯 ENDPOINT 2: CANDIDATE PROFILE & RESUME SETUP 
# ==============================================================================
@app.route('/api/candidates', methods=['POST'])
def create_or_update_candidate():
    data = request.get_json() or {}
    if 'username' not in data:
        return jsonify({"error": "Missing 'username' parameter"}), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO candidates (username, skills, resume_text)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                skills=excluded.skills,
                resume_text=excluded.resume_text
        ''', (data['username'], data.get('skills', ''), data.get('resume_text', '')))
        conn.commit()

    return jsonify({"message": "Candidate profile updated successfully."}), 200

# ==============================================================================
# 🎯 ENDPOINT 3: APPLY FOR JOBS & TRACK APPLICATIONS 
# ==============================================================================
@app.route('/api/applications', methods=['POST', 'GET'])
def handle_applications():
    if request.method == 'POST':
        data = request.get_json() or {}
        if not all(k in data for k in ('job_id', 'candidate_id')):
            return jsonify({"error": "Missing job_id or candidate_id"}), 400

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO applications (job_id, candidate_id, cover_letter)
                    VALUES (?, ?, ?)
                ''', (data['job_id'], data['candidate_id'], data.get('cover_letter', '')))
                conn.commit()
                app_id = cursor.lastrowid
            return jsonify({"message": "Application submitted successfully", "application_id": app_id}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Submission rejected. Check if both job_id and candidate_id exist."}), 400

    # GET application records 
    candidate_id = request.args.get('candidate_id')
    if not candidate_id:
        return jsonify({"error": "Provide candidate_id query parameter to track applications"}), 400

    with get_db_connection() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.id, j.title as job_title, a.status, a.cover_letter 
            FROM applications a
            JOIN job_listings j ON a.job_id = j.id
            WHERE a.candidate_id = ?
        ''', (candidate_id,))
        apps = cursor.fetchall()

    return jsonify(apps), 200

# ==============================================================================
# 🎯 ENDPOINT 4: EMPLOYER APPLICATION STATUS UPDATE & NOTIFICATION [cite: 51]
# ==============================================================================
@app.route('/api/applications/<int:app_id>/status', methods=['PATCH'])
def update_status(app_id):
    data = request.get_json() or {}
    new_status = data.get('status', '').strip().upper()
    
    valid_statuses = ['PENDING', 'REVIEWING', 'ACCEPTED', 'REJECTED']
    if new_status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of {valid_statuses}"}), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Application record not found"}), 404

    # Simulated notification system requirement [cite: 51]
    print(f"📢 [NOTIFICATION LOG]: Application ID {app_id} shifted to status: {new_status}")
    return jsonify({"message": f"Application status successfully changed to {new_status}."}), 200

if __name__ == '__main__':
    # Build database automatically on startup if it doesn't exist
    if not os.path.exists(DB_NAME):
        init_db()
    app.run(debug=True, port=5000)

import streamlit as st
import requests

# Page Layout Configuration
st.set_page_config(
    page_title="Job Board Platform | CodeAlpha",
    page_icon="💼",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:5000/api"

# Custom Styling for a Professional Dark/Modern Theme
st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: 800; color: #3b82f6; text-align: center; margin-bottom: 0.5rem; }
        .sub-header { font-size: 1rem; color: #64748b; text-align: center; margin-bottom: 2rem; }
        .card { background-color: #1e293b; padding: 1.5rem; border-radius: 0.75rem; border: 1px solid #334155; margin-bottom: 1rem; }
        .job-title { font-size: 1.25rem; font-weight: 700; color: #f8fafc; }
        .job-meta { font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.5rem; }
        .status-badge { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.8rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>💼 CareerHub Job Board</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>CodeAlpha Backend Development — Task 4 Dashboard</div>", unsafe_allow_html=True)

# Separate the interface into clear workflow tabs
tab1, tab2, tab3 = st.tabs(["🔍 Browse & Apply", "👤 Candidate Profile", "🏢 Employer Dashboard"])

# ==============================================================================
# 🎯 TAB 1: BROWSE JOBS, SEARCH, AND SUBMIT APPLICATIONS
# ==============================================================================
with tab1:
    st.header("Find Your Next Opportunity")
    
    # Search and Filter Bars
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search by Keywords (Title/Description)", placeholder="e.g., Python, Backend")
    with col2:
        location_term = st.text_input("Filter by Location", placeholder="e.g., Remote, New York")
        
    # Fetch job listings matching the filters from the Flask API
    try:
        params = {"search": search_term, "location": location_term}
        response = requests.get(f"{BACKEND_URL}/jobs", params=params)
        
        if response.status_code == 200:
            jobs = response.json()
            
            if not jobs:
                st.info("No job openings found matching your criteria.")
            else:
                for job in jobs:
                    with st.container():
                        st.markdown(f"""
                            <div class='card'>
                                <div class='job-title'>{job['title']}</div>
                                <div class='job-meta'>📍 {job['location']} | ⏱️ {job['job_type']} | 💰 {job['salary_range'] or 'Not Disclosed'}</div>
                                <p style='color: #cbd5e1;'>{job['description']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Interactive Application Form expander embedded under each card
                        with st.expander(f"Apply for {job['title']}"):
                            with st.form(f"apply_form_{job['id']}", clear_on_submit=True):
                                c_id = st.number_input("Your Candidate ID", min_value=1, step=1, key=f"cid_{job['id']}")
                                cover = st.text_area("Cover Letter / Pitch", placeholder="Why are you a good fit?", key=f"cov_{job['id']}")
                                submit_app = st.form_submit_button("Submit Application")
                                
                                if submit_app:
                                    app_payload = {"job_id": job['id'], "candidate_id": c_id, "cover_letter": cover}
                                    app_res = requests.post(f"{BACKEND_URL}/applications", json=app_payload)
                                    if app_res.status_code == 201:
                                        st.success(f"Successfully applied! Application ID: {app_res.json()['application_id']}")
                                    else:
                                        st.error(app_res.json().get("error", "Application failed."))
                        st.write("---")
        else:
            st.error("Failed to sync job listings from server database.")
    except Exception as e:
        st.error(f"Backend Offline: Connect to your Flask server terminal first. Error: {e}")

# ==============================================================================
# 🎯 TAB 2: CANDIDATE PROFILE & APPLICATION TRACKER
# ==============================================================================
with tab2:
    st.header("Candidate Profile Management")
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        st.subheader("Update Credentials")
        with st.form("profile_form"):
            username = st.text_input("Username / Email Address", placeholder="alex_developer")
            skills = st.text_input("Core Skills (Comma Separated)", placeholder="Python, Flask, SQLite")
            resume_text = st.text_area("Paste Resume Text / Summary", placeholder="Experienced builder handling application layer designs...")
            save_profile = st.form_submit_button("Save Profile Settings")
            
            if save_profile:
                prof_payload = {"username": username, "skills": skills, "resume_text": resume_text}
                prof_res = requests.post(f"{BACKEND_URL}/candidates", json=prof_payload)
                if prof_res.status_code == 200:
                    st.success("Candidate file updated securely!")
                else:
                    st.error(prof_res.json().get("error", "Update failed."))
                    
    with col_p2:
        st.subheader("📋 Track Your Submitted Applications")
        track_id = st.number_input("Enter your Candidate ID to view status records:", min_value=1, step=1)
        if st.button("Fetch My Applications"):
            try:
                track_res = requests.get(f"{BACKEND_URL}/applications", params={"candidate_id": track_id})
                if track_res.status_code == 200:
                    user_apps = track_res.json()
                    if not user_apps:
                        st.info("No applications found for this Candidate ID.")
                    else:
                        for app in user_apps:
                            st.markdown(f"""
                                **Job Title:** {app['job_title']}  
                                **Status:** `{app['status']}`  
                                **Cover Letter Note:** {app['cover_letter'] or 'None Provided'}
                                ---
                            """)
                else:
                    st.error(track_res.json().get("error", "Could not fetch data."))
            except Exception as e:
                st.error(f"Error connecting to data layer: {e}")

# ==============================================================================
# 🎯 TAB 3: EMPLOYER INTERFACE (POST JOBS & CONTROL STATUS)
# ==============================================================================
with tab3:
    st.header("Employer Management Portal")
    
    col_e1, col_e2 = st.columns(2)
    
    with col_e1:
        st.subheader("📢 Post a New Job Opening")
        with st.form("job_post_form", clear_on_submit=True):
            employer_id = st.number_input("Employer ID (Registered Identifier)", min_value=1, step=1)
            title = st.text_input("Job Title", placeholder="Senior Python Engineer")
            location = st.text_input("Location", placeholder="Remote / New York, NY")
            job_type = st.selectbox("Job Structure Type", ["Full-Time", "Part-Time", "Remote", "Internship"])
            salary_range = st.text_input("Salary Compensation Windows", placeholder="$90,000 - $120,000")
            description = st.text_area("Detailed Core Duties & Responsibilities")
            post_job_btn = st.form_submit_button("Publish Job Posting")
            
            if post_job_btn:
                job_payload = {
                    "employer_id": employer_id, "title": title, "location": location,
                    "job_type": job_type, "salary_range": salary_range, "description": description
                }
                post_res = requests.post(f"{BACKEND_URL}/jobs", json=job_payload)
                if post_res.status_code == 201:
                    st.success(f"Job successfully listed! ID generated: {post_res.json()['job_id']}")
                else:
                    st.error(post_res.json().get("error", "Failed to compile posting data structures."))

    with col_e2:
        st.subheader("⚡ Manage Applicant Statuses")
        st.write("Review applicant IDs and modify their review states:")
        
        with st.form("status_update_form"):
            target_app_id = st.number_input("Target Application ID", min_value=1, step=1)
            next_status = st.selectbox("Assign Evaluation State", ["PENDING", "REVIEWING", "ACCEPTED", "REJECTED"])
            update_status_btn = st.form_submit_button("Commit Evaluation Update")
            
            if update_status_btn:
                status_payload = {"status": next_status}
                patch_res = requests.patch(f"{BACKEND_URL}/applications/{target_app_id}/status", json=status_payload)
                if patch_res.status_code == 200:
                    st.success(f"Application {target_app_id} shifted to {next_status} successfully!")
                    st.info("Check your Flask terminal screen to view the simulated employer notification log output.")
                else:
                    st.error(patch_res.json().get("error", "Failed to update record state details."))
