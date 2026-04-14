import streamlit as st
import sqlite3
import pandas as pd

# --- 1. STYLING ---
st.set_page_config(page_title="TalentHub Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .job-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 15px;
        border-left: 5px solid #FFC107; margin-bottom: 10px;
    }
    .delete-btn { color: #FF4B4B; cursor: pointer; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
conn = sqlite3.connect('recruitment.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, pay TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT)')
    conn.commit()

init_db()

# --- 3. NAVIGATION ---
page = st.sidebar.radio("Menu", ["Find Jobs", "Manage Candidates"])

# --- 4. PAGE LOGIC WITH DELETE ---

if page == "Find Jobs":
    st.title("💼 Job Management")
    
    # Add Job Form
    with st.expander("➕ Post a New Job"):
        with st.form("add_job"):
            t = st.text_input("Job Title")
            co = st.text_input("Company")
            p = st.text_input("Pay")
            if st.form_submit_button("Post"):
                c.execute("INSERT INTO jobs (title, company, pay) VALUES (?,?,?)", (t, co, p))
                conn.commit()
                st.rerun()

    # Display Jobs with Delete Buttons
    jobs = c.execute("SELECT id, title, company, pay FROM jobs").fetchall()
    for j_id, j_title, j_co, j_pay in jobs:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.markdown(f"""<div class="job-card"><h3>{j_title}</h3><p>{j_co} • {j_pay}</p></div>""", unsafe_allow_html=True)
        with col2:
            # UNIQUE KEY is required for each button
            if st.button(f"🗑️ Delete", key=f"del_job_{j_id}"):
                c.execute("DELETE FROM jobs WHERE id=?", (j_id,))
                conn.commit()
                st.rerun()

elif page == "Manage Candidates":
    st.title("👤 Candidate Management")
    
    # Add Candidate Form
    with st.form("add_cand"):
        n = st.text_input("Candidate Name")
        r = st.text_input("Target Role")
        if st.form_submit_button("Add"):
            c.execute("INSERT INTO candidates (name, role) VALUES (?,?)", (n, r))
            conn.commit()
            st.rerun()

    # Display Candidates in a Table with Delete option
    df = pd.read_sql_query("SELECT id, name, role FROM candidates", conn)
    if not df.empty:
        for index, row in df.iterrows():
            c1, c2 = st.columns([0.8, 0.2])
            c1.write(f"**{row['name']}** - {row['role']}")
            if c2.button("🗑️ Remove", key=f"del_can_{row['id']}"):
                c.execute("DELETE FROM candidates WHERE id=?", (row['id'],))
                conn.commit()
                st.rerun()
