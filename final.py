import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from PIL import Image
import io

# Database Setup
conn = sqlite3.connect('agency_ultimate.db', check_same_thread=False)
c = conn.cursor()

def create_db():
    c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT, company TEXT, status TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, email TEXT, skill TEXT, exp INTEGER, photo BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS hires (id INTEGER PRIMARY KEY, job_title TEXT, candidate_name TEXT, hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()

create_db()

# Security Setup
def check_password():
    if "password_correct" not in st.session_state:
        st.sidebar.title("🔐 Admin Login")
        st.sidebar.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["password_correct"]

def password_entered():
    if st.session_state["password"] == "admin123":
        st.session_state["password_correct"] = True
    else:
        st.error("❌ गलत पासवर्ड!")

if check_password():
    st.set_page_config(page_title="TalentHub Ultimate", layout="wide")
    
    st.markdown("""
        <style>
        .candidate-card { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #ddd; text-align: center; margin-bottom: 20px; }
        .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("🚀 TalentHub Ultimate")
    menu = st.sidebar.radio("मुख्य मेनु", ["📊 Dashboard", "💼 Jobs", "👤 Candidates", "🎯 Hiring", "⚙️ Admin Settings"])

    if menu == "📊 Dashboard":
        st.title("📈 Recruitment Insights")
        cands_df = pd.read_sql('SELECT * FROM candidates', conn)
        hires_df = pd.read_sql('SELECT * FROM hires', conn)
        jobs_df = pd.read_sql('SELECT * FROM jobs', conn) # Job डाटा तानिएको
        
        # यहाँ तीनवटा Metric राखिएको छ
        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Talent", len(cands_df))
        col2.metric("💼 Total Jobs", len(jobs_df)) # यहाँ जॉबको संख्या देखिनेछ
        col3.metric("🎯 Total Hires", len(hires_df))

        st.divider()
        
        st.subheader("👥 Registered Candidates")
        if not cands_df.empty:
            cols = st.columns(4)
            for idx, row in cands_df.iterrows():
                with cols[idx % 4]:
                    st.markdown("<div class='candidate-card'>", unsafe_allow_html=True)
                    if row['photo']:
                        st.image(Image.open(io.BytesIO(row['photo'])), use_container_width=True)
                    st.write(f"**{row['name']}**")
                    st.caption(f"🎯 {row['skill']}")
                    st.markdown("</div>", unsafe_allow_html=True)
            
            st.divider()
            st.subheader("📊 Experience Analytics")
            fig = px.bar(cands_df, x='name', y='exp', color='skill', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("विवरणहरू देख्नको लागि पहिले क्यान्डिडेट थप्नुहोस्।")

    # बाँकी Jobs, Candidates, Hiring कोडहरू पहिलेकै जस्तै रहन्छन्...
    elif menu == "💼 Jobs":
        st.title("💼 Manage Job Vacancies")
        with st.form("job"):
            t = st.text_input("Job Title"); co = st.text_input("Company")
            if st.form_submit_button("Post Vacancy"):
                c.execute('INSERT INTO jobs (title, company, status) VALUES (?,?,"Active")', (t, co)); conn.commit()
                st.success("Job Posted!")

    elif menu == "👤 Candidates":
        st.title("👤 Register New Candidate")
        with st.form("cand_form", clear_on_submit=True):
            n = st.text_input("Full Name"); e = st.text_input("Email"); s = st.text_input("Key Skill"); ex = st.number_input("Experience", 0); p = st.file_uploader("Photo", type=['jpg', 'png'])
            if st.form_submit_button("Save Candidate"):
                if n and e and p:
                    img_byte = io.BytesIO(); Image.open(p).save(img_byte, format='PNG')
                    c.execute('INSERT INTO candidates (name, email, skill, exp, photo) VALUES (?,?,?,?,?)', (n, e, s, ex, img_byte.getvalue()))
                    conn.commit(); st.success("Saved!"); st.balloons()

    elif menu == "🎯 Hiring":
        st.title("🎯 Smart Hiring")
        j = pd.read_sql('SELECT * FROM jobs', conn); cands = pd.read_sql('SELECT * FROM candidates', conn)
        if not j.empty and not cands.empty:
            sj = st.selectbox("Job", j['title']); sc = st.selectbox("Candidate", cands['name'])
            if st.button("Confirm Hire"):
                c.execute('INSERT INTO hires (job_title, candidate_name) VALUES (?,?)', (sj, sc)); conn.commit(); st.success("Hired!")
    
    elif menu == "⚙️ Admin Settings":
        st.title("⚙️ Data Management")
        h_df = pd.read_sql('SELECT * FROM hires', conn)
        st.download_button("📥 Download Hiring Report (CSV)", h_df.to_csv(index=False), "report.csv", "text/csv")
