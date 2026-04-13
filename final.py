import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import datetime

# Page configuration
st.set_page_config(page_title="TalentHub Pro", page_icon="🎯", layout="wide")

# Database Setup
conn = sqlite3.connect('agency_ultimate.db', check_same_thread=False)
c = conn.cursor()

# Check existing columns and add missing ones
c.execute("PRAGMA table_info(candidates)")
existing_columns = [column[1] for column in c.fetchall()]

# Add missing columns if they don't exist
if 'phone' not in existing_columns:
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN phone TEXT")
    except:
        pass

if 'status' not in existing_columns:
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN status TEXT DEFAULT 'Available'")
    except:
        pass

if 'added_date' not in existing_columns:
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN added_date TEXT")
    except:
        pass

if 'resume_path' not in existing_columns:
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN resume_path TEXT")
    except:
        pass

if 'source' not in existing_columns:
    try:
        c.execute("ALTER TABLE candidates ADD COLUMN source TEXT")
    except:
        pass

# Create jobs table with more fields
c.execute("""CREATE TABLE IF NOT EXISTS jobs 
            (id INTEGER PRIMARY KEY, 
             title TEXT, 
             company TEXT, 
             location TEXT,
             salary_range TEXT,
             job_type TEXT,
             status TEXT,
             posted_date TEXT,
             description TEXT)""")

# Add job columns if missing
c.execute("PRAGMA table_info(jobs)")
job_columns = [column[1] for column in c.fetchall()]
for col in ['location', 'salary_range', 'job_type', 'description']:
    if col not in job_columns:
        try:
            c.execute(f"ALTER TABLE jobs ADD COLUMN {col} TEXT")
        except:
            pass

if 'posted_date' not in job_columns:
    try:
        c.execute("ALTER TABLE jobs ADD COLUMN posted_date TEXT")
    except:
        pass

# Create placements table
c.execute("""CREATE TABLE IF NOT EXISTS placements 
            (id INTEGER PRIMARY KEY,
             candidate_id INTEGER,
             job_id INTEGER,
             placement_date TEXT,
             status TEXT,
             feedback TEXT)""")

conn.commit()

# Session state for pagination
if 'candidate_page' not in st.session_state:
    st.session_state.candidate_page = 1
if 'job_page' not in st.session_state:
    st.session_state.job_page = 1
if 'records_per_page' not in st.session_state:
    st.session_state.records_per_page = 20

# Sidebar Navigation
st.sidebar.title("🎯 TalentHub Pro")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "👥 Manage Candidates", "💼 Manage Jobs", "🤝 Placements", "📈 Analytics", "📁 Data Export"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Version 2.0 | Unlimited Records Support")

# Records per page selector in sidebar
st.sidebar.subheader("Display Settings")
st.session_state.records_per_page = st.sidebar.selectbox(
    "Records per page",
    [10, 20, 50, 100, 200, 500],
    index=1
)

# ==================== DASHBOARD PAGE ====================
if page == "📊 Dashboard":
    st.title("📊 TalentHub Pro Dashboard")
    st.markdown("---")
    
    # Get metrics
    total_candidates = c.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    total_jobs = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_hires = c.execute("SELECT COUNT(*) FROM placements WHERE status='Hired'").fetchone()[0]
    active_jobs = c.execute("SELECT COUNT(*) FROM jobs WHERE status='Open'").fetchone()[0]
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total Talent", total_candidates, help="Total candidates in database")
    with col2:
        st.metric("💼 Total Jobs", total_jobs, help="Total jobs posted")
    with col3:
        st.metric("✅ Total Hires", total_hires, help="Successful placements")
    with col4:
        st.metric("📌 Active Jobs", active_jobs, help="Open positions")
    
    st.markdown("---")
    
    # Quick stats row
    col1, col2, col3 = st.columns(3)
    with col1:
        available_candidates = c.execute("SELECT COUNT(*) FROM candidates WHERE status='Available'").fetchone()[0]
        st.metric("Available for Work", available_candidates, delta=f"{available_candidates} ready")
    with col2:
        interviewing = c.execute("SELECT COUNT(*) FROM candidates WHERE status='Interviewing'").fetchone()[0]
        st.metric("In Interview Process", interviewing)
    with col3:
        placement_rate = (total_hires / total_candidates * 100) if total_candidates > 0 else 0
        st.metric("Placement Rate", f"{placement_rate:.1f}%")
    
    st.markdown("---")
    
    # Talent Pool Gallery with limit for performance
    st.subheader("🌟 Recent Talent Pool")
    
    candidates_data = c.execute("SELECT name, skill, exp, status FROM candidates ORDER BY id DESC LIMIT 12").fetchall()
    
    if not candidates_data:
        st.info("No candidates in the talent pool. Go to 'Manage Candidates' to add some!")
    else:
        cols = st.columns(3)
        for idx, candidate in enumerate(candidates_data):
            with cols[idx % 3]:
                name, skill, exp, status = candidate
                exp_val = exp if exp else 0
                skill_text = skill if skill else "Not specified"
                status_color = "🟢" if status == "Available" else "🟡" if status == "Interviewing" else "🔴"
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    <h4>{name}</h4>
                    <p>🔧 {skill_text}</p>
                    <p>📅 {exp_val} years exp</p>
                    <p>{status_color} {status if status else 'Available'}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Experience Distribution Chart
    if total_candidates > 0:
        st.subheader("📊 Experience Distribution")
        exp_data = c.execute("SELECT exp FROM candidates WHERE exp IS NOT NULL").fetchall()
        if exp_data:
            exp_df = pd.DataFrame(exp_data, columns=['exp'])
            exp_fig = px.histogram(exp_df, x='exp', title="Years of Experience Distribution", 
                                    labels={'exp': 'Years of Experience'}, 
                                    color_discrete_sequence=['#FF6B6B'],
                                    nbins=20)
            st.plotly_chart(exp_fig, use_container_width=True)
    
    # Recent Placements
    st.subheader("🎉 Recent Placements")
    recent_placements = c.execute("""
        SELECT c.name, j.title, p.placement_date 
        FROM placements p
        JOIN candidates c ON p.candidate_id = c.id
        JOIN jobs j ON p.job_id = j.id
        WHERE p.status='Hired'
        ORDER BY p.placement_date DESC
        LIMIT 10
    """).fetchall()
    
    if recent_placements:
        for placement in recent_placements:
            st.write(f"✅ **{placement[0]}** placed as **{placement[1]}** on {placement[2]}")
    else:
        st.info("No placements yet. Go to 'Placements' to hire candidates!")

# ==================== MANAGE CANDIDATES PAGE ====================
elif page == "👥 Manage Candidates":
    st.title("👥 Manage Candidates")
    st.markdown(f"**Total Candidates in Database:** {c.execute('SELECT COUNT(*) FROM candidates').fetchone()[0]}")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Candidate", "📋 View Candidates", "✏️ Edit/Delete"])
    
    # Tab 1: Add Candidate
    with tab1:
        st.subheader("Add New Candidate")
        
        with st.form("add_candidate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                candidate_name = st.text_input("Full Name *")
                candidate_email = st.text_input("Email *")
                candidate_phone = st.text_input("Phone")
                candidate_skill = st.text_input("Primary Skill")
                candidate_source = st.selectbox("Source", ["LinkedIn", "Indeed", "Referral", "Company Website", "Job Fair", "Other"])
            
            with col2:
                candidate_exp = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
                candidate_status = st.selectbox("Status", ["Available", "Interviewing", "Placed", "On Hold", "Not Interested"])
                candidate_experience = st.text_area("Previous Experience Details", height=100)
            
            submitted = st.form_submit_button("💾 Save Candidate", use_container_width=True)
            
            if submitted:
                if candidate_name and candidate_email:
                    try:
                        added_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        c.execute("""INSERT INTO candidates (name, email, phone, skill, exp, c_experience, status, added_date, source)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                  (candidate_name, candidate_email, candidate_phone, 
                                   candidate_skill, candidate_exp, candidate_experience, 
                                   candidate_status, added_date, candidate_source))
                        conn.commit()
                        st.success(f"✅ {candidate_name} added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding candidate: {e}")
                else:
                    st.error("Name and Email are required!")
    
    # Tab 2: View Candidates with Pagination and Search
    with tab2:
        st.subheader("All Candidates")
        
        # Search and filter section
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("🔍 Search by name or skill", placeholder="Type to search...")
        with col2:
            filter_status = st.selectbox("Filter by Status", ["All", "Available", "Interviewing", "Placed", "On Hold", "Not Interested"])
        with col3:
            sort_by = st.selectbox("Sort by", ["ID (Newest)", "ID (Oldest)", "Name (A-Z)", "Name (Z-A)", "Experience (High-Low)", "Experience (Low-High)"])
        
        # Build query
        query = "SELECT id, name, email, phone, skill, exp, status, added_date FROM candidates WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (name LIKE ? OR skill LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if filter_status != "All":
            query += " AND status = ?"
            params.append(filter_status)
        
        # Add sorting
        if sort_by == "ID (Newest)":
            query += " ORDER BY id DESC"
        elif sort_by == "ID (Oldest)":
            query += " ORDER BY id ASC"
        elif sort_by == "Name (A-Z)":
            query += " ORDER BY name ASC"
        elif sort_by == "Name (Z-A)":
            query += " ORDER BY name DESC"
        elif sort_by == "Experience (High-Low)":
            query += " ORDER BY exp DESC"
        elif sort_by == "Experience (Low-High)":
            query += " ORDER BY exp ASC"
        
        # Get total count for pagination
        count_query = f"SELECT COUNT(*) FROM ({query})"
        total_records = c.execute(count_query, params).fetchone()[0]
        
        # Pagination
        offset = (st.session_state.candidate_page - 1) * st.session_state.records_per_page
        query += f" LIMIT ? OFFSET ?"
        params.extend([st.session_state.records_per_page, offset])
        
        candidates_list = c.execute(query, params).fetchall()
        
        if not candidates_list:
            st.info("No candidates found. Add some candidates in the 'Add Candidate' tab!")
        else:
            candidates_df = pd.DataFrame(candidates_list, columns=['ID', 'Name', 'Email', 'Phone', 'Skill', 'Experience', 'Status', 'Added Date'])
            st.dataframe(candidates_df, use_container_width=True, hide_index=True)
            
            # Pagination controls
            st.markdown("---")
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            total_pages = (total_records + st.session_state.records_per_page - 1) // st.session_state.records_per_page
            
            with col1:
                if st.button("◀ Previous", disabled=st.session_state.candidate_page == 1):
                    st.session_state.candidate_page -= 1
                    st.rerun()
            
            with col2:
                st.write(f"Page {st.session_state.candidate_page} of {total_pages}")
            
            with col3:
                if st.button("Next ▶", disabled=st.session_state.candidate_page == total_pages):
                    st.session_state.candidate_page += 1
                    st.rerun()
            
            with col4:
                st.write(f"Showing {len(candidates_list)} of {total_records} records")
            
            # Export option
            if st.button("📥 Export All to CSV"):
                all_candidates = c.execute("SELECT id, name, email, phone, skill, exp, status, added_date FROM candidates").fetchall()
                all_df = pd.DataFrame(all_candidates, columns=['ID', 'Name', 'Email', 'Phone', 'Skill', 'Experience', 'Status', 'Added Date'])
                csv = all_df.to_csv(index=False)
                st.download_button("Download CSV", csv, f"candidates_export_{datetime.datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    
    # Tab 3: Edit/Delete
    with tab3:
        st.subheader("Edit or Delete Candidates")
        
        # Search for candidate to edit
        search_edit = st.text_input("🔍 Search candidate by name", key="search_edit")
        
        if search_edit:
            candidates_list = c.execute("SELECT id, name, skill, status FROM candidates WHERE name LIKE ? ORDER BY name", (f"%{search_edit}%",)).fetchall()
        else:
            candidates_list = c.execute("SELECT id, name, skill, status FROM candidates ORDER BY name LIMIT 100").fetchall()
        
        if candidates_list:
            candidate_options = {f"{c[1]} - {c[2]} ({c[3]})": c[0] for c in candidates_list}
            selected_candidate = st.selectbox("Select candidate to edit/delete", list(candidate_options.keys()))
            candidate_id = candidate_options[selected_candidate]
            
            # Get candidate details
            candidate_data = c.execute("SELECT * FROM candidates WHERE id=?", (candidate_id,)).fetchone()
            
            if candidate_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_name = st.text_input("Name", candidate_data[1])
                    edit_email = st.text_input("Email", candidate_data[2])
                    edit_phone = st.text_input("Phone", candidate_data[3] if candidate_data[3] else "")
                    edit_skill = st.text_input("Skill", candidate_data[4] if candidate_data[4] else "")
                
                with col2:
                    edit_exp = st.number_input("Experience (Years)", value=candidate_data[5] if candidate_data[5] else 0)
                    edit_status = st.selectbox("Status", ["Available", "Interviewing", "Placed", "On Hold", "Not Interested"], 
                                               index=["Available", "Interviewing", "Placed", "On Hold", "Not Interested"].index(candidate_data[7] if len(candidate_data) > 7 and candidate_data[7] else "Available"))
                    edit_experience = st.text_area("Experience Details", candidate_data[6] if candidate_data[6] else "", height=100)
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("💾 Update Candidate", use_container_width=True):
                        try:
                            c.execute("""UPDATE candidates 
                                        SET name=?, email=?, phone=?, skill=?, exp=?, c_experience=?, status=?
                                        WHERE id=?""",
                                      (edit_name, edit_email, edit_phone, edit_skill, edit_exp, edit_experience, edit_status, candidate_id))
                            conn.commit()
                            st.success("✅ Candidate updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating candidate: {e}")
                
                with col_btn2:
                    if st.button("🗑️ Delete Candidate", type="secondary", use_container_width=True):
                        if st.checkbox("Confirm permanent deletion"):
                            try:
                                c.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
                                conn.commit()
                                st.success("✅ Candidate deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting candidate: {e}")
        else:
            st.info("No candidates found to edit")

# ==================== MANAGE JOBS PAGE ====================
elif page == "💼 Manage Jobs":
    st.title("💼 Manage Jobs")
    st.markdown(f"**Total Jobs in Database:** {c.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]}")
    
    tab1, tab2, tab3 = st.tabs(["➕ Post Job", "📋 View Jobs", "✏️ Edit/Delete"])
    
    # Tab 1: Post Job
    with tab1:
        st.subheader("Post New Job")
        
        with st.form("add_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_title = st.text_input("Job Title *")
                job_company = st.text_input("Company Name *")
                job_location = st.text_input("Location")
                job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Remote", "Hybrid"])
            
            with col2:
                job_salary = st.text_input("Salary Range (e.g., $50k-$70k)")
                job_status = st.selectbox("Job Status", ["Open", "Closed", "On Hold"])
                job_description = st.text_area("Job Description", height=100)
            
            submitted = st.form_submit_button("💾 Post Job", use_container_width=True)
            
            if submitted:
                if job_title and job_company:
                    try:
                        posted_date = datetime.datetime.now().strftime("%Y-%m-%d")
                        c.execute("""INSERT INTO jobs (title, company, location, salary_range, job_type, status, posted_date, description)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (job_title, job_company, job_location, job_salary, job_type, job_status, posted_date, job_description))
                        conn.commit()
                        st.success(f"✅ Job '{job_title}' posted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error posting job: {e}")
                else:
                    st.error("Job Title and Company are required!")
    
    # Tab 2: View Jobs with Pagination
    with tab2:
        st.subheader("All Jobs")
        
        # Search and filter
        col1, col2 = st.columns(2)
        with col1:
            search_job = st.text_input("🔍 Search jobs by title or company")
        with col2:
            filter_job_status = st.selectbox("Filter by Status", ["All", "Open", "Closed", "On Hold"])
        
        # Build query
        job_query = "SELECT id, title, company, location, job_type, status, posted_date FROM jobs WHERE 1=1"
        job_params = []
        
        if search_job:
            job_query += " AND (title LIKE ? OR company LIKE ?)"
            job_params.extend([f"%{search_job}%", f"%{search_job}%"])
        
        if filter_job_status != "All":
            job_query += " AND status = ?"
            job_params.append(filter_job_status)
        
        job_query += " ORDER BY id DESC"
        
        # Get total count
        total_jobs_count = c.execute(f"SELECT COUNT(*) FROM ({job_query})", job_params).fetchone()[0]
        
        # Pagination
        job_offset = (st.session_state.job_page - 1) * st.session_state.records_per_page
        job_query += f" LIMIT ? OFFSET ?"
        job_params.extend([st.session_state.records_per_page, job_offset])
        
        jobs_list = c.execute(job_query, job_params).fetchall()
        
        if not jobs_list:
            st.info("No jobs found. Post some jobs in the 'Post Job' tab!")
        else:
            jobs_df = pd.DataFrame(jobs_list, columns=['ID', 'Title', 'Company', 'Location', 'Type', 'Status', 'Posted Date'])
            st.dataframe(jobs_df, use_container_width=True, hide_index=True)
            
            # Pagination controls
            total_job_pages = (total_jobs_count + st.session_state.records_per_page - 1) // st.session_state.records_per_page
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("◀ Previous Jobs", disabled=st.session_state.job_page == 1):
                    st.session_state.job_page -= 1
                    st.rerun()
            with col2:
                st.write(f"Page {st.session_state.job_page} of {total_job_pages}")
            with col3:
                if st.button("Next Jobs ▶", disabled=st.session_state.job_page == total_job_pages):
                    st.session_state.job_page += 1
                    st.rerun()
    
    # Tab 3: Edit/Delete
    with tab3:
        st.subheader("Edit or Delete Jobs")
        
        jobs_list = c.execute("SELECT id, title, company, status FROM jobs ORDER BY title LIMIT 100").fetchall()
        
        if jobs_list:
            job_options = {f"{j[1]} at {j[2]} (ID: {j[0]})": j[0] for j in jobs_list}
            selected_job = st.selectbox("Select job to edit/delete", list(job_options.keys()))
            job_id = job_options[selected_job]
            
            job_data = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            
            if job_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    edit_title = st.text_input("Job Title", job_data[1])
                    edit_company = st.text_input("Company", job_data[2])
                    edit_location = st.text_input("Location", job_data[3] if len(job_data) > 3 and job_data[3] else "")
                
                with col2:
                    edit_salary = st.text_input("Salary Range", job_data[4] if len(job_data) > 4 and job_data[4] else "")
                    edit_job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Remote", "Hybrid"],
                                                index=["Full-time", "Part-time", "Contract", "Remote", "Hybrid"].index(job_data[5] if len(job_data) > 5 and job_data[5] else "Full-time"))
                    edit_status = st.selectbox("Status", ["Open", "Closed", "On Hold"], 
                                              index=["Open", "Closed", "On Hold"].index(job_data[6] if len(job_data) > 6 and job_data[6] in ["Open", "Closed", "On Hold"] else "Open"))
                    edit_description = st.text_area("Description", job_data[8] if len(job_data) > 8 and job_data[8] else "", height=100)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 Update Job", use_container_width=True):
                        try:
                            c.execute("""UPDATE jobs 
                                        SET title=?, company=?, location=?, salary_range=?, job_type=?, status=?, description=?
                                        WHERE id=?""",
                                      (edit_title, edit_company, edit_location, edit_salary, edit_job_type, edit_status, edit_description, job_id))
                            conn.commit()
                            st.success("✅ Job updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating job: {e}")
                
                with col2:
                    if st.button("🗑️ Delete Job", type="secondary", use_container_width=True):
                        if st.checkbox("Confirm deletion"):
                            try:
                                c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
                                conn.commit()
                                st.success("✅ Job deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting job: {e}")
        else:
            st.info("No jobs to edit. Post some first!")

# ==================== PLACEMENTS PAGE ====================
elif page == "🤝 Placements":
    st.title("🤝 Candidate Placements")
    st.markdown("Match and place candidates into jobs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Candidates")
        available_candidates = c.execute("SELECT id, name, skill, exp FROM candidates WHERE status IN ('Available', 'Interviewing')").fetchall()
        
        if available_candidates:
            candidate_choices = {f"{c[1]} - {c[2]} ({c[3]} yrs)": c[0] for c in available_candidates}
            selected_candidate = st.selectbox("Select Candidate", list(candidate_choices.keys()))
            candidate_id = candidate_choices[selected_candidate]
        else:
            st.info("No candidates available")
            candidate_id = None
    
    with col2:
        st.subheader("Open Jobs")
        open_jobs = c.execute("SELECT id, title, company, location FROM jobs WHERE status='Open'").fetchall()
        
        if open_jobs:
            job_choices = {f"{j[1]} at {j[2]} ({j[3] if j[3] else 'Location TBD'})": j[0] for j in open_jobs}
            selected_job = st.selectbox("Select Job", list(job_choices.keys()))
            job_id = job_choices[selected_job]
        else:
            st.info("No open jobs")
            job_id = None
    
    if candidate_id and job_id:
        feedback = st.text_area("Placement Notes / Feedback")
        
        if st.button("✅ Place Candidate", type="primary", use_container_width=True):
            placement_date = datetime.datetime.now().strftime("%Y-%m-%d")
            try:
                c.execute("""INSERT INTO placements (candidate_id, job_id, placement_date, status, feedback) 
                            VALUES (?, ?, ?, ?, ?)""",
                          (candidate_id, job_id, placement_date, "Hired", feedback))
                c.execute("UPDATE candidates SET status='Placed' WHERE id=?", (candidate_id,))
                conn.commit()
                st.success("🎉 Candidate placed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating placement: {e}")
    
    st.markdown("---")
    st.subheader("📋 Placement History")
    
    placements_data = c.execute("""
        SELECT p.id, c.name, j.title, j.company, p.placement_date, p.feedback
        FROM placements p
        JOIN candidates c ON p.candidate_id = c.id
        JOIN jobs j ON p.job_id = j.id
        WHERE p.status='Hired'
        ORDER BY p.placement_date DESC
    """).fetchall()
    
    if not placements_data:
        st.info("No placements yet")
    else:
        placements_df = pd.DataFrame(placements_data, columns=['ID', 'Candidate', 'Job', 'Company', 'Placement Date', 'Feedback'])
        st.dataframe(placements_df, use_container_width=True, hide_index=True)
        
        # Export placements
        if st.button("📥 Export Placements to CSV"):
            csv = placements_df.to_csv(index=False)
            st.download_button("Download CSV", csv, f"placements_{datetime.datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

# ==================== ANALYTICS PAGE ====================
elif page == "📈 Analytics":
    st.title("📈 Recruitment Analytics")
    st.markdown("---")
    
    # Get all data
    total_candidates = c.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    total_jobs = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_placements = c.execute("SELECT COUNT(*) FROM placements").fetchone()[0]
    
    st.markdown(f"### 📊 Overview")
    st.markdown(f"**Total Records:** {total_candidates} Candidates | {total_jobs} Jobs | {total_placements} Placements")
    st.markdown("---")
    
    # Skills distribution
    skills_data = c.execute("SELECT skill, COUNT(*) as count FROM candidates WHERE skill IS NOT NULL AND skill != '' GROUP BY skill ORDER BY count DESC LIMIT 15").fetchall()
    
    if skills_data:
        st.subheader("🎯 Top Skills in Talent Pool")
        skills_df = pd.DataFrame(skills_data, columns=['Skill', 'Count'])
        fig_skills = px.bar(skills_df, x='Count', y='Skill', orientation='h',
                            title="Most In-Demand Skills", 
                            labels={'Count': 'Number of Candidates', 'Skill': 'Skill'},
                            color='Count', color_continuous_scale='Viridis')
        fig_skills.update_layout(height=500)
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.info("No skill data available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Experience distribution
        exp_data = c.execute("SELECT exp FROM candidates WHERE exp IS NOT NULL").fetchall()
        if exp_data:
            exp_df = pd.DataFrame(exp_data, columns=['Experience'])
            exp_df['Level'] = pd.cut(exp_df['Experience'], 
                                     bins=[0, 2, 5, 10, 20, 50], 
                                     labels=['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '20+ yrs'])
            exp_levels = exp_df['Level'].value_counts()
            fig_exp = px.pie(values=exp_levels.values, names=exp_levels.index, 
                            title="Experience Level Distribution",
                            color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_exp, use_container_width=True)
    
    with col2:
        # Status distribution
        status_data = c.execute("SELECT status, COUNT(*) FROM candidates GROUP BY status").fetchall()
        if status_data:
            status_df = pd.DataFrame(status_data, columns=['Status', 'Count'])
            fig_status = px.pie(status_df, values='Count', names='Status', 
                               title="Candidate Status Overview",
                               color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_status, use_container_width=True)
    
    # Job status
    job_status_data = c.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall()
    if job_status_data:
        st.subheader("💼 Job Status Overview")
        job_status_df = pd.DataFrame(job_status_data, columns=['Status', 'Count'])
        fig_jobs = px.bar(job_status_df, x='Status', y='Count', 
                         title="Jobs by Status",
                         color='Status', text='Count')
        st.plotly_chart(fig_jobs, use_container_width=True)
    
    # Monthly placements trend
    placements_by_month = c.execute("""
        SELECT strftime('%Y-%m', placement_date) as month, COUNT(*) 
        FROM placements 
        GROUP BY month 
        ORDER BY month DESC 
        LIMIT 12
    """).fetchall()
    
    if placements_by_month:
        st.subheader("📈 Placement Trends")
        trend_df = pd.DataFrame(placements_by_month, columns=['Month', 'Placements'])
        fig_trend = px.line(trend_df, x='Month', y='Placements', 
                           title="Placements Over Time",
                           markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Success metrics
    st.markdown("---")
    st.subheader("🎯 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        placement_rate = (total_placements / total_candidates * 100) if total_candidates > 0 else 0
        st.metric("Placement Rate", f"{placement_rate:.1f}%")
    with col2:
        avg_exp = c.execute("SELECT AVG(exp) FROM candidates WHERE exp IS NOT NULL").fetchone()[0]
        st.metric("Average Experience", f"{avg_exp:.1f} years" if avg_exp else "N/A")
    with col3:
        jobs_per_company = c.execute("SELECT COUNT(DISTINCT company) FROM jobs").fetchone()[0]
        st.metric("Unique Companies", jobs_per_company)
    with col4:
        st.metric("Success Rate", f"{(total_placements / total_jobs * 100) if total_jobs > 0 else 0:.1f}%")

# ==================== DATA EXPORT PAGE ====================
elif page == "📁 Data Export":
    st.title("📁 Data Export & Backup")
    st.markdown("Export all your data for backup or analysis")
    
    tab1, tab2 = st.tabs(["📊 Export Data", "🗑️ Data Management"])
    
    with tab1:
        st.subheader("Export Database Tables")
        
        export_type = st.radio("Select data to export", ["All Data", "Candidates Only", "Jobs Only", "Placements Only"])
        
        if st.button("📥 Generate Export", type="primary"):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_type in ["All Data", "Candidates Only"]:
                candidates_all = c.execute("SELECT * FROM candidates").fetchall()
                candidates_cols = [description[0] for description in c.description] if c.description else []
                if candidates_all:
                    candidates_df = pd.DataFrame(candidates_all, columns=candidates_cols)
                    csv_candidates = candidates_df.to_csv(index=False)
                    st.download_button("📥 Download Candidates Data", csv_candidates, f"candidates_{timestamp}.csv", "text/csv")
            
            if export_type in ["All Data", "Jobs Only"]:
                jobs_all = c.execute("SELECT * FROM jobs").fetchall()
                jobs_cols = [description[0] for description in c.description] if c.description else []
                if jobs_all:
                    jobs_df = pd.DataFrame(jobs_all, columns=jobs_cols)
                    csv_jobs = jobs_df.to_csv(index=False)
                    st.download_button("📥 Download Jobs Data", csv_jobs, f"jobs_{timestamp}.csv", "text/csv")
            
            if export_type in ["All Data", "Placements Only"]:
                placements_all = c.execute("SELECT * FROM placements").fetchall()
                placements_cols = [description[0] for description in c.description] if c.description else []
                if placements_all:
                    placements_df = pd.DataFrame(placements_all, columns=placements_cols)
                    csv_placements = placements_df.to_csv(index=False)
                   
