import os
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="World Cup Pool Dashboard",
    page_icon="🏆",
    layout="wide"
)

DATA_DIR = "data"
PREDICTIONS_FILE = os.path.join(DATA_DIR, "predictions.csv")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.csv")

GROUP_STAGE = "Group stage"

GROUP_POINTS = {
    "win": 3,
    "draw": 1,
    "loss": 0
}

KNOCKOUT_POINTS = {
    "Round of 32": 4,
    "Round of 16": 6,
    "Quarter-finals": 8,
    "Semi-finals": 10,
    "Third-place match": 12,
    "Final": 15,
    "Champion": 15
}

STAGE_ORDER = [
    "Group stage",
    "Round of 32",
    "Round of 16",
    "Quarter-finals",
    "Semi-finals",
    "Third-place match",
    "Final"
]

REQUIRED_PREDICTION_COLUMNS = ["player", "team"]
REQUIRED_MATCH_COLUMNS = [
    "date", "time", "stage", "group",
    "home_team", "away_team", "home_goals", "away_goals"
]

st.markdown(
    """
    <style>
    .main {background-color: #f7f7f4;}

    .title-card {
        background: linear-gradient(135deg, #14532d, #166534, #22c55e);
        padding: 26px;
        border-radius: 22px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.12);
    }

    .title-card h1 {
        color: white;
        margin-bottom: 4px;
        font-size: 42px;
    }

    .title-card p {
        color: #ecfdf5;
        font-size: 17px;
        margin: 0;
    }

    .metric-card {
        background-color: white;
        padding: 18px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        min-height: 98px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #166534;
        line-height: 1.15;
        word-break: break-word;
    }

    .metric-label {
        font-size: 13px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 6px;
    }

    .day-title {
        background-color: #111827;
        color: white;
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 8px;
    }

    .player-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }

    .player-name {
        font-size: 22px;
        font-weight: 800;
        color: #14532d;
        margin-bottom: 6px;
    }

    .small-note {
        color: #6b7280;
        font-size: 13px;
    }

    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def create_default_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(PREDICTIONS_FILE):
        pd.DataFrame(columns=REQUIRED_PREDICTION_COLUMNS).to_csv(PREDICTIONS_FILE, index=False)

    if not os.path.exists(MATCHES_FILE):
        pd.DataFrame(columns=REQUIRED_MATCH_COLUMNS).to_csv(MATCHES_FILE, index=False)


@st.cache_data
def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def clean_team_name(value):
    return clean_text(value)


def clean_stage(value):
    return clean_text(value)


def validate_columns(df, required_columns, file_name):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"{file_name} is missing required columns: {', '.join(missing)}")
        st.stop()


def score_is_available(row):
    home = clean_text(row.get("home_goals", ""))
    away = clean_text(row.get("away_goals", ""))

    if home == "" or away == "":
        return False

    try:
        int(float(home))
        int(float(away))
        return True
    except Exception:
        return False


def get_result_from_match(row):
    if not score_is_available(row):
        return []

    home_team = clean_team_name(row["home_team"])
    away_team = clean_team_name(row["away_team"])
    home_score = int(float(row["home_goals"]))
    away_score = int(float(row["away_goals"]))
    stage = clean_stage(row["stage"])

    if home_score > away_score:
        return [
            {
                "date": row["date"],
                "stage": stage,
                "team": home_team,
                "result": "win",
                "opponent": away_team,
                "goals_for": home_score,
                "goals_against": away_score
            },
            {
                "date": row["date"],
                "stage": stage,
                "team": away_team,
                "result": "loss",
                "opponent": home_team,
                "goals_for": away_score,
                "goals_against": home_score
            }
        ]

    if home_score < away_score:
        return [
            {
                "date": row["date"],
                "stage": stage,
                "team": home_team,
                "result": "loss",
                "opponent": away_team,
                "goals_for": home_score,
                "goals_against": away_score
            },
            {
                "date": row["date"],
                "stage": stage,
                "team": away_team,
                "result": "win",
                "opponent": home_team,
                "goals_for": away_score,
                "goals_against": home_score
            }
        ]

    return [
        {
            "date": row["date"],
            "stage": stage,
            "team": home_team,
            "result": "draw",
            "opponent": away_team,
            "goals_for": home_score,
            "goals_against": away_score
        },
        {
            "date": row["date"],
            "stage": stage,
            "team": away_team,
            "result": "draw",
            "opponent": home_team,
            "goals_for": away_score,
            "goals_against": home_score
        }
    ]


def build_results_from_matches(matches):
    rows = []

    if matches.empty:
        return pd.DataFrame(columns=[
            "date", "stage", "team", "result",
            "opponent", "goals_for", "goals_against"
        ])

    for _, row in matches.iterrows():
        rows.extend(get_result_from_match(row))

    return pd.DataFrame(rows)


def points_for_team_result(row):
    stage = clean_stage(row["stage"])
    result = clean_text(row["result"]).lower()

    if stage == GROUP_STAGE:
        return GROUP_POINTS.get(result, 0)

    if stage in KNOCKOUT_POINTS:
        if result == "win":
            return KNOCKOUT_POINTS[stage]
        return 0

    return 0


def compute_team_scores(matches):
    results = build_results_from_matches(matches)

    if results.empty:
        return pd.DataFrame(columns=[
            "team",
            "group_points",
            "knockout_points",
            "team_total_points",
            "last_date",
            "last_stage",
            "last_result"
        ])

    results["points"] = results.apply(points_for_team_result, axis=1)
    results["group_points"] = results.apply(
        lambda row: row["points"] if row["stage"] == GROUP_STAGE else 0,
        axis=1
    )
    results["knockout_points"] = results.apply(
        lambda row: row["points"] if row["stage"] != GROUP_STAGE else 0,
        axis=1
    )

    scores = (
        results
        .groupby("team", as_index=False)
        .agg(
            group_points=("group_points", "sum"),
            knockout_points=("knockout_points", "sum")
        )
    )

    scores["team_total_points"] = scores["group_points"] + scores["knockout_points"]

    last_results = results.copy()
    last_results["date_dt"] = pd.to_datetime(last_results["date"], errors="coerce")
    last_results = last_results.sort_values(["team", "date_dt", "stage"])

    last_status = (
        last_results
        .drop_duplicates(subset=["team"], keep="last")
        [["team", "date", "stage", "result"]]
        .rename(columns={
            "date": "last_date",
            "stage": "last_stage",
            "result": "last_result"
        })
    )

    return scores.merge(last_status, on="team", how="left")


def add_dense_positions(ranking):
    if ranking.empty:
        ranking.insert(0, "position", [])
        return ranking

    unique_scores = (
        ranking[["total_points"]]
        .drop_duplicates()
        .sort_values("total_points", ascending=False)
        .reset_index(drop=True)
    )
    unique_scores["position"] = unique_scores.index + 1
    score_to_position = dict(zip(unique_scores["total_points"], unique_scores["position"]))
    ranking.insert(0, "position", ranking["total_points"].map(score_to_position).astype(int))
    return ranking


def compute_ranking_and_predictions(predictions, matches):
    predictions = predictions.copy()
    predictions["player"] = predictions["player"].apply(clean_text)
    predictions["team"] = predictions["team"].apply(clean_team_name)

    players = (
        pd.DataFrame({"player": sorted(predictions["player"].dropna().unique())})
        .reset_index(drop=True)
    )

    team_scores = compute_team_scores(matches)
    scored_predictions = predictions.merge(team_scores, on="team", how="left")

    score_columns = ["group_points", "knockout_points", "team_total_points"]
    for col in score_columns:
        scored_predictions[col] = scored_predictions[col].fillna(0).astype(int)

    for col in ["last_date", "last_stage", "last_result"]:
        scored_predictions[col] = scored_predictions[col].fillna("")

    ranking = (
        scored_predictions
        .groupby("player", as_index=False)
        .agg(
            group_points=("group_points", "sum"),
            knockout_points=("knockout_points", "sum"),
            total_points=("team_total_points", "sum"),
            selected_teams=("team", "count")
        )
    )

    ranking = players.merge(ranking, on="player", how="left")

    for col in ["group_points", "knockout_points", "total_points", "selected_teams"]:
        ranking[col] = ranking[col].fillna(0).astype(int)

    ranking = ranking.sort_values(
        ["total_points", "knockout_points", "group_points", "player"],
        ascending=[False, False, False, True]
    ).reset_index(drop=True)

    ranking = add_dense_positions(ranking)

    return ranking, scored_predictions, team_scores


def format_match_score(row):
    if clean_text(row["home_goals"]) == "" or clean_text(row["away_goals"]) == "":
        return ""
    return f"{int(float(row['home_goals']))} - {int(float(row['away_goals']))}"


def make_matches_by_day(matches):
    if matches.empty:
        return {}

    df = matches.copy()
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(["date_dt", "time", "home_team"])

    days = {}

    for date_dt, df_day in df.groupby("date_dt"):
        if pd.isna(date_dt):
            continue

        day_label = date_dt.strftime("%d %b")

        table = df_day[[
            "time", "stage", "group", "home_team",
            "home_goals", "away_goals", "away_team"
        ]].copy()

        table["score"] = table.apply(format_match_score, axis=1)
        table = table[["time", "stage", "group", "home_team", "score", "away_team"]]
        table.columns = ["Time", "Stage", "Group", "Team 1", "Score", "Team 2"]

        days[day_label] = table

    return days


def prepare_matches_for_editor(matches):
    df = matches.copy()

    for col in REQUIRED_MATCH_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[REQUIRED_MATCH_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date

    for col in ["time", "stage", "group", "home_team", "away_team"]:
        df[col] = df[col].fillna("").astype(str)

    df["home_goals"] = pd.to_numeric(df["home_goals"], errors="coerce").astype("Int64")
    df["away_goals"] = pd.to_numeric(df["away_goals"], errors="coerce").astype("Int64")

    return df


def prepare_matches_for_calculation(matches):
    df = matches.copy()

    for col in REQUIRED_MATCH_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df = df[REQUIRED_MATCH_COLUMNS].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["date"] = df["date"].fillna("")

    for col in ["time", "stage", "group", "home_team", "away_team"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    for col in ["home_goals", "away_goals"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].apply(lambda value: "" if pd.isna(value) else int(value))

    return df.sort_values(["date", "time", "stage", "home_team"]).reset_index(drop=True)


def table_height(df, row_height=35, header_height=38, max_height=900):
    height = header_height + row_height * max(len(df), 1)
    return min(height, max_height)


def style_ranking(df):
    return (
        df.style
        .background_gradient(subset=["Total points"], cmap="Greens")
        .format({
            "Group points": "{:.0f}",
            "Knockout points": "{:.0f}",
            "Total points": "{:.0f}",
            "Selected teams": "{:.0f}"
        })
    )


def style_player_table(df):
    def color_result(value):
        value = str(value).lower()
        if value == "win":
            return "background-color: #bbf7d0; color: #14532d; font-weight: 700;"
        if value == "draw":
            return "background-color: #fef3c7; color: #92400e; font-weight: 700;"
        if value == "loss":
            return "background-color: #fecaca; color: #991b1b; font-weight: 700;"
        return ""

    return (
        df.style
        .map(color_result, subset=["Last result"])
        .background_gradient(subset=["Total"], cmap="Greens")
        .format({
            "Group points": "{:.0f}",
            "Knockout points": "{:.0f}",
            "Total": "{:.0f}"
        })
    )


def style_team_scores(df):
    return (
        df.style
        .background_gradient(subset=["Total points"], cmap="Greens")
        .format({
            "Group points": "{:.0f}",
            "Knockout points": "{:.0f}",
            "Total points": "{:.0f}"
        })
    )


def display_metric_card(value, label):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def make_leader_summary(ranking):
    if ranking.empty:
        return "-", "0 pts"

    top_score = int(ranking["total_points"].max())
    leaders = ranking.loc[ranking["total_points"] == top_score, "player"].tolist()

    if len(leaders) <= 3:
        leader_text = ", ".join(leaders)
    else:
        leader_text = f"{len(leaders)} tied leaders"

    points_text = f"{top_score} pt" if top_score == 1 else f"{top_score} pts"
    return leader_text, points_text


create_default_files()

predictions = load_csv(PREDICTIONS_FILE)
matches_from_file = load_csv(MATCHES_FILE)

validate_columns(predictions, REQUIRED_PREDICTION_COLUMNS, PREDICTIONS_FILE)
validate_columns(matches_from_file, REQUIRED_MATCH_COLUMNS, MATCHES_FILE)

if "edited_matches" not in st.session_state:
    st.session_state.edited_matches = prepare_matches_for_calculation(matches_from_file)

matches = st.session_state.edited_matches.copy()

st.markdown(
    """
    <div class="title-card">
        <h1>🏆 World Cup Pool Dashboard</h1>
        <p>Track match results, player rankings, team points, and predictions in one place.</p>
    </div>
    """,
    unsafe_allow_html=True
)

if predictions.empty:
    st.error("data/predictions.csv is empty or could not be found.")
    st.stop()

if matches.empty:
    st.error("data/matches.csv is empty or could not be found.")
    st.stop()

ranking, scored_predictions, team_scores = compute_ranking_and_predictions(predictions, matches)

n_players = predictions["player"].nunique()
n_teams = predictions["team"].nunique()
n_matches = len(matches)
n_finished = matches.apply(score_is_available, axis=1).sum()
leader_text, leader_points = make_leader_summary(ranking)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    display_metric_card(n_players, "Players")
with col2:
    display_metric_card(n_teams, "Selected teams")
with col3:
    display_metric_card(n_matches, "Matches")
with col4:
    display_metric_card(n_finished, "Completed matches")
with col5:
    display_metric_card(leader_text, f"Leader: {leader_points}")

st.markdown("")

tab_ranking, tab_update, tab_matches, tab_players, tab_teams, tab_rules, tab_files = st.tabs([
    "🏅 Ranking",
    "✏️ Update results",
    "📅 Matches",
    "📝 Predictions",
    "🌍 Teams",
    "📌 Rules",
    "📂 Files"
])

with tab_ranking:
    st.subheader("🏅 Overall ranking")
    last_update = datetime.now(ZoneInfo("Europe/Rome")).strftime("%d/%m/%y %H:%M")
    st.caption(f"Update: {last_update}")

    ranking_show = ranking.rename(columns={
        "position": "Position",
        "player": "Player",
        "group_points": "Group points",
        "knockout_points": "Knockout points",
        "total_points": "Total points",
        "selected_teams": "Selected teams"
    })

    st.dataframe(
        style_ranking(ranking_show),
        use_container_width=True,
        hide_index=True,
        height=table_height(ranking_show)
    )

    st.markdown("### Total points by player")

    chart_df = ranking.sort_values("total_points", ascending=True).copy()
    fig = px.bar(
        chart_df,
        x="total_points",
        y="player",
        orientation="h",
        text="total_points",
        labels={"total_points": "Total points", "player": "Player"},
        height=max(360, 34 * len(chart_df))
    )
    fig.update_traces(marker_color="#f2b705", textposition="outside")
    fig.update_layout(
        margin=dict(l=10, r=40, t=10, b=10),
        xaxis_title="Total points",
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_update:
    st.subheader("✏️ Update match results")

    st.info(
        "Edits made here update the dashboard during the current session only. "
        "Download the updated CSV and replace data/matches.csv in GitHub to make changes permanent online."
    )

    editor_df = prepare_matches_for_editor(matches)

    edited_matches = st.data_editor(
        editor_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "date": st.column_config.DateColumn("Date"),
            "time": st.column_config.TextColumn("Time"),
            "stage": st.column_config.SelectboxColumn("Stage", options=STAGE_ORDER),
            "group": st.column_config.TextColumn("Group"),
            "home_team": st.column_config.TextColumn("Team 1"),
            "away_team": st.column_config.TextColumn("Team 2"),
            "home_goals": st.column_config.NumberColumn("Goals team 1", min_value=0, step=1, format="%d"),
            "away_goals": st.column_config.NumberColumn("Goals team 2", min_value=0, step=1, format="%d")
        },
        key="matches_editor"
    )

    matches_to_download = prepare_matches_for_calculation(edited_matches)

    col_apply, col_reload, col_download = st.columns([1, 1, 1])
    with col_apply:
        if st.button("Apply changes"):
            st.session_state.edited_matches = matches_to_download
            st.success("Changes applied to this session.")
            st.rerun()
    with col_reload:
        if st.button("Reset from CSV"):
            st.session_state.edited_matches = prepare_matches_for_calculation(matches_from_file)
            st.rerun()
    with col_download:
        st.download_button(
            "Download updated matches.csv",
            data=matches_to_download.to_csv(index=False).encode("utf-8"),
            file_name="matches.csv",
            mime="text/csv"
        )

    st.markdown("### Results interpreted by the dashboard")
    interpreted_results = build_results_from_matches(matches_to_download)

    if interpreted_results.empty:
        st.warning("No complete match result was found yet.")
    else:
        st.dataframe(interpreted_results, use_container_width=True, hide_index=True)

with tab_matches:
    st.subheader("📅 Matches by day")

    days = make_matches_by_day(matches)

    if not days:
        st.info("No matches available.")
    else:
        selected_days = st.multiselect(
            "Select days to display",
            list(days.keys()),
            default=list(days.keys())
        )

        for day in selected_days:
            st.markdown(f"<div class='day-title'>📅 {day}</div>", unsafe_allow_html=True)
            st.dataframe(days[day], use_container_width=True, hide_index=True)

with tab_players:
    st.subheader("📝 Predictions by player")

    player_names = sorted(scored_predictions["player"].unique())

    selected_players = st.multiselect(
        "Select players to display",
        player_names,
        default=player_names
    )

    for player in selected_players:
        total_row = ranking.loc[ranking["player"] == player, "total_points"]
        total_player = int(total_row.iloc[0]) if not total_row.empty else 0

        st.markdown(
            f"""
            <div class="player-card">
                <div class="player-name">{player}</div>
                <div class="small-note">Current total: <b>{total_player}</b> points</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        df_player = scored_predictions.loc[scored_predictions["player"] == player].copy()
        df_show = df_player[[
            "team", "last_stage", "last_result",
            "group_points", "knockout_points", "team_total_points"
        ]].copy()

        df_show.columns = [
            "Team", "Last stage", "Last result",
            "Group points", "Knockout points", "Total"
        ]

        df_show = df_show.sort_values(
            ["Total", "Knockout points", "Group points", "Team"],
            ascending=[False, False, False, True]
        )

        st.dataframe(style_player_table(df_show), use_container_width=True, hide_index=True)

    st.markdown("### Prediction overview")

    bet_matrix = (
        scored_predictions
        .pivot_table(
            index="player",
            columns="team",
            values="team_total_points",
            aggfunc="first"
        )
        .reset_index()
        .fillna("")
    )

    bet_matrix = bet_matrix.rename(columns={"player": "Player"})

    st.dataframe(
        bet_matrix,
        use_container_width=True,
        hide_index=True,
        height=table_height(bet_matrix)
    )

with tab_teams:
    st.subheader("🌍 Points by team")

    if team_scores.empty:
        st.info("No team has scored yet.")
    else:
        show_team_scores = team_scores[[
            "team", "last_date", "last_stage", "last_result",
            "group_points", "knockout_points", "team_total_points"
        ]].copy()

        show_team_scores = show_team_scores.sort_values(
            ["team_total_points", "knockout_points", "group_points", "team"],
            ascending=[False, False, False, True]
        )

        show_team_scores = show_team_scores.rename(columns={
            "team": "Team",
            "last_date": "Last date",
            "last_stage": "Last stage",
            "last_result": "Last result",
            "group_points": "Group points",
            "knockout_points": "Knockout points",
            "team_total_points": "Total points"
        })

        st.dataframe(
            style_team_scores(show_team_scores),
            use_container_width=True,
            hide_index=True,
            height=table_height(show_team_scores)
        )

with tab_rules:
    st.subheader("📌 Scoring rules")

    st.markdown(
        """
        ### Team selection

        Each player picked two teams from each of the four pots used by FIFA to draw the 12 World Cup groups, giving each player a total of 8 selected teams.

        At the end of the tournament, if multiple participants finish with the same number of points, the prize pool will be shared.

        | Pot 1 | Pot 2 | Pot 3 | Pot 4 |
        |---|---|---|---|
        | United States | Croatia | Norway | Jordan |
        | Mexico | Morocco | Panama | Cape Verde |
        | Canada | Colombia | Egypt | Ghana |
        | Spain | Uruguay | Algeria | Curacao |
        | Argentina | Switzerland | Scotland | Haiti |
        | France | Japan | Paraguay | New Zealand |
        | England | Senegal | Tunisia | Bosnia & Herzegovina |
        | Brazil | Iran | Ivory Coast | Sweden |
        | Portugal | South Korea | Uzbekistan | Czech Republic |
        | Netherlands | Ecuador | Qatar | Turkey |
        | Belgium | Austria | Saudi Arabia | DR Congo |
        | Germany | Australia | South Africa | Iraq |

        ### Group stage

        Each selected team earns points in every group-stage match.

        | Team result | Points |
        |---|---:|
        | Win | 3 |
        | Draw | 1 |
        | Loss | 0 |

        ### Knockout stage

        The teams selected at the beginning continue to count until the end of the tournament.

        | Stage won by the team | Points per win |
        |---|---:|
        | Round of 32 | 4 |
        | Round of 16 | 6 |
        | Quarter-finals | 8 |
        | Semi-finals | 10 |
        | Third-place match | 12 |
        | Final / Champion | 15 |

        If there is a tie at the end, the winning players share the prize equally.
        """
    )

with tab_files:
    st.subheader("📂 Project files")

    st.markdown(
        """
        This dashboard uses two main CSV files:

        ```text
        data/predictions.csv
        data/matches.csv
        ```

        Player ranking, team points, and prediction status are calculated automatically from these files.
        """
    )

    st.markdown("### predictions.csv")
    st.code(
        """player,team
Graziela,Argentina
Graziela,Spain
Graziela,Morocco""",
        language="text"
    )

    st.markdown("### matches.csv")
    st.code(
        """date,time,stage,group,home_team,away_team,home_goals,away_goals
2026-06-11,18:00,Group stage,A,Mexico,South Africa,2,0
2026-06-12,18:00,Group stage,B,Canada,Bosnia,1,1""",
        language="text"
    )

    col_matches, col_predictions = st.columns(2)
    with col_matches:
        st.download_button(
            "Download current matches.csv",
            data=matches.to_csv(index=False).encode("utf-8"),
            file_name="matches.csv",
            mime="text/csv"
        )
    with col_predictions:
        st.download_button(
            "Download predictions.csv",
            data=predictions.to_csv(index=False).encode("utf-8"),
            file_name="predictions.csv",
            mime="text/csv"
        )
