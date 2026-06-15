# World Cup Pool Dashboard

Interactive Streamlit dashboard to track World Cup pool predictions, match results, player rankings, and team points.

## Files

```text
app.py
data/predictions.csv
data/matches.csv
```

## Data format

`data/predictions.csv`

```csv
player,team
Graziela,Argentina
Graziela,Spain
```

`data/matches.csv`

```csv
date,time,stage,group,home_team,away_team,home_goals,away_goals
2026-06-11,18:00,Group stage,A,Mexico,South Africa,2,0
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

Edits made inside the online app are session-only. To make match updates permanent, replace `data/matches.csv` in GitHub with the updated CSV and redeploy/reload the app.
