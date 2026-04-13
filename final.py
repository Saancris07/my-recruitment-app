import streamlit as st
import sqlite3
import pandas as pd

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, exp REAL, job_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS jobs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, department TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- Helper Functions ---
def add_candidate(name, exp, job_id):
    conn = sqlite3.connect('recruitment.db')
    c = conn.cursor()
    c.execute("INSERT INTO candidates (name, exp, job_id) VALUES (?, ?, ?)", (name, exp, job_id))
    conn.commit()
    conn.close()

# --- Main App ---
st.title("TalentHub Pro: Unlimited Mode")

menu = ["Dashboard", "Manage Candidates", "Manage Jobs"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Manage Candidates":
    st.subheader("Add New Candidate")
    
    # Use a form to batch submit data
    with st.form("candidate_form", clear_on_submit=True):
        name = st.text_input("Candidate Name")
        # FIXED: Explicit float casting to prevent your previous error
        exp = st.number_input("Experience (Years)", value=0.0, step=0.5)
        
        # Load jobs from DB for the dropdown
        conn = sqlite3.connect('recruitment.db')
        jobs_df = pd.read_sql_query("SELECT id, title FROM jobs", conn)
        conn.close()
        
        job_options = {row['title']: row['id'] for idx, row in jobs_df.iterrows()}
        selected_job = st.selectbox("Assign to Job", options=list(job_options.keys()))
        
        submit = st.form_submit_button("Save Candidate")
        
        if submit:
            add_candidate(name, exp, job_options[selected_job])
            st.success(f"Candidate {name} added successfully!")

    # Display "Unlimited" Candidates
    st.divider()
    st.subheader("Candidate Records")
    conn = sqlite3.connect('recruitment.db')
    df = pd.read_sql_query("SELECT * FROM candidates", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

elif choice == "Manage Jobs":
    st.subheader("Post New Job")
    with st.form("job_form", clear_on_submit=True):
        title = st.text_input("Job Title")
        dept = st.text_input("Department")
        if st.form_submit_button("Post Job"):
            conn = sqlite3.connect('recruitment.db')
            c = conn.cursor()
            c.execute("INSERT INTO jobs (title, department) VALUES (?, ?)", (title, dept))
            conn.commit()
            conn.close()
            st.success("Job posted!")
