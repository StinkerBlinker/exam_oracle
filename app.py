import streamlit as st
import pdfplumber
import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. UI Configuration
st.set_page_config(page_title="OS Exam Oracle", page_icon="🔮", layout="wide")

st.title("🔮 CS311 Exam Oracle: Neural Predictor")
st.markdown("### The Predictive Engine for Operating Systems")
st.write("Drag and drop **MULTIPLE** past papers (e.g., 2023, 2024, 2025) to generate the 2026 forecast.")

# Notice: accept_multiple_files=True
uploaded_files = st.file_uploader("Upload Exam PDFs", type="pdf", accept_multiple_files=True)

os_topics = ["Deadlock", "Paging", "Synchronization", "Scheduling", "Virtual Memory", "Threads"]

if uploaded_files:
    st.success(f"{len(uploaded_files)} files secured. Engaging multi-dimensional analysis...")
    
    # Dictionary to store our timeline: {2023: {Deadlock: 5, Paging: 3}, 2024: {...}}
    timeline_data = {}
    
    with st.spinner("Extracting timelines and calculating vectors..."):
        for file in uploaded_files:
            # Extract the year from the filename (e.g., looks for "2023", "2024")
            year_match = re.search(r'(20\d{2})', file.name)
            if not year_match:
                st.warning(f"Could not find a year in filename: {file.name}. Please rename it like 'CS311_2024.pdf'")
                continue
                
            year = int(year_match.group(1))
            
            # Extract text
            with pdfplumber.open(file) as pdf:
                full_text = ""
                for i, page in enumerate(pdf.pages):
                    if i != 0: # Skip cover
                        text = page.extract_text()
                        if text: full_text += text + "\n"
            
            # Count topics
            text_lower = full_text.lower()
            topic_counts = {}
            for topic in os_topics:
                count = len(re.findall(r'\b' + topic.lower() + r'\b', text_lower))
                topic_counts[topic] = count
                
            timeline_data[year] = topic_counts
            
    # --- The Math & Prediction Engine ---
    if timeline_data:
        st.subheader("📈 2026 Predictive Forecast")
        
        # Sort the years chronologically
        years_recorded = sorted(list(timeline_data.keys()))
        future_year = years_recorded[-1] + 1
        plot_years = years_recorded + [future_year]
        
        # Create a beautiful interactive Plotly chart
        fig = go.Figure()
        
        for topic in os_topics:
            # Get the historical data for this topic
            y_values = [timeline_data[y][topic] for y in years_recorded]
            
            # Draw the historical line
            fig.add_trace(go.Scatter(
                x=years_recorded, y=y_values, 
                mode='lines+markers', name=f'{topic} (Actual)',
                line=dict(width=2)
            ))
            
            # Do the Linear Regression Math (if we have at least 2 years of data)
            if len(years_recorded) >= 2:
                m, c = np.polyfit(years_recorded, y_values, 1)
                future_prediction = m * future_year + c
                
                # Draw the dashed prediction line to 2026
                fig.add_trace(go.Scatter(
                    x=[years_recorded[-1], future_year], 
                    y=[y_values[-1], future_prediction],
                    mode='lines+markers', name=f'{topic} (Predicted)',
                    line=dict(dash='dash', width=2),
                    showlegend=False # Keep the legend clean
                ))
        
        fig.update_layout(
            title="Topic Mentions Over Time vs. Future Projection",
            xaxis_title="Year",
            yaxis_title="Mentions / Weight",
            xaxis=dict(tickmode='linear', dtick=1),
            template="plotly_dark",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)