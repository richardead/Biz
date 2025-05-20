import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os

st.title("Budget Planner")

SAVE_FILE = "saved_points.csv"

# Functions to save/load points persistently
def save_points(points):
    df = pd.DataFrame(points, columns=["Day", "Savings"])
    df.to_csv(SAVE_FILE, index=False)

def load_points():
    if os.path.exists(SAVE_FILE):
        df = pd.read_csv(SAVE_FILE)
        return list(zip(df["Day"], df["Savings"]))
    return None

# Load saved points or initialize default
if "points" not in st.session_state:
    loaded_points = load_points()
    if loaded_points is not None:
        st.session_state.points = loaded_points
    else:
        st.session_state.points = [(1, 0), (30, 0)]  # default with 30 days

# Step 1: Input Parameters
num_days = st.number_input("Number of Days", min_value=1, max_value=365, value=30)
total_money = st.number_input("Total Money to Save", min_value=1.0, value=1000.0)

max_daily_saving = total_money / num_days  # max saving per day

# Adjust points if num_days changed
# Remove points beyond num_days, add end point if missing
def adjust_points(points, max_day):
    points = [pt for pt in points if pt[0] <= max_day]
    days = [pt[0] for pt in points]
    if max_day not in days:
        points.append((max_day, 0))
    points = sorted(points, key=lambda x: x[0])
    return points

st.session_state.points = adjust_points(st.session_state.points, num_days)

st.subheader("Add Points")

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
    yaxis_title="Money Saved per Day",
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

if st.button("Add Point"):
    if (clicked_day, clicked_money) not in st.session_state.points:
        st.session_state.points.append((clicked_day, clicked_money))
        st.session_state.points = sorted(st.session_state.points, key=lambda x: x[0])
        save_points(st.session_state.points)
        st.rerun()

if st.button("Clear Points"):
    st.session_state.points = [(1, 0), (num_days, 0)]
    save_points(st.session_state.points)
    st.rerun()

if st.button("Reset Saved Plan"):
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
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

# Calculate adjustment per day to match total target sum
adjustment = (total_money - np.sum(raw_savings)) / num_days

# Add adjustment evenly across all days
final_savings_array = raw_savings + adjustment

# Display adjusted daily savings
st.subheader("Adjusted Daily Savings Plan")
df = pd.DataFrame({
    "Day": np.arange(1, num_days + 1),
    "Daily Savings": final_savings_array
})
st.line_chart(df.set_index("Day"))

# Assuming num_days and final_savings_array are already defined
st.subheader("Daily Savings Tracker")

df_display = pd.DataFrame({
    "Day": np.arange(1, num_days + 1),
    "Daily Savings": final_savings_array.round(2)
})

# Style: alternate row colors and format currency
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit import _get_option

# Detect dark mode
is_dark_mode = _get_option("theme.base") == "dark"

bg_color = "#1e1e1e" if is_dark_mode else "white"
text_color = "white" if is_dark_mode else "black"
header_bg = "#333333" if is_dark_mode else "#4CAF50"

def style_rows(row):
    return [f'background-color: {bg_color}; color: {text_color}' for _ in row]


styled_df =import plotly.graph_objects as go

def sierpinski_triangle(level=1):
    return [[(0, 0), (1, 0), (0.5, 0.866)]]

if "click_count" not in st.session_state:
    st.session_state.click_count = 0

st.subheader("Sierpiński Triangle – Level 1 z Licznikiem Kliknięć")

triangle_level1 = sierpinski_triangle(level=1)[0]
x = [p[0] for p in triangle_level1] + [triangle_level1[0][0]]
y = [p[1] for p in triangle_level1] + [triangle_level1[0][1]]

fig_tri = go.Figure()

fig_tri.add_trace(go.Scatter(
    x=x,
    y=y,
    fill='toself',
    line=dict(color='blue'),
    mode='lines',
    name='Clickable Triangle',
    hoverinfo='skip'
))

mid_x = sum(p[0] for p in triangle_level1) / 3
mid_y = sum(p[1] for p in triangle_level1) / 3

fig_tri.add_trace(go.Scatter(
    x=[mid_x],
    y=[mid_y],
    mode='text',
    text=[f"{st.session_state.click_count}"],
    textfont=dict(size=24, color="black"),
    showlegend=False
))

fig_tri.update_layout(
    xaxis=dict(visible=False, range=[-0.1, 1.1]),
    yaxis=dict(visible=False, scaleanchor='x', scaleratio=1, range=[-0.1, 1]),
    margin=dict(t=20, b=20, l=20, r=20),
    height=400
)

st.plotly_chart(fig_tri, use_container_width=True)

if st.button("Kliknij trójkąt"):
    st.session_state.click_count += 1
    st.experimental_rerun()
 (
    df_display.style
    .apply(style_rows, axis=1)
    .format({"Daily Savings": "${:.2f}"})  # Format currency
    .set_table_styles([
        {"selector": "th", "props": [("background-color", header_bg), ("color", "white" if is_dark_mode else "white"), ("font-weight", "bold")]},
        {"selector": "td", "props": [("background-color", bg_color), ("color", text_color), ("text-align", "center"), ("padding", "8px")]},
        {"selector": "table", "props": [("border-collapse", "collapse"), ("width", "100%")]},
    ])
    .set_properties(**{"max-height": "400px", "overflow-y": "auto", "display": "block"})
)

st.write(styled_df)

def sierpinski_triangle(level=1):
    # zwraca listę współrzędnych trójkątów, na razie tylko jeden trójkąt
    return [[(0, 0), (1, 0), (0.5, 0.866)]]

