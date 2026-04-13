import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="TalentHub Pro", page_icon="💼", layout="wide")

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('recruitment_data.db', check_same_thread=False)
    c = conn.cursor()
    # Jobs Table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, dept TEXT, status TEXT)''')
    # Candidates Table
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, exp REAL, job_id INTEGER, 
                  email TEXT, status TEXT, date_added TEXT,
                  FOREIGN KEY(job_id) REFERENCES jobs(id))''')
    conn.commit()
    return conn

conn = init_db()

# --- APP NAVIGATION ---
st.sidebar.title("📌 Navigation")
menu = ["Dashboard", "Manage Jobs", "Manage Candidates"]
choice = st.sidebar.radio("Go to", menu)

# --- 1. DASHBOARD ---
if choice == "Dashboard":
    st.title("🚀 Recruitment Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    total_jobs = pd.read_sql("SELECT COUNT(*) FROM jobs", conn).iloc[0,0]
    total_cands = pd.read_sql("SELECT COUNT(*) FROM candidates", conn).iloc[0,0]
    
    col1.metric("Total Jobs", total_jobs)
    col2.metric("Total Candidates", total_cands)
    col3.metric("Status", "Active")

    st.subheader("Recent Applications")
    recent_df = pd.read_sql('''SELECT candidates.name, jobs.title as Job_Role, candidates.status 
                               FROM candidates JOIN jobs ON candidates.job_id = jobs.id 
                               ORDER BY candidates.id DESC LIMIT 10''', conn)
    st.table(recent_df)

# --- 2. MANAGE JOBS ---
elif choice == "Manage Jobs":
    st.title("🏢 Job Management")
    
    with st.expander("➕ Add New Job Opening"):
        with st.form("job_form", clear_on_submit=True):
            title = st.text_input("Job Title (e.g. Python Developer)")
            dept = st.selectbox("Department", ["IT", "Sales", "HR", "Marketing", "Finance"])
            submit_job = st.form_submit_button("Post Job")
            
            if submit_job and title:
                c = conn.cursor()
                c.execute("INSERT INTO jobs (title, dept, status) VALUES (?, ?, ?)", (title, dept, "Open"))
                conn.commit()
                st.success(f"Job '{title}' posted successfully!")

    st.subheader("Current Openings")
    jobs_df = pd.read_sql("SELECT * FROM jobs", conn)
    st.dataframe(jobs_df, use_container_width=True)

# --- 3. MANAGE CANDIDATES ---
elif choice == "Manage Candidates":
    st.title("👤 Candidate Management")
    
    # Check if jobs exist first
    jobs_list = pd.read_sql("SELECT id, title FROM jobs", conn)
    
    if jobs_list.empty:
        st.warning("Please add at least one Job in 'Manage Jobs' before adding candidates.")
    else:
        with st.expander("➕ Register New Candidate"):
            with st.form("cand_form", clear_on_submit=True):
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                # FIXED: Force float for experience to prevent StreamlitMixedNumericTypesError
                exp = st.number_input("Years of Experience", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
                
                job_options = {row['title']: row['id'] for _, row in jobs_list.iterrows()}
                target_job = st.selectbox("Assign to Job Role", options=list(job_options.keys()))
                
                status = st.selectbox("Initial Status", ["Screening", "Interview", "Hired", "Rejected"])
                
                submit_cand = st.form_submit_button("Register Candidate")
                
                if submit_cand and name:
                    c = conn.cursor()
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    c.execute('''INSERT INTO candidates (name, exp, job_id, email, status, date_added) 
                                 VALUES (?, ?, ?, ?, ?, ?)''', 
                              (name, float(exp), job_options[target_job], email, status, date_str))
                    conn.commit()
                    st.success(f"Candidate {name} added to the system!")

    st.divider()
    st.subheader("All Candidates")
    
    # Advanced view joining tables
    query = '''
    SELECT c.id, c.name, c.email, c.exp as Experience, j.title as Applied_For, c.status, c.date_added
    FROM candidates c
    JOIN jobs j ON c.job_id = j.id
    '''
    full_df = pd.read_sql(query, conn)
    st.dataframe(full_df, use_container_width=True)

    if st.button("🗑️ Clear All Data"):
        c = conn.cursor()
        c.execute("DELETE FROM candidates")
        c.execute("DELETE FROM jobs")
        conn.commit()
        st.rerun()
