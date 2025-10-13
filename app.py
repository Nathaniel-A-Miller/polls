import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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
span_value = st.sidebar.slider(
    "Smoothing span (higher = smoother)", min_value=2, max_value=20, value=5
)
daily_avg["smoothed"] = daily_avg["average"].ewm(span=span_value, adjust=False).mean()

# --- Plotly figure ---
fig = go.Figure()

# Plot each pollster as faint dashed line
for poll in selected_pollsters:
    sub = filtered_df[filtered_df["pollster"] == poll]
    fig.add_trace(
        go.Scatter(
            x=sub["date"],
            y=sub["Approve"],
            mode="lines",
            name=poll,
            line=dict(dash="dot", width=1),
            opacity=0.4,
            hoverinfo="x+y+name",
        )
    )

# Plot raw average as thin red line
fig.add_trace(
    go.Scatter(
        x=daily_avg["date"],
        y=daily_avg["average"],
        mode="lines",
        name="Average",
        line=dict(color="red", width=2),
        hoverinfo="x+y+name",
    )
)

# Plot smoothed average as thick blue line
fig.add_trace(
    go.Scatter(
        x=daily_avg["date"],
        y=daily_avg["smoothed"],
        mode="lines",
        name="Smoothed Average",
        line=dict(color="blue", width=3),
        hoverinfo="x+y+name",
    )
)

# Update layout
fig.update_layout(
    title="Trump Approval Polling Average",
    xaxis_title="Date",
    yaxis_title="Approve %",
    hovermode="x unified",
    legend=dict(
        y=0.5,
        x=1.05,
        xanchor="left",
        yanchor="middle",
        bordercolor="LightGray",
        borderwidth=1,
    ),
    margin=dict(l=50, r=150, t=80, b=50),
)

# Display interactive Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Optional: show filtered data
with st.expander("Show filtered data"):
    st.dataframe(filtered_df)
