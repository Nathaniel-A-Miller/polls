import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# --- Best-ranked pollsters ---
best_ranked_pollsters = [
    "Ipsos",
    "Reuters/Ipsos",
    "NBC News",
    "FOX News",
    "Wall Street Journal",
    "IBD/TIPP",
    "Gallup",
    "Wash Post/Ipsos",
    "TIPP",
    "Economist/YouGov",
    "ABC/Wash Post/Ipsos",
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

# --- Page layout ---
st.set_page_config(layout="wide")
st.title("Trump Poll Average Dashboard")

# --- Information box ---
st.info(
    "Mobile users: please click on the double angle brackets (>>) on the upper-left-hand side of your screen "
    "to expand the poll selection checkbox menu. The exponential smoothing selector is at the bottom of that list."
)

# --- Load CSV ---
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

# Initialize session state
if "select_all" not in st.session_state:
    st.session_state["select_all"] = False
if "best538" not in st.session_state:
    st.session_state["best538"] = True

# --- Sidebar buttons stacked vertically ---
if st.sidebar.button("Select All"):
    st.session_state["select_all"] = True
    st.session_state["best538"] = False

if st.sidebar.button("Deselect All"):
    st.session_state["select_all"] = False
    st.session_state["best538"] = False

if st.sidebar.button("538 Best pollsters¹"):
    st.session_state["select_all"] = False
    st.session_state["best538"] = True

# --- Checkbox list ---
selected_pollsters_dict = {}
for poll in pollsters:
    if st.session_state["best538"]:
        default = poll in best_ranked_pollsters
    else:
        default = st.session_state["select_all"]
    selected_pollsters_dict[poll] = st.sidebar.checkbox(poll, value=default)

# List of pollsters currently selected
selected_pollsters = [poll for poll, selected in selected_pollsters_dict.items() if selected]

# Filter data based on selection
filtered_df = df[df["pollster"].isin(selected_pollsters)]

# --- Exponential smoothing ---
span_value = st.sidebar.slider(
    "Smoothing span (higher = smoother)", min_value=2, max_value=20, value=10
)

# Approval averages
daily_avg_approve = (
    filtered_df.groupby("date")["Approve"]
    .mean()
    .reset_index(name="average")
    .sort_values("date")
)
daily_avg_approve["smoothed"] = daily_avg_approve["average"].ewm(span=span_value, adjust=False).mean()

# Disapproval averages
daily_avg_disapprove = (
    filtered_df.groupby("date")["Disapprove"]
    .mean()
    .reset_index(name="average")
    .sort_values("date")
)
daily_avg_disapprove["smoothed"] = daily_avg_disapprove["average"].ewm(span=span_value, adjust=False).mean()

# --- Compute latest averages ---
latest_date = daily_avg_approve["date"].max()
latest_approve = daily_avg_approve.loc[daily_avg_approve["date"] == latest_date, "smoothed"].values[0]
latest_disapprove = daily_avg_disapprove.loc[daily_avg_disapprove["date"] == latest_date, "smoothed"].values[0]

# --- Display latest values in color ---
st.markdown(
    f"""
    <div style='text-align:center;'>
        <h4>Most Recent Smoothed Averages</h4>
        <div style='display:flex; justify-content:center; gap:80px;'>
            <div style='color:blue; font-size:24px;'>
                <b>Approval:</b> {latest_approve:.1f}%
            </div>
            <div style='color:red; font-size:24px;'>
                <b>Disapproval:</b> {latest_disapprove:.1f}%
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --- Plotly figure ---
fig = go.Figure()

# Individual pollster lines for approval (faint dashed)
for poll in selected_pollsters:
    sub = filtered_df[filtered_df["pollster"] == poll]
    fig.add_trace(
        go.Scatter(
            x=sub["date"],
            y=sub["Approve"],
            mode="lines",
            name=f"{poll} Approve",
            line=dict(dash="dot", width=1),
            opacity=0.6,
            hoverinfo="x+y+name",
        )
    )
    # Optional: pollster disapproval lines (also faint dashed)
    fig.add_trace(
        go.Scatter(
            x=sub["date"],
            y=sub["Disapprove"],
            mode="lines",
            name=f"{poll} Disapprove",
            line=dict(dash="dot", width=1, color="red"),
            opacity=0.6,
            hoverinfo="x+y+name",
        )
    )

# Smoothed averages
fig.add_trace(
    go.Scatter(
        x=daily_avg_approve["date"],
        y=daily_avg_approve["smoothed"],
        mode="lines",
        name="Smoothed Approval",
        line=dict(color="blue", width=3),
        hoverinfo="x+y+name",
    )
)
fig.add_trace(
    go.Scatter(
        x=daily_avg_disapprove["date"],
        y=daily_avg_disapprove["smoothed"],
        mode="lines",
        name="Smoothed Disapproval",
        line=dict(color="red", width=3),
        hoverinfo="x+y+name",
    )
)

# Layout
fig.update_layout(
    title="Trump Approval and Disapproval Polling Average",
    xaxis_title="Date",
    yaxis_title="Percentage",
    hovermode="x unified",
    height=700,
    legend=dict(
        orientation="h",
        y=-0.3,
        x=0.5,
        xanchor="center",
        yanchor="top",
        bordercolor="LightGray",
        borderwidth=1,
    ),
    margin=dict(l=50, r=50, t=80, b=120),
)

# Display chart
st.plotly_chart(fig, use_container_width=True)

# Foonote on "538 Best Pollsters" button
st.write("¹ [FiveThirtyEight Pollster Ratings](https://github.com/fivethirtyeight/data/blob/master/pollster-ratings/2023/pollster-ratings.csv)")

# Last updated

def get_last_updated(repo_owner, repo_name, file_path):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    params = {"path": file_path, "page": 1, "per_page": 1}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None, "Unknown" # Return None for data and "Unknown" for formatted date

        commit_date = data[0]["commit"]["committer"]["date"]
        dt = datetime.fromisoformat(commit_date.replace("Z", "+00:00")).astimezone(ZoneInfo("UTC"))
        formatted_date = dt.strftime("%B %d, %Y, %H:%M %Z")
        return data, formatted_date # Return both data and formatted date

    except requests.RequestException as e:
        print("Request failed:", e)
        return None, "Unknown"

# Call the function to get the data and formatted date
data, last_updated = get_last_updated("Nathaniel-A-Miller", "polls", "polls.csv")

# Check if data was successfully retrieved before attempting to parse
if data:
    commit_date = data[0]["commit"]["committer"]["date"]
    dt = datetime.fromisoformat(commit_date.replace("Z", "+00:00")).astimezone(ZoneInfo("UTC"))
    st.write("Data last updated:", dt.strftime("%B %d, %Y, %H:%M %Z"))
else:
    st.write("Could not retrieve commit data.")

# Optional: show filtered data
with st.expander("Show filtered data"):
    st.dataframe(filtered_df)
