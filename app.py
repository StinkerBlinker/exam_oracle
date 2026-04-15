import streamlit as st
import pdfplumber
import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai

# 1. UI Configuration & Branding
st.set_page_config(page_title="Universal Oracle Pro", page_icon="💎", layout="wide")

# Custom CSS for that "Premium" Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3e445e;
    }
    div.stButton > button:first-child {
        background-color: #4b6cb7;
        color: white;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Controls and Info
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    st.title("Oracle Control")
    st.divider()
    st.info("The Oracle uses Gemini 2.5 Flash to dynamically map your exam syllabus.")
    
    if "GEMINI_API_KEY" in st.secrets:
        st.success("API Connection: Active")
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("API Connection: Offline")
        st.stop()

# 3. Main Header
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.title("🔮 Universal Exam Oracle")
    st.write("Professional-grade exam trend analysis and predictive AI tutoring.")

# 4. Logic Functions
def discover_subject_and_topics(text):
    prompt = f"""
    Analyze this exam text and determine:
    1. The Subject Name.
    2. The 6 most important recurring technical keywords.
    Return ONLY a comma-separated list: Subject, Topic1, Topic2, Topic3, Topic4, Topic5, Topic6
    Text Sample: {text[:4000]}
    """
    response = model.generate_content(prompt)
    data = response.text.split(',')
    return data[0].strip(), [t.strip() for t in data[1:7]]

# 5. File Uploader Area
uploaded_files = st.file_uploader("Drop past papers here...", type="pdf", accept_multiple_files=True)

if uploaded_files:
    with st.status("Analyzing Repository...", expanded=True) as status:
        st.write("Identifying subject domain...")
        with pdfplumber.open(uploaded_files[0]) as pdf:
            identity_text = pdf.pages[0].extract_text() or ""
        subject_name, discovered_topics = discover_subject_and_topics(identity_text)
        
        st.write("Extracting temporal data...")
        timeline_data = {}
        all_text_combined = ""
        
        for file in uploaded_files:
            year_match = re.search(r'(20\d{2})', file.name)
            year = int(year_match.group(1)) if year_match else 2026
            with pdfplumber.open(file) as pdf:
                page_text = "\n".join([p.extract_text() or "" for p in pdf.pages])
                all_text_combined += page_text
            text_lower = page_text.lower()
            timeline_data[year] = {t: len(re.findall(r'\b' + t.lower() + r'\b', text_lower)) for t in discovered_topics}
        
        status.update(label="Analysis Complete!", state="complete", expanded=False)

    # UI: Metrics Bar
    m1, m2, m3 = st.columns(3)
    m1.metric("Subject", subject_name)
    m2.metric("Files Scanned", len(uploaded_files))
    m3.metric("Vectors Tracked", len(discovered_topics))

    # UI: Charts
    st.subheader(f"📊 {subject_name} Predictive Model")
    years_recorded = sorted(list(timeline_data.keys()))
    future_year = years_recorded[-1] + 1
    
    fig = go.Figure()
    for topic in discovered_topics:
        y_values = [timeline_data[y][topic] for y in years_recorded]
        fig.add_trace(go.Scatter(x=years_recorded, y=y_values, mode='lines+markers', name=topic))
        if len(years_recorded) >= 2:
            m, c = np.polyfit(years_recorded, y_values, 1)
            future_val = max(0, m * future_year + c)
            fig.add_trace(go.Scatter(x=[years_recorded[-1], future_year], y=[y_values[-1], future_val],
                                     mode='lines', name=f"{topic} (Est.)", line=dict(dash='dash', width=1)))

    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # UI: AI Tutor Section in a nice Container
    with st.container():
        st.divider()
        left, right = st.columns([1, 2])
        with left:
            st.subheader("🤖 AI Study Strategy")
            st.write("The Oracle will now generate a high-intensity plan based on historical frequency.")
            generate_btn = st.button("Generate Strategy Plan")
        
        with right:
            if generate_btn:
                total_counts = {t: len(re.findall(r'\b' + t.lower() + r'\b', all_text_combined.lower())) for t in discovered_topics}
                top_topic = max(total_counts, key=total_counts.get)
                prompt = f"Subject: {subject_name}. Top Topic: {top_topic}. Topics: {', '.join(discovered_topics)}. Create a 14-day intensive study plan."
                
                with st.spinner("Oracle is thinking..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
else:
    # Landing Page if no files
    st.empty()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/5610/5610931.png", width=200)
        st.info("System Ready. Please upload past exam papers in PDF format to begin the neural mapping process.")