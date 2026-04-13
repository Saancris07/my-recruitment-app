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
    c.execute('CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, skill TEXT, exp INTEGER, photo BLOB)')
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
    st.set_page_config(page_title="TalentHub Pro", layout="wide", initial_sidebar_state="expanded")
    
    st.markdown("""
        <style>
        .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
        header { visibility: hidden; }
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: white; padding: 10px; border-radius: 10px; border-left: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .candidate-card { background-color: white; padding: 12px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); text-align: center; border: 1px solid #eee; margin-bottom: 10px; }
        .candidate-name { font-weight: bold; font-size: 1rem; color: #333; margin-top: 5px; }
        .candidate-info { font-size: 0.85rem; color: #666; margin-top: 2px; }
        .section-title { color: #333; font-size: 1rem; font-weight: bold; margin-bottom: 15px; }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("🚀 TalentHub Pro")
    menu = st.sidebar.radio("मुख्य मेनु", ["📊 Dashboard", "💼 Jobs", "👤 Candidates", "🎯 Hiring", "⚙️ Settings"])

    if menu == "📊 Dashboard":
        cands_df = pd.read_sql('SELECT * FROM candidates', conn)
        hires_df = pd.read_sql('SELECT * FROM hires', conn)
        jobs_df = pd.read_sql('SELECT * FROM jobs', conn)
        
        st.write("") 
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("👥 Total Talent", len(cands_df))
        m2.metric("💼 Total Jobs", len(jobs_df))
        m3.metric("🎯 Total Hires", len(hires_df))
        m4.metric("📈 Status", "Live")

        st.markdown("<p class='section-title'>👤 Talent Pool Gallery</p>", unsafe_allow_html=True)
        
        if not cands_df.empty:
            cols = st.columns(6)
            for idx, row in cands_df.iterrows():
                with cols[idx % 6]:
                    st.markdown("<div class='candidate-card'>", unsafe_allow_html=True)
                    if row['photo']:
                        st.image(Image.open(io.BytesIO(row['photo'])), use_container_width=True)
                    st.markdown(f"<div class='candidate-name'>{row['name']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='candidate-info'>🎯 {row['skill']}</div>", unsafe_allow_html=True)
                    if 'phone' in row and row['phone']:
                        st.markdown(f"<div class='candidate-info'>📞 {row['phone']}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No candidates available.")

        st.divider()
        col_chart, _ = st.columns([2, 1])
        with col_chart:
            st.markdown("<p class='section-title'>📊 Experience Distribution (Yrs)</p>", unsafe_allow_html=True)
            if not cands_df.empty:
                fig = px.bar(cands_df, x='name', y='exp', color='skill', height=220, template="plotly_white")
                fig.update_layout(margin=dict(l=5, r=5, t=5, b=5), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    elif menu == "👤 Candidates":
        st.title("👤 New Registration")
        with st.form("c", clear_on_submit=True):
            n = st.text_input("Full Name *")
            e = st.text_input("Email *")
            p_num = st.text_input("Phone Number")
            s = st.text_input("Skill")
            ex = st.number_input("Exp (Yrs)", 0)
            p = st.file_uploader("Photo", type=['jpg', 'png'])
            if st.form_submit_button("Save Candidate"):
                if n and e and p:
                    img_byte = io.BytesIO(); Image.open(p).save(img_byte, format='PNG')
                    c.execute('INSERT INTO candidates (name, email, phone, skill, exp, photo) VALUES (?,?,?,?,?,?)', (n, e, p_num, s, ex, img_byte.getvalue()))
                    conn.commit(); st.success("Registered!"); st.balloons()
                else:
                    st.error("Please fill Name, Email and Photo.")

    # Jobs, Hiring, Settings Sections (Same as before)
    elif menu == "💼 Jobs":
        st.title("💼 Manage Jobs")
        with st.form("j"):
            t = st.text_input("Job Title"); co = st.text_input("Company")
            if st.form_submit_button("Post Job"):
                c.execute('INSERT INTO jobs (title, company, status) VALUES (?,?,"Active")', (t, co)); conn.commit(); st.success("Posted!")

    elif menu == "🎯 Hiring":
        st.title("🎯 Hiring System")
        j = pd.read_sql('SELECT * FROM jobs', conn); cands = pd.read_sql('SELECT * FROM candidates', conn)
        if not j.empty and not cands.empty:
            sj = st.selectbox("Job", j['title']); sc = st.selectbox("Candidate", cands['name'])
            if st.button("Confirm Hire"):
                c.execute('INSERT INTO hires (job_title, candidate_name) VALUES (?,?)', (sj, sc)); conn.commit(); st.success("Hired!")
    
    elif menu == "⚙️ Settings":
        st.title("⚙️ Admin Settings")
        h_df = pd.read_sql('SELECT * FROM hires', conn)
        st.download_button("📥 Export Hiring Report", h_df.to_csv(index=False), "hires.csv", "text/csv")
