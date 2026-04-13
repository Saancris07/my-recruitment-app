import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from PIL import Image
import io

# Database Setup
conn = sqlite3.connect('agency_final.db', check_same_thread=False)
c = conn.cursor()

def create_db():
    c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT, company TEXT, status TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, email TEXT, skill TEXT, exp INTEGER, photo BLOB)')
    c.execute('CREATE TABLE IF NOT EXISTS hires (id INTEGER PRIMARY KEY, job_title TEXT, candidate_name TEXT, hire_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()

create_db()

# 4. Security: Simple Login System
def check_password():
    if "password_correct" not in st.session_state:
        st.sidebar.text_input("Admin Password", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["password_correct"]

def password_entered():
    if st.session_state["password"] == "admin123": # तपाईंले यहाँ आफ्नो पासवर्ड फेर्न सक्नुहुन्छ
        st.session_state["password_correct"] = True
    else:
        st.error("❌ गलत पासवर्ड!")

if check_password():
    st.set_page_config(page_title="TalentHub Ultimate", layout="wide")
    st.sidebar.title("🚀 TalentHub Ultimate")
    menu = st.sidebar.radio("मुख्य मेनु", ["📊 Dashboard", "💼 Jobs", "👤 Candidates", "🎯 Hiring", "⚙️ Admin Settings"])

    # 1. Advanced Analytics (Dashboard)
    if menu == "📊 Dashboard":
        st.title("📈 Recruitment Insights")
        hires_df = pd.read_sql('SELECT * FROM hires', conn)
        cands_df = pd.read_sql('SELECT * FROM candidates', conn)
        
        m1, m2 = st.columns(2)
        m1.metric("Total Successful Hires", len(hires_df))
        m2.metric("Talent Pool Size", len(cands_df))
        
        st.divider()
        if not cands_df.empty:
            st.subheader("Candidate Skills Distribution")
            fig = px.bar(cands_df, x='name', y='exp', color='skill', title="Years of Experience by Candidate")
            st.plotly_chart(fig, use_container_width=True)

    # 3. Export to Excel (Database Section मा थपिएको)
    elif menu == "⚙️ Admin Settings":
        st.title("⚙️ Control Panel")
        st.subheader("📥 Export Data")
        hires_df = pd.read_sql('SELECT * FROM hires', conn)
        if st.download_button(label="Download Hiring Report (CSV)", data=hires_df.to_csv(index=False), file_name='hiring_report.csv', mime='text/csv'):
            st.success("फाइल डाउनलोड भयो!")

    # 2. Hiring & Automation
    elif menu == "🎯 Hiring":
        st.title("🎯 Hiring System")
        jobs_df = pd.read_sql('SELECT * FROM jobs', conn)
        cands_df = pd.read_sql('SELECT * FROM candidates', conn)
        
        if not jobs_df.empty and not cands_df.empty:
            sel_job = st.selectbox("Select Job", jobs_df['title'])
            sel_cand = st.selectbox("Select Candidate", cands_df['name'])
            
            if st.button("Confirm Hire & Notify"):
                c.execute('INSERT INTO hires (job_title, candidate_name) VALUES (?,?)', (sel_job, sel_cand))
                conn.commit()
                st.balloons()
                st.success(f"बधाई छ! {sel_cand} लाई {sel_job} को लागि नियुक्त गरियो।")
                st.info(f"📧 सूचना: {sel_cand} लाई अटोमेटिक ईमेल ड्र्याफ्ट तयार भयो।") # Simulation of Email

    # (बाँकी Jobs र Candidates कोड पहिले जस्तै राख्नुहोला)
    elif menu == "💼 Jobs":
        st.title("Manage Jobs")
        with st.form("j"):
            t = st.text_input("Title"); co = st.text_input("Company")
            if st.form_submit_button("Post"):
                c.execute('INSERT INTO jobs (title, company, status) VALUES (?,?,"Active")', (t, co)); conn.commit()
    
    elif menu == "👤 Candidates":
        st.title("Add Candidate")
        with st.form("c"):
            n = st.text_input("Name"); e = st.text_input("Email"); s = st.text_input("Skill"); ex = st.number_input("Exp", 0)
            if st.form_submit_button("Save"):
                c.execute('INSERT INTO candidates (name, email, skill, exp) VALUES (?,?,?,?)', (n,e,s,ex)); conn.commit()
