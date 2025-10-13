import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- Load data ---
st.title("Trump Poll Average Dashboard")

# Load CSV automatically from the repo
df = pd.read_csv("polls.csv")

# Ensure necessary columns
required_cols = {"pollster", "date", "Approve"}
if not required_cols.issubset(df.columns):
    st.error(f"CSV must contain columns: {', '.join(required_cols)}")
    st.stop()

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# --- Sidebar pollster selection ---
pollsters = sorted(df["pollster"].unique())
selected_pollsters = st.sidebar.multiselect(
    "Select pollsters to include:",
    pollsters,
    default=pollsters
)

# --- Filter data based on selection ---
filtered_df = df[df["pollster"].isin(selected_pollsters)]

# --- Compute daily average ---
daily_avg = (
    filtered_df.groupby("date")["Approve"]
    .mean()
    .reset_index(name="average")
    .sort_values("date")
)

# --- Plot ---
fig, ax = plt.subplots(figsize=(10, 5))

# Plot each pollster as a faint dashed line
for poll in selected_pollsters:
    sub = filtered_df[filtered_df["pollster"] == poll]
    ax.plot(sub["date"], sub["Approve"], linestyle="--", alpha=0.4, label=poll)

# Plot average as a thick red line
ax.plot(daily_avg["date"], daily_avg["average"], color="red", linewidth=2.5, label="Average")

ax.set_title("Trump Approval Polling Average")
ax.set_xlabel("Date")
ax.set_ylabel("Approve %")
ax.grid(True)

# Move legend outside to the right
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

st.pyplot(fig)

# Optional: show filtered data
with st.expander("Show filtered data"):
    st.dataframe(filtered_df)
