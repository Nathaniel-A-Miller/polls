import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Page layout ---
st.set_page_config(layout="wide")
st.title("Trump Poll Average Dashboard")

# --- Information box ---
st.info(
    "Mobile users: click on the double carrot >> on the upper left-hand side of your screen "
    "to expand the poll selection checkbox menu. The exponential smoothing selector is at the bottom of that list."
)

# --- Load CSV automatically ---
df = pd.read_csv("polls.csv")

# Ensure necessary columns
required_cols = {"pollster", "date", "Approve"}
if not required_cols.issubset(df.columns):
    st.error(f"CSV must contain columns: {', '.join(required_cols)}")
    st.stop()

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# --- Sidebar: pollster selection ---
pollsters = sorted(df["pollster"].unique())

st.sidebar.markdown("### Select polls to include:")

# Use checkboxes so all pollsters are always visible
selected_pollsters_dict = {}
for poll in pollsters:
    selected_pollsters_dict[poll] = st.sidebar.checkbox(poll, value=True)

# Build list of selected pollsters
selected_pollsters = [poll for poll, selected in selected_pollsters_dict.items() if selected]

# Filter data based on selection
filtered_df = df[df["pollster"].isin(selected_pollsters)]

# --- Exponential smoothing ---
daily_avg = (
    filtered_df.groupby("date")["Approve"]
    .mean()
    .reset_index(name="average")
    .sort_values("date")
)

# Smoothing span slider
span_value = st.sidebar.slider("Smoothing span (higher = smoother)", min_value=2, max_value=20, value=5)
daily_avg["smoothed"] = daily_avg["average"].ewm(span=span_value, adjust=False).mean()

# --- Plot ---
fig, ax = plt.subplots(figsize=(12, 6))

# Plot each pollster as faint dashed line
for poll in selected_pollsters:
    sub = filtered_df[filtered_df["pollster"] == poll]
    ax.plot(sub["date"], sub["Approve"], linestyle="--", alpha=0.4, label=poll)

# Plot raw average as thin red line
ax.plot(daily_avg["date"], daily_avg["average"], color="red", linewidth=1.5, label="Average")

# Plot smoothed average as thick blue line
ax.plot(daily_avg["date"], daily_avg["smoothed"], color="blue", linewidth=2.5, label="Smoothed Average")

ax.set_title("Trump Approval Polling Average")
ax.set_xlabel("Date")
ax.set_ylabel("Approve %")
ax.grid(True)

# External legend
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

st.pyplot(fig)

# Optional: show filtered data
with st.expander("Show filtered data"):
    st.dataframe(filtered_df)
