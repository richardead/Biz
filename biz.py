import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os

st.title("Budget Planner – Daily Savings")

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

st.subheader("Daily Savings Tracker")

df_display = pd.DataFrame({
    "Day": np.arange(1, num_days + 1),
    "Daily Savings (Zloty)": final_savings_array.round(2)
})

# Style: alternate row colors and format currency
def style_rows(row):
    return ['background-color: #000000' for _ in row]

styled_df = (
    df_display.style
    .apply(style_rows, axis=1)
    .format({"Daily Savings (Zloty)": "{:.2f}"})
    .set_table_styles([
        {"selector": "th", "props": [("background-color", "#4CAF50"), ("color", "white"), ("font-weight", "bold")]},
        {"selector": "td", "props": [("text-align", "center")]},
    ])
    .set_properties(**{"max-height": "400px", "overflow-y": "auto", "display": "block"})
)

st.write(styled_df)

st.markdown(f"**Total Saved:** {final_savings_array.sum():.2f} Zloty (Target: {total_money})")\

import math
import plotly.express as px

st.subheader("Fibonacci Spiral Zoom")

if "fib_zoom" not in st.session_state:
    st.session_state.fib_zoom = 0

if st.button("Zoom Fibonacci Spiral"):
    st.session_state.fib_zoom += 1

# Fibonacci square spiral logic
def generate_fib_squares(n):
    fib = [1, 1]
    for _ in range(n - 2):
        fib.append(fib[-1] + fib[-2])
    return fib

def get_spiral_squares(fib, zoom_level, savings):
    squares = []
    angle = 0
    x, y = 0, 0

    for i in range(zoom_level, zoom_level + 4):
        size = fib[i % len(fib)]
        dx = size * math.cos(math.radians(angle))
        dy = size * math.sin(math.radians(angle))
        squares.append({
            "x": x,
            "y": y,
            "size": size,
            "day": (i % len(savings)) + 1,
            "savings": round(savings[i % len(savings)], 2)
        })
        x += dx
        y += dy
        angle += 90
    return squares

if len(final_savings_array) >= 4:
    fib = generate_fib_squares(20)
    zoom_index = st.session_state.fib_zoom % 16
    squares = get_spiral_squares(fib, zoom_index, final_savings_array)

    spiral_fig = go.Figure()

    for s in squares:
        spiral_fig.add_shape(
            type="rect",
            x0=s["x"], y0=s["y"],
            x1=s["x"] + s["size"], y1=s["y"] + s["size"],
            line=dict(color="blue")
        )
        spiral_fig.add_annotation(
            x=s["x"] + s["size"] / 2,
            y=s["y"] + s["size"] / 2,
            text=f"Day {s['day']}<br>{s['savings']} zł",
            showarrow=False,
            font=dict(size=10, color="black"),
            xanchor="center", yanchor="middle"
        )

    spiral_fig.update_layout(
        title="Fibonacci Spiral Zoom View",
        showlegend=False,
        width=600,
        height=600,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )

    st.plotly_chart(spiral_fig)
else:
    st.info("Not enough data for Fibonacci spiral. Add more days.")


#streamlit
#numpy
#pandas
#plotly
