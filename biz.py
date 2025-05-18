import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.title("💰 Budget Planner – Daily Savings")

# Step 1: Input Parameters
num_days = st.number_input("Number of Days", min_value=1, max_value=365, value=30)
total_money = st.number_input("Total Zlotys to Save", min_value=1.0, value=1000.0)

max_daily_saving = total_money / num_days  # max saving per day

# Session state to store user points
if "points" not in st.session_state:
    st.session_state.points = [(1, 0), (num_days, 0)]  # daily savings points

st.subheader("📈 Click to Add Points")

# Extract and sort points
x_vals = [pt[0] for pt in st.session_state.points]
y_vals = [pt[1] for pt in st.session_state.points]
sorted_points = sorted(zip(x_vals, y_vals), key=lambda x: x[0])
x_vals_sorted, y_vals_sorted = zip(*sorted_points)

# Plot user points
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=x_vals_sorted,
    y=y_vals_sorted,
    mode='lines+markers',
    line=dict(color='blue'),
    marker=dict(size=10, color='red'),
    name="Daily Savings Points"
))

# Show only ticks on selected days
tick_days = sorted(set(x_vals_sorted))
tick_labels = [f"Day {d}" for d in tick_days]

fig.update_layout(
    xaxis_title="Day",
    yaxis_title="Money Saved per Day (Zloty)",
    xaxis=dict(
        range=[1, num_days],
        tickmode='array',
        tickvals=tick_days,
        ticktext=tick_labels,
        tickangle=45
    ),
    yaxis=dict(range=[0, max(y_vals_sorted) * 1.2 + 1]),
    dragmode='drawopenpath',
    height=500
)

st.plotly_chart(fig, use_container_width=True)

clicked_day = st.slider("Select Day to Add Point", 1, num_days, 1)
clicked_money = st.slider("Money Saved on that Day", 0.0, max_daily_saving, 0.0)

if st.button("➕ Add Point"):
    if (clicked_day, clicked_money) not in st.session_state.points:
        st.session_state.points.append((clicked_day, clicked_money))
        st.rerun()

if st.button("🗑️ Clear Points"):
    st.session_state.points = [(1, 0), (num_days, 0)]
    st.rerun()

# Interpolate Daily Savings
daily_savings = np.zeros(num_days)
sorted_points = sorted(st.session_state.points, key=lambda x: x[0])

for i in range(len(sorted_points) - 1):
    x0, y0 = sorted_points[i]
    x1, y1 = sorted_points[i + 1]
    days = x1 - x0
    if days == 0:
        continue
    slope = (y1 - y0) / days
    for d in range(x0, x1):
        daily_savings[d - 1] = y0 + slope * (d - x0)

# Set final point
daily_savings[sorted_points[-1][0] - 1] = sorted_points[-1][1]

# Clip interpolated savings within allowed daily max
raw_savings = np.clip(daily_savings, 0, max_daily_saving)

# Calculate adjustment to match total target sum
adjustment = (total_money - np.sum(raw_savings)) / num_days

# Add adjustment evenly across all days
adjusted_savings = raw_savings + adjustment

# Clip again to ensure limits after adjustment
adjusted_savings = np.clip(adjusted_savings, 0, max_daily_saving)

# Display adjusted daily savings
st.subheader("📊 Adjusted Daily Savings Plan")
df = pd.DataFrame({
    "Day": np.arange(1, num_days + 1),
    "Daily Savings": adjusted_savings
})
st.line_chart(df.set_index("Day"))

st.subheader("📥 Array of Daily Savings")
st.code(adjusted_savings.tolist(), language='python')

st.markdown(f"**Total Saved:** {round(np.sum(adjusted_savings), 2)} Zloty (Target: {total_money})")
