import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Page layout ---
st.set_page_config(layout="wide")
st.title("Trump Poll Average Dashboard")

# --- Load CSV automatically ---
df = pd.read_csv("polls.csv")

# Ensure necessary columns
required_cols = {"pollster", "date", "Approve"}
if not required_cols.issubset(df.columns):
    st.error(f"CSV must contain columns: {', '.join(required_cols)}")
    st.stop()

# Convert date column to datetime (already a single date)
df["date"] = pd.to_datetime(df["date"])

# --- Sidebar: pollster selection ---
# Inject CSS to make multiselect taller
st.markdown(
    """
    <style>
    .css-1siy2j7 {
        max-height: 400px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

pollsters = sorted(df["pollster"].unique())
selected_pollsters = st.sidebar.multiselect(
    "Select pollsters to include:",
    pollsters,
    default=pollsters
)

# Filter data based on selection
filtered_df = df[df["pollster"].isin(selected_pollsters)]

# --- Compute daily average and apply exponential smoothing ---
daily_avg = (
    filtered_df.groupby("date")["Approve"]
    .mean()
    .reset_index(name="average")
    .sort_values("date")
)

# Exponential smoothing (span controls smoothness)
span_value = st.sidebar.slider("Smoothing span (higher = smoother)", min_value=2, max_value=20, value=5)
daily_avg["smoothed"] = daily_avg["average"].ewm(span=span_value, adjust=False).mean()

# --- Plot ---
fig, ax = plt.subplots(figsize=(12, 6))

# Plot each pollster as a faint dashed line
for poll in selected_pollsters:
    sub = filtered_df[filtered_df["pollster"] == poll]
    ax.plot(sub["date"], sub["Approve"], linestyle="--", alpha=0.4, label=poll)

# Plot raw average as thin line
ax.plot(daily_avg["date"], daily_avg["average"], color="red", linewidth=1.5, label="Average")

# Plot smoothed average as thick line
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
