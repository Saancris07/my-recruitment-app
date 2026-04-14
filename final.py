import streamlit as st
import sqlite3
import pandas as pd

# --- DATABASE SETUP ---
# Connect to SQLite database
conn = sqlite3.connect('recruitment.db', check_same_thread=False)
c = conn.cursor()

# Initialize the database and create tables if they don't exist
def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS candidates 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, email TEXT, role TEXT, status TEXT)''')
    # Add other tables (jobs, placements, etc.) here if needed
    conn.commit()

init_db()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Manage Candidates", "Manage Jobs", "Placements", "Analytics", "Data Export"])

# --- DASHBOARD PAGE ---
if page == "Dashboard":
    st.title("📊 TalentHub Pro Dashboard")
    
    # This was the specific line (122) causing your error
    # It now works because init_db() ensures the table exists
    c.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = c.fetchone()[0]
    
    # Display simple metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Candidates", total_candidates)
    col2.metric("Open Jobs", "5") # Example static value
    col3.metric("Placements", "12") # Example static value

    st.write("Welcome to the TalentHub Pro management system.")

# --- OTHER PAGES (Placeholders) ---
elif page == "Manage Candidates":
    st.header("Manage Candidates")
    name = st.text_input("Candidate Name")
    role = st.text_input("Target Role")
    if st.button("Add Candidate"):
        c.execute("INSERT INTO candidates (name, role, status) VALUES (?, ?, ?)", (name, role, 'New'))
        conn.commit()
        st.success(f"Added {name}!")

# (Add similar logic for other pages here...)
