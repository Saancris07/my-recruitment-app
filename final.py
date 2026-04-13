import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

# Database Setup
conn = sqlite3.connect('agency_v3.db', check_same_thread=False)
c = conn.cursor()

def create_db():
    c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT, company TEXT, status TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, email TEXT, skill TEXT, exp INTEGER, photo BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS hires (id INTEGER PRIMARY KEY, job_title TEXT, candidate_name TEXT, hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()

create_db()

st.set_page_config(page_title="TalentHub Pro", layout="wide")

# Sidebar Menu
st.sidebar.title("🚀 TalentHub Pro")
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "💼 Job Listings", "👤 Candidates", "🎯 Hiring System"])

# --- DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("Recruitment Analytics")
    data_h = pd.read_sql('SELECT * FROM hires', conn)
    st.metric("Total Successful Hires ✅", len(data_h))
    st.divider()
    st.subheader("Recent Hiring History")
    st.dataframe(data_h, use_container_width=True)

# --- JOB LISTINGS ---
elif menu == "💼 Job Listings":
    st.title("Manage Job Vacancies")
    with st.form("job_form", clear_on_submit=True):
        t = st.text_input("Job Title")
        comp = st.text_input("Company Name")
        if st.form_submit_button("Post Job"):
            c.execute('INSERT INTO jobs (title, company, status) VALUES (?,?,"Active")', (t, comp))
            conn.commit()
            st.success("Job Posted!")
    st.dataframe(pd.read_sql('SELECT * FROM jobs', conn), use_container_width=True)

# --- CANDIDATES ---
elif menu == "👤 Candidates":
    st.title("Candidate Registration")
    with st.form("cand_form", clear_on_submit=True):
        n = st.text_input("Candidate Name")
        e = st.text_input("Email")
        s = st.text_input("Skill")
        p = st.file_uploader("Photo", type=['jpg', 'png'])
        if st.form_submit_button("Register Candidate"):
            img_byte = io.BytesIO()
            if p: Image.open(p).save(img_byte, format='PNG')
            c.execute('INSERT INTO candidates (name, email, skill, photo) VALUES (?,?,?,?)', (n, e, s, img_byte.getvalue()))
            conn.commit()
            st.success("Candidate Registered!")

# --- HIRING SYSTEM (नयाँ फिचर) ---
elif menu == "🎯 Hiring System":
    st.title("🎯 Confirm Hiring")
    jobs_df = pd.read_sql('SELECT * FROM jobs WHERE status="Active"', conn)
    cands_df = pd.read_sql('SELECT * FROM candidates', conn)

    if jobs_df.empty or cands_df.empty:
        st.warning("Please ensure you have both Active Jobs and Registered Candidates.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            job_list = jobs_df['title'] + " at " + jobs_df['company']
            selected_job = st.selectbox("Select Job", job_list)
        with col2:
            selected_cand = st.selectbox("Select Candidate", cands_df['name'])
        
        if st.button("Confirm Hire Now 🚀"):
            c.execute('INSERT INTO hires (job_title, candidate_name) VALUES (?,?)', (selected_job, selected_cand))
            # Optional: Close the job after hiring
            # c.execute('UPDATE jobs SET status="Closed" WHERE title=?', (selected_job.split(" at ")[0],))
            conn.commit()
            st.success(f"Congratulations! {selected_cand} has been hired for {selected_job}!")