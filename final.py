import streamlit as st

# --- FIX: Changed unsafe_allow_index to unsafe_allow_html ---
st.markdown("""
    <style>
    /* Dark & Yellow Theme */
    .stApp { background-color: #121212; color: white; }
    
    /* Custom Card Style */
    .job-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #FFC107;
        margin-bottom: 10px;
    }
    
    /* Yellow Button Style */
    div.stButton > button:first-child {
        background-color: #FFC107;
        color: black;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    
    .main-title { font-size: 40px; font-weight: 800; color: #FFC107; }
    </style>
    """, unsafe_allow_html=True)

# --- APP LAYOUT ---
st.markdown('<p class="main-title">Let\'s Find <br>Your Perfect Match</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.button("🔍 Find Job")
with col2:
    st.button("📝 Post Job")

st.subheader("Popular Projects")

# Example Job Card
st.markdown("""
    <div class="job-card">
        <h3 style='margin:0;'>Project Manager</h3>
        <p style='color:#888;'>Google • Full-time</p>
        <span style='background:#FFC107; color:black; padding:2px 8px; border-radius:5px; font-size:12px;'>$120k - $150k</span>
    </div>
    """, unsafe_allow_html=True)
