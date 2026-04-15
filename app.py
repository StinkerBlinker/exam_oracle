import streamlit as st
import pdfplumber
import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai

# 1. UI Configuration
st.set_page_config(page_title="Universal Exam Oracle", page_icon="🔮", layout="wide")

st.title("🔮 Universal Exam Oracle")
st.markdown("### AI-Driven Multi-Subject Analysis & Prediction")

# 2. Setup Gemini AI
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("Missing Gemini API Key! Please add it to Streamlit Secrets.")
    st.stop()

# --- NEW: AI Topic Discovery Function ---
def discover_subject_and_topics(text):
    prompt = f"""
    Analyze this exam text and determine:
    1. The Subject Name (e.g., Operating Systems, Organic Chemistry).
    2. The 6 most important recurring technical topics/keywords for analysis.
    
    Return ONLY a comma-separated list in this exact format:
    Subject Name, Topic1, Topic2, Topic3, Topic4, Topic5, Topic6
    
    Text Sample: {text[:4000]}
    """
    response = model.generate_content(prompt)
    data = response.text.split(',')
    # Clean up whitespace and handle potential formatting issues
    subject = data[0].strip()
    topics = [t.strip() for t in data[1:7]]
    return subject, topics

# 3. File Uploader
uploaded_files = st.file_uploader("Upload Past Papers (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # --- PHASE 1: IDENTITY DISCOVERY ---
    with st.spinner("Oracle is identifying subject matter..."):
        # Read the first page of the first file to identify the subject
        with pdfplumber.open(uploaded_files[0]) as pdf:
            identity_text = pdf.pages[0].extract_text() or ""
        
        subject_name, discovered_topics = discover_subject_and_topics(identity_text)
        
    st.success(f"Target Identified: **{subject_name}**")
    st.info(f"Tracking Vectors: {', '.join(discovered_topics)}")

    # --- PHASE 2: DATA EXTRACTION ---
    timeline_data = {}
    all_text_combined = ""
    
    for file in uploaded_files:
        # Year detection
        year_match = re.search(r'(20\d{2})', file.name)
        year = int(year_match.group(1)) if year_match else 2026
        
        with pdfplumber.open(file) as pdf:
            page_text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted: page_text += extracted + "\n"
            all_text_combined += page_text
        
        # Count discovered topics
        text_lower = page_text.lower()
        topic_counts = {topic: len(re.findall(r'\b' + topic.lower() + r'\b', text_lower)) for topic in discovered_topics}
        timeline_data[year] = topic_counts

    # --- PHASE 3: TREND ANALYSIS ---
    if len(timeline_data) > 0:
        st.subheader(f"📈 {subject_name} Trend Forecast")
        years_recorded = sorted(list(timeline_data.keys()))
        future_year = years_recorded[-1] + 1
        
        fig = go.Figure()
        for topic in discovered_topics:
            y_values = [timeline_data[y][topic] for y in years_recorded]
            
            # Plot Actual Data
            fig.add_trace(go.Scatter(x=years_recorded, y=y_values, mode='lines+markers', name=topic))
            
            # Prediction Logic (Linear Regression)
            if len(years_recorded) >= 2:
                m, c = np.polyfit(years_recorded, y_values, 1)
                future_val = max(0, m * future_year + c)
                fig.add_trace(go.Scatter(
                    x=[years_recorded[-1], future_year], 
                    y=[y_values[-1], future_val],
                    mode='lines', name=f"{topic} (Pred)",
                    line=dict(dash='dash', width=1)
                ))

        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig, use_container_width=True)

    # --- PHASE 4: THE AI TUTOR ---
    st.divider()
    if st.button(f"Generate 14-Day {subject_name} Study Plan"):
        # Rank topics by total mentions
        total_counts = {topic: len(re.findall(r'\b' + topic.lower() + r'\b', all_text_combined.lower())) for topic in discovered_topics}
        top_topic = max(total_counts, key=total_counts.get)
        
        prompt = f"""
        Subject: {subject_name}
        Top Priority Topic: {top_topic}
        All Exam Topics: {', '.join(discovered_topics)}
        
        Generate a high-intensity 14-day study schedule. 
        Focus heavily on {top_topic} as it is trending.
        Format with bold headings and structured bullet points.
        """
        
        with st.spinner("Synthesizing strategy..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
else:
    st.info("Awaiting input. Upload PDFs to begin neural mapping.")