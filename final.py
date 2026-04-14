import streamlit as st

# --- CUSTOM CSS FOR DRIBBBLE LOOK ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #FDFDFD;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        color: white;
    }
    
    /* The "Let's Find Perfect Match" style cards */
    .stButton>button {
        background-color: #FFC107; /* Dribbble Yellow */
        color: black;
        border-radius: 15px;
        border: none;
        font-weight: bold;
        height: 3em;
        width: 100%;
    }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #FFC107;
        padding: 15px;
        border-radius: 20px;
        color: black !important;
    }
    
    /* Profile Header Styling */
    .header-text {
        font-size: 28px;
        font-weight: 800;
        color: #1E1E1E;
    }
    </style>
    """, unsafe_allow_index=True)

# --- APP CONTENT ---
st.markdown('<p class="header-text">Let\'s Find <br>Perfect Match</p>', unsafe_allow_html=True)
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE SETUP ---
conn = sqlite3.connect('recruitment.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, role TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS jobs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS placements 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, job TEXT, date TEXT)''')
    conn.commit()

init_db()

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Manage Candidates", "Manage Jobs", "Placements", "Analytics", "Data Export"])

# --- 3. PAGE CONTENT ---

if page == "Dashboard":
    st.title("📊 TalentHub Pro Dashboard")
    # Fetch real counts from DB
    cand_count = c.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    job_count = c.execute("SELECT COUNT(*) FROM jobs WHERE status='Open'").fetchone()[0]
    place_count = c.execute("SELECT COUNT(*) FROM placements").fetchone()[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Candidates", cand_count)
    col2.metric("Open Jobs", job_count)
    col3.metric("Total Placements", place_count)

elif page == "Manage Candidates":
    st.title("👤 Candidate Management")
    with st.form("cand_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        role = st.selectbox("Role", ["Developer", "Designer", "Manager", "HR"])
        if st.form_submit_button("Add Candidate"):
            c.execute("INSERT INTO candidates (name, email, role, status) VALUES (?,?,?,?)", (name, email, role, 'Active'))
            conn.commit()
            st.success(f"Added {name}!")
    st.dataframe(pd.read_sql_query("SELECT * FROM candidates", conn), use_container_width=True)

elif page == "Manage Jobs":
    st.title("💼 Job Management")
    with st.form("job_form", clear_on_submit=True):
        title = st.text_input("Job Title")
        company = st.text_input("Company Name")
        if st.form_submit_button("Post Job"):
            c.execute("INSERT INTO jobs (title, company, status) VALUES (?,?,?)", (title, company, 'Open'))
            conn.commit()
            st.success(f"Job '{title}' Posted!")
    st.dataframe(pd.read_sql_query("SELECT * FROM jobs", conn), use_container_width=True)

elif page == "Placements":
    st.title("🎯 Placements")
    # Get lists for dropdowns
    cands = [row[0] for row in c.execute("SELECT name FROM candidates").fetchall()]
    jobs = [row[0] for row in c.execute("SELECT title FROM jobs").fetchall()]
    
    if not cands or not jobs:
        st.warning("Please add candidates and jobs first!")
    else:
        with st.form("place_form"):
            sel_cand = st.selectbox("Select Candidate", cands)
            sel_job = st.selectbox("Select Job", jobs)
            if st.form_submit_button("Confirm Placement"):
                c.execute("INSERT INTO placements (candidate, job, date) VALUES (?,?,?)", 
                          (sel_cand, sel_job, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.success("Placement Recorded!")
    st.dataframe(pd.read_sql_query("SELECT * FROM placements", conn), use_container_width=True)

elif page == "Analytics":
    st.title("📈 Analytics")
    data = pd.read_sql_query("SELECT role, COUNT(*) as count FROM candidates GROUP BY role", conn)
    if not data.empty:
        st.bar_chart(data.set_index('role'))
    else:
        st.info("Add data to see charts.")

elif page == "Data Export":
    st.title("💾 Data Export")
    if st.button("Export Candidates to CSV"):
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        st.download_button("Download CSV", df.to_csv(index=False), "candidates.csv", "text/csv")
