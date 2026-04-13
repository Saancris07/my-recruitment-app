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

# Create tables
c.execute("""CREATE TABLE IF NOT EXISTS jobs 
            (id INTEGER PRIMARY KEY, 
             title TEXT, 
             company TEXT, 
             status TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS candidates 
            (id INTEGER PRIMARY KEY, 
             name TEXT, 
             email TEXT, 
             phone TEXT, 
             skill TEXT, 
             exp INTEGER, 
             c_experience TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS placements 
            (id INTEGER PRIMARY KEY,
             candidate_id INTEGER,
             job_id INTEGER,
             placement_date TEXT,
             status TEXT)""")

conn.commit()

# Sidebar Navigation
st.sidebar.title("🎯 TalentHub Pro")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "👥 Manage Candidates", "💼 Manage Jobs", "🤝 Placements", "📈 Analytics"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Version 1.0 | Recruitment Management System")

# ==================== DASHBOARD PAGE ====================
if page == "📊 Dashboard":
    st.title("📊 TalentHub Pro Dashboard")
    st.markdown("---")
    
    # Get metrics
    total_candidates = c.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    total_jobs = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_hires = c.execute("SELECT COUNT(*) FROM placements WHERE status='Hired'").fetchone()[0]
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total Talent", total_candidates)
    with col2:
        st.metric("💼 Total Jobs", total_jobs)
    with col3:
        st.metric("✅ Total Hires", total_hires)
    with col4:
        active_jobs = c.execute("SELECT COUNT(*) FROM jobs WHERE status='Open'").fetchone()[0]
        st.metric("📌 Active Jobs", active_jobs)
    
    st.markdown("---")
    
    # Talent Pool Gallery
    st.subheader("🌟 Talent Pool Gallery")
    
    candidates_data = c.execute("SELECT name, skill, exp FROM candidates").fetchall()
    
    if not candidates_data:
        st.info("No candidates in the talent pool. Go to 'Manage Candidates' to add some!")
    else:
        cols = st.columns(3)
        for idx, candidate in enumerate(candidates_data):
            with cols[idx % 3]:
                name, skill, exp = candidate
                exp_val = exp if exp else 0
                skill_text = skill if skill else "Not specified"
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    <h4>{name}</h4>
                    <p>🔧 {skill_text}</p>
                    <p>📅 {exp_val} years exp</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Experience Distribution Chart
    if candidates_data:
        st.subheader("📊 Experience Distribution")
        exp_list = [c[2] for c in candidates_data if c[2] is not None]
        if exp_list:
            exp_df = pd.DataFrame({'exp': exp_list})
            exp_fig = px.histogram(exp_df, x='exp', title="Years of Experience Distribution", 
                                    labels={'exp': 'Years of Experience'}, color_discrete_sequence=['#FF6B6B'])
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
        LIMIT 5
    """).fetchall()
    
    if recent_placements:
        for placement in recent_placements:
            st.write(f"✅ **{placement[0]}** placed as **{placement[1]}** on {placement[2]}")
    else:
        st.info("No placements yet. Go to 'Placements' to hire candidates!")

# ==================== MANAGE CANDIDATES PAGE ====================
elif page == "👥 Manage Candidates":
    st.title("👥 Manage Candidates")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Candidate", "📋 View Candidates", "✏️ Edit/Delete"])
    
    # Tab 1: Add Candidate
    with tab1:
        st.subheader("Add New Candidate")
        
        with st.form("add_candidate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                candidate_name = st.text_input("Full Name *", key="cand_name")
                candidate_email = st.text_input("Email *", key="cand_email")
                candidate_phone = st.text_input("Phone", key="cand_phone")
                candidate_skill = st.text_input("Primary Skill", key="cand_skill")
            
            with col2:
                candidate_exp = st.number_input("Years of Experience", min_value=0, step=1, key="cand_exp")
                candidate_experience = st.text_area("Previous Experience Details", key="cand_exp_details")
            
            submitted = st.form_submit_button("💾 Save Candidate")
            
            if submitted:
                if candidate_name and candidate_email:
                    try:
                        c.execute("""INSERT INTO candidates (name, email, phone, skill, exp, c_experience)
                                    VALUES (?, ?, ?, ?, ?, ?)""", 
                                  (candidate_name, candidate_email, candidate_phone, 
                                   candidate_skill, candidate_exp, candidate_experience))
                        conn.commit()
                        st.success(f"✅ {candidate_name} added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding candidate: {e}")
                else:
                    st.error("Name and Email are required!")
    
    # Tab 2: View Candidates
    with tab2:
        st.subheader("All Candidates")
        
        candidates_list = c.execute("SELECT id, name, email, phone, skill, exp FROM candidates ORDER BY id DESC").fetchall()
        
        if not candidates_list:
            st.info("No candidates found. Add some candidates in the 'Add Candidate' tab!")
        else:
            # Convert to DataFrame for display
            candidates_df = pd.DataFrame(candidates_list, columns=['ID', 'Name', 'Email', 'Phone', 'Skill', 'Experience'])
            
            # Search filter
            search = st.text_input("🔍 Search candidates by name or skill")
            if search:
                candidates_df = candidates_df[candidates_df['Name'].str.contains(search, case=False) | 
                                              candidates_df['Skill'].str.contains(search, case=False)]
            
            st.dataframe(candidates_df, use_container_width=True, hide_index=True)
            
            # Export option
            if st.button("📥 Export to CSV"):
                csv = candidates_df.to_csv(index=False)
                st.download_button("Download CSV", csv, "candidates.csv", "text/csv")
    
    # Tab 3: Edit/Delete
    with tab3:
        st.subheader("Edit or Delete Candidates")
        
        candidates_list = c.execute("SELECT id, name, skill FROM candidates ORDER BY name").fetchall()
        
        if candidates_list:
            candidate_options = {f"{c[1]} (ID: {c[0]})": c[0] for c in candidates_list}
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
                    edit_experience = st.text_area("Experience Details", candidate_data[6] if candidate_data[6] else "")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("💾 Update Candidate"):
                        try:
                            c.execute("""UPDATE candidates 
                                        SET name=?, email=?, phone=?, skill=?, exp=?, c_experience=?
                                        WHERE id=?""",
                                      (edit_name, edit_email, edit_phone, edit_skill, edit_exp, edit_experience, candidate_id))
                            conn.commit()
                            st.success("✅ Candidate updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating candidate: {e}")
                
                with col_btn2:
                    if st.button("🗑️ Delete Candidate", type="secondary"):
                        if st.checkbox("Confirm deletion"):
                            try:
                                c.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
                                conn.commit()
                                st.success("✅ Candidate deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting candidate: {e}")
        else:
            st.info("No candidates to edit. Add some first!")

# ==================== MANAGE JOBS PAGE ====================
elif page == "💼 Manage Jobs":
    st.title("💼 Manage Jobs")
    
    tab1, tab2, tab3 = st.tabs(["➕ Post Job", "📋 View Jobs", "✏️ Edit/Delete"])
    
    # Tab 1: Post Job
    with tab1:
        st.subheader("Post New Job")
        
        with st.form("add_job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                job_title = st.text_input("Job Title *")
                job_company = st.text_input("Company Name *")
            
            with col2:
                job_status = st.selectbox("Job Status", ["Open", "Closed", "On Hold"])
            
            submitted = st.form_submit_button("💾 Post Job")
            
            if submitted:
                if job_title and job_company:
                    try:
                        c.execute("INSERT INTO jobs (title, company, status) VALUES (?, ?, ?)",
                                  (job_title, job_company, job_status))
                        conn.commit()
                        st.success(f"✅ Job '{job_title}' posted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error posting job: {e}")
                else:
                    st.error("Job Title and Company are required!")
    
    # Tab 2: View Jobs
    with tab2:
        st.subheader("All Jobs")
        
        jobs_list = c.execute("SELECT id, title, company, status FROM jobs ORDER BY id DESC").fetchall()
        
        if not jobs_list:
            st.info("No jobs found. Post some jobs in the 'Post Job' tab!")
        else:
            jobs_df = pd.DataFrame(jobs_list, columns=['ID', 'Title', 'Company', 'Status'])
            
            search_job = st.text_input("🔍 Search jobs by title or company")
            if search_job:
                jobs_df = jobs_df[jobs_df['Title'].str.contains(search_job, case=False) | 
                                  jobs_df['Company'].str.contains(search_job, case=False)]
            
            st.dataframe(jobs_df, use_container_width=True, hide_index=True)
    
    # Tab 3: Edit/Delete
    with tab3:
        st.subheader("Edit or Delete Jobs")
        
        jobs_list = c.execute("SELECT id, title, company, status FROM jobs ORDER BY title").fetchall()
        
        if jobs_list:
            job_options = {f"{j[1]} at {j[2]} (ID: {j[0]})": j[0] for j in jobs_list}
            selected_job = st.selectbox("Select job to edit/delete", list(job_options.keys()))
            job_id = job_options[selected_job]
            
            job_data = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            
            if job_data:
                edit_title = st.text_input("Job Title", job_data[1])
                edit_company = st.text_input("Company", job_data[2])
                edit_status = st.selectbox("Status", ["Open", "Closed", "On Hold"], 
                                          index=["Open", "Closed", "On Hold"].index(job_data[3]) if job_data[3] in ["Open", "Closed", "On Hold"] else 0)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 Update Job"):
                        try:
                            c.execute("UPDATE jobs SET title=?, company=?, status=? WHERE id=?",
                                      (edit_title, edit_company, edit_status, job_id))
                            conn.commit()
                            st.success("✅ Job updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating job: {e}")
                
                with col2:
                    if st.button("🗑️ Delete Job", type="secondary"):
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
        available_candidates = c.execute("SELECT id, name, skill, exp FROM candidates").fetchall()
        
        if available_candidates:
            candidate_choices = {f"{c[1]} - {c[2]} ({c[3]} yrs)": c[0] for c in available_candidates}
            selected_candidate = st.selectbox("Select Candidate", list(candidate_choices.keys()))
            candidate_id = candidate_choices[selected_candidate]
        else:
            st.info("No candidates available")
            candidate_id = None
    
    with col2:
        st.subheader("Open Jobs")
        open_jobs = c.execute("SELECT id, title, company FROM jobs WHERE status='Open'").fetchall()
        
        if open_jobs:
            job_choices = {f"{j[1]} at {j[2]}": j[0] for j in open_jobs}
            selected_job = st.selectbox("Select Job", list(job_choices.keys()))
            job_id = job_choices[selected_job]
        else:
            st.info("No open jobs")
            job_id = None
    
    if candidate_id and job_id:
        if st.button("✅ Place Candidate", type="primary"):
            placement_date = datetime.datetime.now().strftime("%Y-%m-%d")
            try:
                c.execute("INSERT INTO placements (candidate_id, job_id, placement_date, status) VALUES (?, ?, ?, ?)",
                          (candidate_id, job_id, placement_date, "Hired"))
                conn.commit()
                st.success("🎉 Candidate placed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating placement: {e}")
    
    st.markdown("---")
    st.subheader("📋 Placement History")
    
    placements_data = c.execute("""
        SELECT p.id, c.name, j.title, j.company, p.placement_date
        FROM placements p
        JOIN candidates c ON p.candidate_id = c.id
        JOIN jobs j ON p.job_id = j.id
        ORDER BY p.placement_date DESC
    """).fetchall()
    
    if not placements_data:
        st.info("No placements yet")
    else:
        placements_df = pd.DataFrame(placements_data, columns=['ID', 'Candidate', 'Job', 'Company', 'Placement Date'])
        st.dataframe(placements_df, use_container_width=True, hide_index=True)

# ==================== ANALYTICS PAGE ====================
elif page == "📈 Analytics":
    st.title("📈 Recruitment Analytics")
    st.markdown("---")
    
    # Get data for analytics
    candidates_data = c.execute("SELECT skill, exp FROM candidates").fetchall()
    jobs_data = c.execute("SELECT status FROM jobs").fetchall()
    placements_data = c.execute("SELECT * FROM placements").fetchall()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Skills distribution
        if candidates_data:
            st.subheader("Top Skills in Talent Pool")
            skills = [c[0] for c in candidates_data if c[0]]
            if skills:
                skill_counts = pd.Series(skills).value_counts().head(10)
                fig_skills = px.bar(x=skill_counts.values, y=skill_counts.index, orientation='h',
                                    title="Most Common Skills", labels={'x': 'Count', 'y': 'Skill'})
                st.plotly_chart(fig_skills, use_container_width=True)
            else:
                st.info("No skill data available")
        else:
            st.info("No candidate data available")
    
    with col2:
        # Experience distribution
        if candidates_data:
            st.subheader("Experience Level Distribution")
            exp_values = [c[1] for c in candidates_data if c[1] is not None]
            if exp_values:
                exp_df = pd.DataFrame({'exp': exp_values})
                exp_df['exp_level'] = pd.cut(exp_df['exp'], 
                                            bins=[0, 2, 5, 10, 100], 
                                            labels=['Junior (0-2)', 'Mid (3-5)', 'Senior (6-10)', 'Expert (10+)'])
                exp_levels = exp_df['exp_level'].value_counts()
                if not exp_levels.empty:
                    fig_exp = px.bar(x=exp_levels.index, y=exp_levels.values, title="Experience Levels",
                                     color=exp_levels.index, labels={'x': 'Level', 'y': 'Number of Candidates'})
                    st.plotly_chart(fig_exp, use_container_width=True)
                else:
                    st.info("No experience data available")
            else:
                st.info("No experience data available")
    
    # Job stats
    if jobs_data:
        st.subheader("Job Status Overview")
        job_status = pd.Series([j[0] for j in jobs_data]).value_counts()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Open Jobs", job_status.get('Open', 0))
        with col2:
            st.metric("Closed Jobs", job_status.get('Closed', 0))
        with col3:
            st.metric("On Hold", job_status.get('On Hold', 0))
    
    # Success rate
    st.markdown("---")
    st.subheader("🎯 Placement Success Rate")
    
    total_candidates = len(candidates_data)
    total_placements = len(placements_data)
    
    if total_candidates > 0:
        success_rate = (total_placements / total_candidates) * 100
        st.metric("Placement Rate", f"{success_rate:.1f}%", f"{total_placements} out of {total_candidates} candidates placed")
        st.progress(success_rate / 100)
    else:
        st.info("Add candidates to see placement metrics")

st.markdown("---")
st.caption("© 2024 TalentHub Pro | Recruitment Management System")
