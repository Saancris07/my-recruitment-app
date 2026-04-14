import streamlit as st
import sqlite3
import pandas as pd

# --- 1. SETTINGS & CUSTOM STYLING ---
st.set_page_config(page_title="TalentHub Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    [data-testid="stSidebar"] { background-color: #1E1E1E; }
    .job-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 15px;
        border-left: 5px solid #FFC107; margin-bottom: 10px;
    }
    .main-title { font-size: 32px; font-weight: 800; color: #FFC107; }
    div.stButton > button {
        background-color: #FFC107; color: black; border-radius: 10px;
        font-weight: bold; width: 100%; border: none;
    }
    .delete-btn > button {
        background-color: #FF4B4B !important; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION (The fix for your error) ---
conn = sqlite3.connect('recruitment.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # This creates the table if it doesn't exist on the server
    c.execute('''CREATE TABLE IF NOT EXISTS jobs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, pay TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT)''')
    conn.commit()

init_db()

# --- 3. NAVIGATION ---
page = st.sidebar.radio("Menu", ["Find Jobs", "Manage Candidates"])

# --- 4. PAGE: FIND JOBS ---
if page == "Find Jobs":
    st.markdown('<p class="main-title">Job Management</p>', unsafe_allow_html=True)
    
    # Post a New Job
    with st.expander("➕ Post a New Job", expanded=True):
        with st.form("job_form", clear_on_submit=True):
            t = st.text_input("Job Title")
            co = st.text_input("Company")
            p = st.text_input("Pay (e.g., 1700-2000)")
            if st.form_submit_button("Post Job"):
                if t and co:
                    c.execute("INSERT INTO jobs (title, company, pay) VALUES (?, ?, ?)", (t, co, p))
                    conn.commit()
                    st.success("Job posted successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in the Job Title and Company.")

    st.write("---")
    
    # Display Jobs with Delete Buttons
    st.subheader("Active Listings")
    jobs = c.execute("SELECT id, title, company, pay FROM jobs").fetchall()
    
    if not jobs:
        st.info("No jobs posted yet.")
    else:
        for j_id, j_title, j_co, j_pay in jobs:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.markdown(f"""
                    <div class="job-card">
                        <h3 style='margin:0;'>{j_title}</h3>
                        <p style='margin:0; color:#888;'>{j_co} • {j_pay}</p>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.write("") # Padding
                if st.button("🗑️ Delete", key=f"del_j_{j_id}"):
                    c.execute("DELETE FROM jobs WHERE id=?", (j_id,))
                    conn.commit()
                    st.rerun()

# --- 5. PAGE: MANAGE CANDIDATES ---
elif page == "Manage Candidates":
    st.markdown('<p class="main-title">Manage Candidates</p>', unsafe_allow_html=True)
    
    with st.form("cand_form", clear_on_submit=True):
        n = st.text_input("Candidate Name")
        r = st.text_input("Target Role")
        if st.form_submit_button("Add Candidate"):
            c.execute("INSERT INTO candidates (name, role) VALUES (?, ?)", (n, r))
            conn.commit()
            st.rerun()

    # Display Candidates Table
    candidates = c.execute("SELECT id, name, role FROM candidates").fetchall()
    for c_id, c_name, c_role in candidates:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            st.info(f"**{c_name}** — {c_role}")
        with col2:
            if st.button("🗑️ Delete", key=f"del_c_{c_id}"):
                c.execute("DELETE FROM candidates WHERE id=?", (c_id,))
                conn.commit()
                st.rerun()
