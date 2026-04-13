import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

# Database Persistence (अनलाइनमा डाटा हराउन नदिन)
conn = sqlite3.connect('recruitment_online.db', check_same_thread=False)
c = conn.cursor()

def create_db():
    c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT, company TEXT, status TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, email TEXT, skill TEXT, exp INTEGER, photo BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS hires (id INTEGER PRIMARY KEY, job_title TEXT, candidate_name TEXT, hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()

create_db()

st.set_page_config(page_title="TalentHub Pro Online", layout="wide")

# Sidebar Menu
st.sidebar.title("🚀 TalentHub Online")
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "💼 Job Listings", "👤 Candidates", "🎯 Hiring System"])

if menu == "📊 Dashboard":
    st.title("Recruitment Insights")
    data_h = pd.read_sql('SELECT * FROM hires', conn)
    st.metric("Total Successful Hires ✅", len(data_h))
    st.divider()
    st.subheader("Hiring History")
    st.table(data_h)

elif menu == "💼 Job Listings":
    st.title("Manage Vacancies")
    with st.form("job_form", clear_on_submit=True):
        t = st.text_input("Job Title")
        comp = st.text_input("Company Name")
        if st.form_submit_button("Post Job"):
            c.execute('INSERT INTO jobs (title, company, status) VALUES (?,?,"Active")', (t, comp))
            conn.commit()
            st.success("Job Saved Online!")
    st.dataframe(pd.read_sql('SELECT * FROM jobs', conn), use_container_width=True)

elif menu == "👤 Candidates":
    st.title("Register Talent")
    with st.form("cand_form", clear_on_submit=True):
        n = st.text_input("Name")
        e = st.text_input("Email")
        s = st.text_input("Key Skill")
        p = st.file_uploader("Candidate Photo", type=['jpg', 'png'])
        if st.form_submit_button("Save Candidate"):
            img_byte = io.BytesIO()
            if p: Image.open(p).save(img_byte, format='PNG')
            c.execute('INSERT INTO candidates (name, email, skill, photo) VALUES (?,?,?,?)', (n, e, s, img_byte.getvalue()))
            conn.commit()
            st.success("Candidate Data Secured!")

elif menu == "🎯 Hiring System":
    st.title("🎯 Hire Candidate")
    jobs_df = pd.read_sql('SELECT * FROM jobs WHERE status="Active"', conn)
    cands_df = pd.read_sql('SELECT * FROM candidates', conn)

    if not jobs_df.empty and not cands_df.empty:
        sel_job = st.selectbox("Job", jobs_df['title'] + " at " + jobs_df['company'])
        sel_cand = st.selectbox("Candidate", cands_df['name'])
        if st.button("Confirm Hiring"):
            c.execute('INSERT INTO hires (job_title, candidate_name) VALUES (?,?)', (sel_job, sel_cand))
            conn.commit()
            st.success("Candidate Hired Successfully!")
            st.balloons()
