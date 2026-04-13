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
    
    # Advanced Professional CSS
    st.markdown("""
        <style>
        .main { background-color: #f4f7f6; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #007bff; }
        .candidate-card { background-color: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); text-align: center; border: 1px solid #eee; transition: 0.3s; }
        .candidate-card:hover { transform: translateY(-5px); box-shadow: 0 6px 15px rgba(0,0,0,0.12); }
        .section-title { color: #1e293b; font-weight: bold; border-bottom: 2px solid #007bff; padding-bottom: 5px; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("🚀 TalentHub Pro")
    menu = st.sidebar.radio("मुख्य मेनु", ["📊 Dashboard", "💼 Jobs", "👤 Candidates", "🎯 Hiring", "⚙️ Settings"])

    if menu == "📊 Dashboard":
        st.title("📈 Recruitment Analytics")
        cands_df = pd.read_sql('SELECT * FROM candidates', conn)
        hires_df = pd.read_sql('SELECT * FROM hires', conn)
        jobs_df = pd.read_sql('SELECT * FROM jobs', conn)
        
        # Row 1: Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("👥 Total Talent", len(cands_df))
        m2.metric("💼 Total Jobs", len(jobs_df))
        m3.metric("🎯 Total Hires", len(hires_df))
        m4.metric("📈 Status", "Active", "Live")

        st.divider()
        
        # Row 2: Graph and Stats
        col_graph, col_info = st.columns([2, 1]) # ग्राफलाई २ भाग र जानकारीलाई १ भाग
        
        with col_graph:
            st.markdown("<h3 class='section-title'>📊 Experience Distribution</h3>", unsafe_allow_html=True)
            if not cands_df.empty:
                fig = px.bar(cands_df, x='name', y='exp', color='skill', barmode='group', height=350)
                fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("डाटा उपलब्ध छैन।")

        with col_info:
            st.markdown("<h3 class='section-title'>🔔 Quick Stats</h3>", unsafe_allow_html=True)
            st.write(f"✅ **Latest Hire:** {hires_df['candidate_name'].iloc[-1] if not hires_df.empty else 'None'}")
            st.write(f"🏢 **Top Company:** {jobs_df['company'].mode()[0] if not jobs_df.empty else 'None'}")
            st.write(f"⭐ **Lead Skill:** {cands_df['skill'].mode()[0] if not cands_df.empty else 'None'}")

        st.divider()

        # Row 3: Candidate Grid
        st.markdown("<h3 class='section-title'>👥 Talent Pool Gallery</h3>", unsafe_allow_html=True)
        if not cands_df.empty:
            cols = st.columns(5) # ५ वटा सानो सानो कार्ड एकै ठाउँमा
            for idx, row in cands_df.iterrows():
                with cols[idx % 5]:
                    st.markdown("<div class='candidate-card'>", unsafe_allow_html=True)
                    if row['photo']:
                        st.image(Image.open(io.BytesIO(row['photo'])), use_container_width=True)
                    st.write(f"**{row['name']}**")
                    st.caption(f"🎯 {row['skill']}")
                    st.markdown("</div>", unsafe_allow_html=True)

    # (Jobs, Candidates, Hiring Sections remain same)
    elif menu == "💼 Jobs":
        st.title("💼 Manage Jobs")
        with st.form("j"):
            t = st.text_input("Job Title"); co = st.text_input("Company")
            if st.form_submit_button("Post Job"):
                c.execute('INSERT INTO jobs (title, company, status) VALUES (?,?,"Active")', (t, co)); conn.commit(); st.success("Posted!")

    elif menu == "👤 Candidates":
        st.title("👤 New Registration")
        with st.form("c", clear_on_submit=True):
            n = st.text_input("Full Name"); e = st.text_input("Email"); s = st.text_input("Skill"); ex = st.number_input("Exp (Yrs)", 0); p = st.file_uploader("Photo", type=['jpg', 'png'])
            if st.form_submit_button("Save Candidate"):
                if n and e and p:
                    img_byte = io.BytesIO(); Image.open(p).save(img_byte, format='PNG')
                    c.execute('INSERT INTO candidates (name, email, skill, exp, photo) VALUES (?,?,?,?,?)', (n, e, s, ex, img_byte.getvalue()))
                    conn.commit(); st.success("Registered!"); st.balloons()

    elif menu == "🎯 Hiring":
        st.title("🎯 Hiring System")
        j = pd.read_sql('SELECT * FROM jobs', conn); cands = pd.read_sql('SELECT * FROM candidates', conn)
        if not j.empty and not cands.empty:
            sj = st.selectbox("Job", j['title']); sc = st.selectbox("Candidate", cands['name'])
            if st.button("Confirm Hire"):
                c.execute('INSERT INTO hires (job_title, candidate_name) VALUES (?,?)', (sj, sc)); conn.commit(); st.success("Hired!")
    
    elif menu == "⚙️ Settings":
        st.title("⚙️ Admin")
        h_df = pd.read_sql('SELECT * FROM hires', conn)
        st.download_button("📥 Export Report", h_df.to_csv(index=False), "hires.csv")
