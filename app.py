import streamlit as st
import pdfplumber
import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai

# 1. UI Configuration
st.set_page_config(page_title="OS Exam Oracle", page_icon="🔮", layout="wide")

st.title("🔮 CS311 Exam Oracle: AI Neural Predictor")
st.markdown("### The Predictive Engine for Operating Systems")
st.write("Upload multiple past papers (e.g., 2023, 2024, 2025) to see the trends and get an AI study plan.")

# 2. File Uploader
uploaded_files = st.file_uploader("Upload Exam PDFs", type="pdf", accept_multiple_files=True)

os_topics = ["Deadlock", "Paging", "Synchronization", "Scheduling", "Virtual Memory", "Threads"]

if uploaded_files:
    st.success(f"{len(uploaded_files)} files secured. Engaging multi-dimensional analysis...")
    
    # Storage for timeline data
    timeline_data = {}
    all_text_combined = "" # For global topic ranking
    
    with st.spinner("Analyzing papers and calculating vectors..."):
        for file in uploaded_files:
            # Extract Year from filename
            year_match = re.search(r'(20\d{2})', file.name)
            year = int(year_match.group(1)) if year_match else 2025
            
            # Extract Text
            with pdfplumber.open(file) as pdf:
                page_text = ""
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted: page_text += extracted + "\n"
                all_text_combined += page_text
            
            # Count topics for this specific year
            text_lower = page_text.lower()
            topic_counts = {topic: len(re.findall(r'\b' + topic.lower() + r'\b', text_lower)) for topic in os_topics}
            timeline_data[year] = topic_counts
            
    # 3. Create Rankings (for the AI Tutor)
    total_counts = {topic: len(re.findall(r'\b' + topic.lower() + r'\b', all_text_combined.lower())) for topic in os_topics}
    df_rank = pd.DataFrame(list(total_counts.items()), columns=['Topic', 'Mentions']).sort_values(by="Mentions", ascending=False)

    # 4. Visualization (Plotly Line Chart)
    if len(timeline_data) > 0:
        st.subheader("📈 2026 Predictive Forecast")
        years_recorded = sorted(list(timeline_data.keys()))
        future_year = years_recorded[-1] + 1
        
        fig = go.Figure()
        for topic in os_topics:
            y_values = [timeline_data[y][topic] for y in years_recorded]
            # Historical Line
            fig.add_trace(go.Scatter(x=years_recorded, y=y_values, mode='lines+markers', name=f'{topic} (Actual)'))
            
            # Linear Regression for Prediction
            if len(years_recorded) >= 2:
                m, c = np.polyfit(years_recorded, y_values, 1)
                future_val = max(0, m * future_year + c) # Don't predict negative marks
                fig.add_trace(go.Scatter(
                    x=[years_recorded[-1], future_year], 
                    y=[y_values[-1], future_val],
                    mode='lines+markers', name=f'{topic} (Predicted)',
                    line=dict(dash='dash')
                ))

        fig.update_layout(template="plotly_dark", height=500, xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig, use_container_width=True)

    # 5. AI TUTOR SECTION (The Agentic Move)
    st.divider()
    st.subheader("🤖 AI Study Tutor: 2026 Strategy")
    st.write("Click below to have the Oracle's brain generate a custom study plan based on these trends.")
    
    if st.button("Generate My 14-Day Study Plan"):
        # Access secrets from Streamlit Cloud
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            top_topic = df_rank.iloc[0]['Topic']
            
            prompt = f"""
            I am a student studying Operating Systems (CS311). 
            Based on my past exam analysis, the most frequent topic is '{top_topic}'.
            The overall topics being tested are: {', '.join(os_topics)}.
            
            Please generate a high-intensity 14-day study schedule that prioritizes 
            '{top_topic}' but ensures I cover the others. Use a professional, 
            encouraging tone and format it with bold headings and bullet points.
            """
            
            with st.spinner("Consulting the Oracle's Brain..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
        else:
            st.error("Missing Gemini API Key! Please add it to your Streamlit Secrets.")

else:
    st.info("Awaiting PDF uploads to initiate neural scan...")