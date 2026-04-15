import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("CS311 Exam Oracle")
st.write("Upload your marks to see the 2026 trend.")

# A simple slider to "Simulate" data input
deadlock_2025 = st.slider("2025 Deadlock Marks", 0, 20, 10)

# Run your math here...
# (The same NumPy logic we just wrote)


# Plotting the 'Deadlock' trend

# Create the 10-dimensional Basis (Identity Matrix)
# Each row represents 100% of one specific OS Topic
TOPIC_BASIS = np.eye(10)

syscalls = TOPIC_BASIS[0]
states = TOPIC_BASIS[1]
raid = TOPIC_BASIS[2]
sync = TOPIC_BASIS[3]
threads = TOPIC_BASIS[4]
deadlock = TOPIC_BASIS[5]
disk = TOPIC_BASIS[6]
page = TOPIC_BASIS[7]
replace = TOPIC_BASIS[8]
alloc = TOPIC_BASIS[9]

print("Topic 'Deadlock' Vector:", deadlock)


#Weights extracted from the past papers

w_2023 = [10, 4, 4, 6, 4, 8, 10, 10, 6, 4]
w_2024 = [12, 4, 4, 4, 4, 10, 10, 8, 6, 4]
w_2025 = [10, 4, 4, 4, 4, 10, 10, 10, 6, 4]


# Create the vectors. @ is the dot product operator
exam_2023 = np.array(w_2023) @ TOPIC_BASIS
exam_2024 = np.array(w_2024) @ TOPIC_BASIS
exam_2025 = np.array(w_2025) @ TOPIC_BASIS

data_matrix = np.vstack([exam_2023, exam_2024, exam_2025])

print("Data matrix (3 years x 10 topics):\n", data_matrix)

#prediction_avg = np.mean(data_matrix, axis=0)
#print("2026 prediction (average)", prediction_avg) jst using past to predict future by average


# Years as our X-axis
years = np.array([2023, 2024, 2025])

# We will store our predictions here
prediction_2026 = []

# Loop through each topic (each column in our matrix)
for i in range(10):
    # Get the marks for this specific topic across the 3 years
    y = data_matrix[:, i]
    
    # Fit a 'polynomial' of degree 1 (a straight line: y = mx + c)
    # This finds the 'm' (slope) and 'c' (intercept) that fits best
    coefficients = np.polyfit(years, y, 1)
    
    # Use the 'm' and 'c' to calculate the value for 2026
    val_2026 = np.polyval(coefficients, 2026)
    
    # Marks can't be negative, so we clip at 0
    prediction_2026.append(max(0, round(val_2026, 1)))

print("--- 2026 PREDICTED EXAM WEIGHTS ---")
topics = ["SysCalls", "States", "RAID", "Sync", "Threads", "Deadlock", "Disk", "Paging", "Replace", "Alloc"]
for name, val in zip(topics, prediction_2026):
    print(f"{name}: {val} Marks")



    # Calculate the Standard Deviation for each column (topic)
std_devs = np.std(data_matrix, axis=0)

print("\n--- PREDICTION RELIABILITY (Lower is better) ---")
for name, sd in zip(topics, std_devs):
    # A high SD means the examiner is unpredictable on this topic
    status = "STABLE" if sd < 1 else "VOLATILE"
    print(f"{name}: {sd:.2f} ({status})")


plt.scatter(years, data_matrix[:, 5], color='blue', label='Actual Marks')
plt.plot([2023, 2026], np.polyval(np.polyfit(years, data_matrix[:, 5], 1), [2023, 2026]), color='red', label='Trend Line')
plt.title("Deadlock Weight Prediction")
plt.legend()
plt.show()


# Create the figure
fig = go.Figure()

# Add the actual data points
fig.add_trace(go.Scatter(
    x=years, y=data_matrix[:, 5], 
    mode='markers', name='Actual Marks',
    marker=dict(size=12, color='blue')
))

# Add the prediction line
future_years = [2023, 2024, 2025, 2026]
m, c = np.polyfit(years, data_matrix[:, 5], 1)
prediction_line = [m*x + c for x in future_years]

fig.add_trace(go.Scatter(
    x=future_years, y=prediction_line, 
    mode='lines+markers', name='Trend Line',
    line=dict(dash='dash', color='red')
))


fig.update_layout(
    title='Interactive OS Oracle: Deadlock Prediction',
    xaxis_title='Year',
    yaxis_title='Mark Weight',
    template='plotly_dark' # Use Dark Mode for that "Aura"
)

fig.show()
