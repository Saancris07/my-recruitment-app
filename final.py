import streamlit as st
import sqlite3
import pandas as pd

# --- 1. DATABASE CONFIGURATION ---
conn = sqlite3.connect('recruitment.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # Candidates Table
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, role TEXT, status TEXT)''')
    # Jobs Table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, status TEXT)''')
    # Placements Table
    c.execute('''CREATE TABLE IF NOT EXISTS placements 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate_name TEXT, job_title TEXT, date TEXT)''')
    conn.commit()

init_db()

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Manage Candidates", "Manage Jobs", "Placements", "Analytics", "Data Export"])

# --- 3. PAGE LOGIC ---

if page == "Dashboard":
    st.title("📊 TalentHub Pro Dashboard")
    
    # Fetch Counts
    c.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM jobs WHERE status='Open'")
    open_jobs = c.fetchone()[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Candidates", total_candidates)
    col2.metric("Open Jobs", open_jobs)
    col3.metric("System Status", "Online ✅")

elif page == "Manage Candidates":
    st.title("👤 Candidate Management")
    with st.form("add_candidate"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        role = st.selectbox("Role", ["Developer", "Designer", "Manager", "HR"])
        if st.form_submit_button("Add Candidate"):
            c.execute("INSERT INTO candidates (name, email, role, status) VALUES (?,?,?,?)", (name, email, role, 'New'))
            conn.commit()
            st.success("Candidate added successfully!")
    
    # Display List
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    st.table(df)

elif page == "Manage Jobs":
    st.title("💼 Job Management")
    with st.form("add_job"):
        title = st.text_input("Job Title")
        company = st.text_input("Company Name")
        if st.form_submit_button("Post Job"):
            c.execute("INSERT INTO jobs (title, company, status) VALUES (?,?,?)", (title, company, 'Open'))
            conn.commit()
            st.success("Job posted!")
    
    df_jobs = pd.read_sql_query("SELECT * FROM jobs", conn)
    st.table(df_jobs)

elif page == "Placements":
    st.title("🎯 Placements")
    st.info("Record successful hires here.")
    # Add placement logic here

elif page == "Analytics":
    st.title("📈 Analytics")
    st.bar_chart(pd.DataFrame({'Hires': [5, 10, 15], 'Month': ['Jan', 'Feb', 'Mar']}).set_index('Month'))

elif page == "Data Export":
    st.title("💾 Data Export")
    if st.button("Download Candidate CSV"):
        df = pd.read_sql_query("SELECT * FROM candidates", conn)
        st.download_button("Download Now", df.to_csv().encode('utf-8'), "candidates.csv", "text/csv")
