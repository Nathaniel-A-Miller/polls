import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Page layout ---
st.set_page_config(layout="wide")
st.title("Trump Poll Average Dashboard")

# --- Information box ---
st.info(
    "Mobile users: click on the double carrot >> on the upper-left-hand side of your screen "
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

best_ranked_pollsters = [
    "NY Times/Siena",
    "SurveyUSA",
    "Marquette",
    "Atlas Intel",
    "Cygnal",
    "I&I/TIPP",
    "Emerson",
    "CBS News",
    "Quinnipiac",
    "University of Connecticut",
    "YouGov",
    "Elon University",
]

st.sidebar.markdown("### Select polls to include:")

# Initialize dictionary for checkbox states
if "selected_pollsters_dict" not in st.session_state:
    st.session_state.selected_pollsters_dict = {poll: True for poll in pollsters}

# Sidebar buttons
col1, col2, col3 = st.sidebar.columns(3)
if col1.button("Select all"):
    st.session_state.selected_pollsters_dict = {poll: True for poll in pollsters}
if col2.button("Deselect all"):
    st.session_state.selected_pollsters_dict = {poll: False for poll in pollsters}
if col3.button("538 Best-ranked pollsters"):
    st.session_state.selected_pollsters_dict = {poll: (poll in best_ranked_pollsters) for poll in pollsters}

# Display checkboxes
for poll in pollsters:
    st.session_state.selected_pollsters_dict[poll] = st.sidebar.checkbox(
        poll, value=st.session_state.selected_pollsters_dict.get(poll, True)
    )

# Build list of selected pollsters
selected_pollsters = [poll for poll, selected in st.session_state.selected_pollsters_dict.items() if selected]

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
