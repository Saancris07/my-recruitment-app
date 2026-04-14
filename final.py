import streamlit as st
import sqlite3
import pandas as pd

# --- 1. BLUE & WHITE THEME ---
st.set_page_config(page_title="TalentHub Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #003366; color: white; }
    [data-testid="stSidebar"] { background-color: #001A33; }
    .job-card {
        background-color: #004080; padding: 20px; border-radius: 15px;
        border-left: 5px solid #FFFFFF; margin-bottom: 10px; color: white;
    }
    .main-title { font-size: 32px; font-weight: 800; color: #FFFFFF; }
    p, h1, h2, h3, span, label, .stMetric { color: white !important; }
    div.stButton > button {
        background-color: #FFFFFF; color: #003366; border-radius: 10px;
        font-weight: bold; width: 100%; border: none;
    }
    .stTextInput>div>div>input {
        background-color: #002244; color: white; border: 1px solid #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION (Fixes line 67 error) ---
conn = sqlite3.connect('recruitment.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # This creates the table automatically if it's missing
    c.execute('''CREATE TABLE IF NOT EXISTS Jobs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, pay TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS Candidates 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT)''')
    conn.commit()

init_db()

# --- 3. NAVIGATION ---
page = st.sidebar.radio("Menu", ["Find Jobs", "Manage Candidates"])

# --- 4. PAGE: FIND JOBS ---
if page == "Find Jobs":
    st.markdown('<p class="main-title">Job Management</p>', unsafe_allow_html=True)
    
    with st.form("job_form", clear_on_submit=True):
        t = st.text_input("Job Title")
        co = st.text_input("Company")
        p = st.text_input("Pay Range")
        if st.form_submit_button("Post Job"):
            if t and co:
                c.execute("INSERT INTO Jobs (title, company, pay) VALUES (?, ?, ?)", (t, co, p))
                conn.commit()
                st.rerun()

    st.write("---")
    
    # Display Jobs with Delete Buttons
    jobs = c.execute("SELECT id, title, company, pay FROM Jobs").fetchall()
    for j_id, j_title, j_co, j_pay in jobs:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.markdown(f"""
                <div class="job-card">
                    <h3 style='margin:0;'>{j_title}</h3>
                    <p style='margin:0; color:#CCCCCC;'>{j_co} • {j_pay}</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write("") 
            if st.button("🗑️", key=f"del_j_{j_id}"):
                c.execute("DELETE FROM Jobs WHERE id=?", (j_id,))
                conn.commit()
                st.rerun()

# --- 5. PAGE: MANAGE CANDIDATES ---
elif page == "Manage Candidates":
    st.markdown('<p class="main-title">Manage Applicants</p>', unsafe_allow_html=True)
    
    with st.form("cand_form", clear_on_submit=True):
        n = st.text_input("Candidate Name")
        r = st.text_input("Target Role")
        if st.form_submit_button("Add Candidate"):
            c.execute("INSERT INTO Candidates (name, role) VALUES (?, ?)", (n, r))
            conn.commit()
            st.rerun()

    candidates = c.execute("SELECT id, name, role FROM Candidates").fetchall()
    for c_id, c_name, c_role in candidates:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.info(f"**{c_name}** — {c_role}")
        with col2:
            if st.button("🗑️", key=f"del_c_{c_id}"):
                c.execute("DELETE FROM Candidates WHERE id=?", (c_id,))
                conn.commit()
                st.rerun()
