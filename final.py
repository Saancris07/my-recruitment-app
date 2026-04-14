import streamlit as st
import sqlite3
import pandas as pd

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="TalentHub Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    [data-testid="stSidebar"] { background-color: #1E1E1E; }
    .job-card {
        background-color: #1E1E1E; padding: 20px; border-radius: 15px;
        border-left: 5px solid #FFC107; margin-bottom: 15px;
    }
    .main-title { font-size: 36px; font-weight: 800; color: #FFC107; margin-bottom: 20px; }
    div.stButton > button {
        background-color: #FFC107; color: black; border-radius: 10px;
        font-weight: bold; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE SETUP ---
conn = sqlite3.connect('recruitment.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT, role TEXT, email TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, title TEXT, company TEXT, pay TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS placements (id INTEGER PRIMARY KEY, c_name TEXT, j_title TEXT)')
    conn.commit()

init_db()

# --- 3. NAVIGATION ---
page = st.sidebar.radio("Menu", ["Dashboard", "Find Jobs", "Candidates", "Placements"])

# --- 4. CATEGORY LOGIC ---

if page == "Dashboard":
    st.markdown('<p class="main-title">TalentHub <br>Overview</p>', unsafe_allow_html=True)
    
    # Quick Stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Live Jobs", c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0])
    c2.metric("Applicants", c.execute("SELECT COUNT(*) FROM candidates").fetchone()[0])
    c3.metric("Hired", c.execute("SELECT COUNT(*) FROM placements").fetchone()[0])

    st.write("---")
    st.subheader("Recent Activity")
    st.info("System is live and tracking recruitment data.")

elif page == "Find Jobs":
    st.markdown('<p class="main-title">Find Your <br>Perfect Match</p>', unsafe_allow_html=True)
    
    # Global Search
    search = st.text_input("🔍 Search jobs or companies...", "").lower()
    
    # Form to add new jobs
    with st.expander("➕ Post a New Job"):
        with st.form("job_form"):
            t = st.text_input("Job Title")
            co = st.text_input("Company")
            p = st.text_input("Pay Range (e.g. $100k)")
            if st.form_submit_button("Post"):
                c.execute("INSERT INTO jobs (title, company, pay) VALUES (?,?,?)", (t, co, p))
                conn.commit()
                st.rerun()

    # Display Filtered Results
    jobs = c.execute("SELECT title, company, pay FROM jobs").fetchall()
    for j_title, j_co, j_pay in jobs:
        if search in j_title.lower() or search in j_co.lower():
            st.markdown(f"""
                <div class="job-card">
                    <h3 style='margin:0;'>{j_title}</h3>
                    <p style='color:#888;'>{j_co} • Full-time</p>
                    <span style='background:#FFC107; color:black; padding:2px 8px; border-radius:5px; font-size:12px;'>{j_pay}</span>
                </div>
            """, unsafe_allow_html=True)

elif page == "Candidates":
    st.markdown('<p class="main-title">Manage <br>Applicants</p>', unsafe_allow_html=True)
    
    with st.form("cand_form"):
        n = st.text_input("Candidate Name")
        r = st.text_input("Role")
        if st.form_submit_button("Add Candidate"):
            c.execute("INSERT INTO candidates (name, role) VALUES (?,?)", (n, r))
            conn.commit()
            st.rerun()

    df = pd.read_sql_query("SELECT name as Name, role as Role FROM candidates", conn)
    st.dataframe(df, use_container_width=True)

elif page == "Placements":
    st.markdown('<p class="main-title">Successful <br>Placements</p>', unsafe_allow_html=True)
    
    # Fetch lists for dropdowns
    c_list = [x[0] for x in c.execute("SELECT name FROM candidates").fetchall()]
    j_list = [x[0] for x in c.execute("SELECT title FROM jobs").fetchall()]

    if not c_list or not j_list:
        st.warning("Add candidates and jobs first to record a placement.")
    else:
        with st.form("place_form"):
            sel_c = st.selectbox("Candidate", c_list)
            sel_j = st.selectbox("Job Title", j_list)
            if st.form_submit_button("Confirm Hire"):
                c.execute("INSERT INTO placements (c_name, j_title) VALUES (?,?)", (sel_c, sel_j))
                conn.commit()
                st.success(f"Hired {sel_c} for {sel_j}!")
        
        st.table(pd.read_sql_query("SELECT c_name as Candidate, j_title as Job FROM placements", conn))
