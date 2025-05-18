import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.title("💰 Budget Planner")

# Step 1: Input Parameters
num_days = st.number_input("Number of Days", min_value=1, max_value=365, value=30)
total_money = st.number_input("Total Zlotys to Save", min_value=1.0, value=1000.0)

# Session state to store user points
if "points" not in st.session_state:
    st.session_state.points = [(0, 0), (num_days - 1, total_money)]

st.subheader("📈 Click to Add Points")

# Step 2: Display interactive chart
fig = go.Figure()

# Initial points
x_vals = [pt[0] for pt in st.session_state.points]
y_vals = [pt[1] for pt in st.session_state.points]

# Sort points
sorted_points = sorted(zip(x_vals, y_vals), key=lambda x: x[0])
x_vals_sorted, y_vals_sorted = zip(*sorted_points)

# Plot user points
fig.add_trace(go.Scatter(
    x=x_vals_sorted,
    y=y_vals_sorted,
    mode='lines+markers',
    line=dict(color='blue'),
    marker=dict(size=10, color='red'),
    name="Milestones"
))

# Show only ticks on selected days
tick_days = sorted(set(day for day, _ in st.session_state.points))
tick_labels = [f"Day {d}" for d in tick_days]

fig.update_layout(
    xaxis_title="Day",
    yaxis_title="Saved Money (Zloty)",
    xaxis=dict(
        range=[0, num_days - 1],
        tickmode='array',
        tickvals=tick_days,
        ticktext=tick_labels,
        tickangle=45
    ),
    yaxis=dict(range=[0, total_money]),
    dragmode='drawopenpath',
    height=500
)

# Step 3: Capture Click
st.plotly_chart(fig, use_container_width=True)

clicked_day = st.slider("Select Day to Add Point", 0, num_days - 1, 0)
clicked_money = st.slider("Select Money at that Day", 0.0, total_money, 0.0)

if st.button("➕ Add Point"):
    if (clicked_day, clicked_money) not in st.session_state.points:
        st.session_state.points.append((clicked_day, clicked_money))
        st.rerun()

if st.button("🗑️ Clear Points"):
    st.session_state.points = [(0, 0), (num_days - 1, total_money)]
    st.rerun()

# Step 4: Interpolate Full Budget Plan
full_plan = np.zeros(num_days)
sorted_points = sorted(st.session_state.points, key=lambda x: x[0])

for i in range(len(sorted_points) - 1):
    x0, y0 = sorted_points[i]
    x1, y1 = sorted_points[i + 1]
    days = x1 - x0
    if days == 0:
        continue
    slope = (y1 - y0) / days
    for d in range(x0, x1):
        full_plan[d] = y0 + slope * (d - x0)

# Final value
full_plan[sorted_points[-1][0]] = sorted_points[-1][1]

# Display result
st.subheader("📊 Daily Savings Plan")
df = pd.DataFrame({
    "Day": np.arange(num_days),
    "Zlotys Saved": full_plan
})
st.line_chart(df.set_index("Day"))

st.subheader("📥 Array of Daily Savings")
st.code(full_plan.tolist(), language='python')
