# app.py
import os
import pandas as pd
import streamlit as st
from datetime import date

# ============================================================
# CONFIGURAÇÕES
# ============================================================
st.set_page_config(
    page_title="Bolão da Copa do Mundo",
    page_icon="🏆",
    layout="wide"
)

DATA_DIR = "data"
BETS_FILE = os.path.join(DATA_DIR, "times_apostados.csv")
MATCHES_FILE = os.path.join(DATA_DIR, "matches.csv")

GROUP_STAGE = "Fase de Grupos"

GROUP_POINTS = {
    "vitória": 3,
    "empate": 1,
    "derrota": 0
}

KNOCKOUT_POINTS = {
    "32 avos": 4,
    "Oitavas": 6,
    "Quartas": 8,
    "Semifinais": 10,
    "3º Lugar": 12,
    "Final": 15,
    "Campeão": 15
}

PHASE_ORDER = [
    "Fase de Grupos",
    "32 avos",
    "Oitavas",
    "Quartas",
    "Semifinais",
    "3º Lugar",
    "Final"
]


# ============================================================
# ESTILO
# ============================================================
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f7f4;
    }

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
    }

    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #166534;
    }

    .metric-label {
        font-size: 13px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.06em;
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


# ============================================================
# ARQUIVOS DE EXEMPLO
# ============================================================
def create_default_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(BETS_FILE):
        bets = [
            ("Graziela", "Argentina"), ("Graziela", "Espanha"),
            ("Graziela", "Marrocos"), ("Graziela", "Suica"),
            ("Graziela", "Noruega"), ("Graziela", "Escocia"),
            ("Graziela", "Republica Checa"), ("Graziela", "Bosnia"),

            ("Daniela", "Franca"), ("Daniela", "Espanha"),
            ("Daniela", "Uruguai"), ("Daniela", "Marrocos"),
            ("Daniela", "Noruega"), ("Daniela", "Paraguai"),
            ("Daniela", "Turquia"), ("Daniela", "Suecia"),

            ("Rubens", "Brasil"), ("Rubens", "Alemanha"),
            ("Rubens", "Croacia"), ("Rubens", "Suica"),
            ("Rubens", "Tunisia"), ("Rubens", "Egito"),
            ("Rubens", "Suecia"), ("Rubens", "Gana"),

            ("Luis", "Mexico"), ("Luis", "Franca"),
            ("Luis", "Marrocos"), ("Luis", "Coreia do Sul"),
            ("Luis", "Paraguai"), ("Luis", "Egito"),
            ("Luis", "Suecia"), ("Luis", "Republica Checa"),

            ("Gabriela", "Brasil"), ("Gabriela", "Mexico"),
            ("Gabriela", "Japao"), ("Gabriela", "Croacia"),
            ("Gabriela", "Paraguai"), ("Gabriela", "Noruega"),
            ("Gabriela", "Republica Checa"), ("Gabriela", "Turquia"),

            ("Miguel", "Espanha"), ("Miguel", "Franca"),
            ("Miguel", "Japao"), ("Miguel", "Uruguai"),
            ("Miguel", "Catar"), ("Miguel", "Noruega"),
            ("Miguel", "Suecia"), ("Miguel", "Turquia"),

            ("Carina", "Estados Unidos"), ("Carina", "Alemanha"),
            ("Carina", "Uruguai"), ("Carina", "Suica"),
            ("Carina", "Paraguai"), ("Carina", "Tunisia"),
            ("Carina", "Suecia"), ("Carina", "Gana"),

            ("Denise", "Portugal"), ("Denise", "Alemanha"),
            ("Denise", "Marrocos"), ("Denise", "Coreia do Sul"),
            ("Denise", "Escocia"), ("Denise", "Africa do Sul"),
            ("Denise", "Gana"), ("Denise", "Turquia"),

            ("Leandro", "Espanha"), ("Leandro", "Franca"),
            ("Leandro", "Croacia"), ("Leandro", "Coreia do Sul"),
            ("Leandro", "Algeria"), ("Leandro", "Costa do Marfim"),
            ("Leandro", "Suecia"), ("Leandro", "Iraque"),

            ("Bianca", "Brasil"), ("Bianca", "Portugal"),
            ("Bianca", "Coreia do Sul"), ("Bianca", "Croacia"),
            ("Bianca", "Catar"), ("Bianca", "Noruega"),
            ("Bianca", "Nova Zelandia"), ("Bianca", "Suecia"),

            ("Lizete", "Brasil"), ("Lizete", "Argentina"),
            ("Lizete", "Coreia do Sul"), ("Lizete", "Croacia"),
            ("Lizete", "Catar"), ("Lizete", "Noruega"),
            ("Lizete", "Nova Zelandia"), ("Lizete", "Suecia")
        ]

        pd.DataFrame(bets, columns=["jogador", "time"]).to_csv(BETS_FILE, index=False)

    if not os.path.exists(MATCHES_FILE):
        pd.DataFrame({
            "data": [
                "2026-06-11", "2026-06-11",
                "2026-06-12", "2026-06-12"
            ],
            "hora": [
                "18:00", "21:00", "18:00", "21:00"
            ],
            "fase": [
                "Fase de Grupos", "Fase de Grupos",
                "Fase de Grupos", "Fase de Grupos"
            ],
            "grupo": [
                "A", "A", "B", "B"
            ],
            "time_casa": [
                "Mexico", "Brasil", "Espanha", "Franca"
            ],
            "time_fora": [
                "Canada", "Japao", "Croacia", "Marrocos"
            ],
            "gols_casa": [
                "", "", "", ""
            ],
            "gols_fora": [
                "", "", "", ""
            ]
        }).to_csv(MATCHES_FILE, index=False)


# ============================================================
# FUNÇÕES
# ============================================================
@st.cache_data
def load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def save_matches(df):
    df.to_csv(MATCHES_FILE, index=False)
    st.cache_data.clear()


def clean_text(x):
    if pd.isna(x):
        return ""
    return str(x).strip()


def clean_team_name(x):
    return clean_text(x)


def clean_phase(x):
    return clean_text(x)


def score_is_available(row):
    home = clean_text(row.get("gols_casa", ""))
    away = clean_text(row.get("gols_fora", ""))

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

    home_team = clean_team_name(row["time_casa"])
    away_team = clean_team_name(row["time_fora"])
    home_score = int(float(row["gols_casa"]))
    away_score = int(float(row["gols_fora"]))
    fase = clean_phase(row["fase"])

    if home_score > away_score:
        return [
            {
                "data": row["data"],
                "fase": fase,
                "time": home_team,
                "resultado": "vitória",
                "adversario": away_team,
                "gols_pro": home_score,
                "gols_contra": away_score
            },
            {
                "data": row["data"],
                "fase": fase,
                "time": away_team,
                "resultado": "derrota",
                "adversario": home_team,
                "gols_pro": away_score,
                "gols_contra": home_score
            }
        ]

    if home_score < away_score:
        return [
            {
                "data": row["data"],
                "fase": fase,
                "time": home_team,
                "resultado": "derrota",
                "adversario": away_team,
                "gols_pro": home_score,
                "gols_contra": away_score
            },
            {
                "data": row["data"],
                "fase": fase,
                "time": away_team,
                "resultado": "vitória",
                "adversario": home_team,
                "gols_pro": away_score,
                "gols_contra": home_score
            }
        ]

    return [
        {
            "data": row["data"],
            "fase": fase,
            "time": home_team,
            "resultado": "empate",
            "adversario": away_team,
            "gols_pro": home_score,
            "gols_contra": away_score
        },
        {
            "data": row["data"],
            "fase": fase,
            "time": away_team,
            "resultado": "empate",
            "adversario": home_team,
            "gols_pro": away_score,
            "gols_contra": home_score
        }
    ]


def build_results_from_matches(matches):
    rows = []

    if matches.empty:
        return pd.DataFrame(columns=[
            "data", "fase", "time", "resultado",
            "adversario", "gols_pro", "gols_contra"
        ])

    for _, row in matches.iterrows():
        rows.extend(get_result_from_match(row))

    return pd.DataFrame(rows)


def points_for_team_result(row):
    fase = clean_phase(row["fase"])
    resultado = clean_text(row["resultado"]).lower()

    if fase == GROUP_STAGE:
        return GROUP_POINTS.get(resultado, 0)

    if fase in KNOCKOUT_POINTS:
        if resultado == "vitória":
            return KNOCKOUT_POINTS[fase]
        return 0

    return 0


def compute_team_scores(matches):
    results = build_results_from_matches(matches)

    if results.empty:
        return pd.DataFrame(columns=[
            "time",
            "pontos_grupos",
            "pontos_mata_mata",
            "pontos_totais_time",
            "ultima_data",
            "ultima_fase",
            "ultimo_resultado"
        ])

    results["pontos"] = results.apply(points_for_team_result, axis=1)

    results["pontos_grupos"] = results.apply(
        lambda r: r["pontos"] if r["fase"] == GROUP_STAGE else 0,
        axis=1
    )

    results["pontos_mata_mata"] = results.apply(
        lambda r: r["pontos"] if r["fase"] != GROUP_STAGE else 0,
        axis=1
    )

    scores = (
        results
        .groupby("time", as_index=False)
        .agg(
            pontos_grupos=("pontos_grupos", "sum"),
            pontos_mata_mata=("pontos_mata_mata", "sum")
        )
    )

    scores["pontos_totais_time"] = (
        scores["pontos_grupos"] + scores["pontos_mata_mata"]
    )

    results_for_last = results.copy()
    results_for_last["data_dt"] = pd.to_datetime(results_for_last["data"], errors="coerce")
    results_for_last = results_for_last.sort_values(["time", "data_dt", "fase"])

    last_status = (
        results_for_last
        .drop_duplicates(subset=["time"], keep="last")
        [["time", "data", "fase", "resultado"]]
        .rename(columns={
            "data": "ultima_data",
            "fase": "ultima_fase",
            "resultado": "ultimo_resultado"
        })
    )

    scores = scores.merge(last_status, on="time", how="left")

    return scores


def compute_ranking_and_bets(bets, matches):
    bets = bets.copy()
    bets["jogador"] = bets["jogador"].apply(clean_text)
    bets["time"] = bets["time"].apply(clean_team_name)

    players = (
        pd.DataFrame({"jogador": sorted(bets["jogador"].dropna().unique())})
        .reset_index(drop=True)
    )

    team_scores = compute_team_scores(matches)

    scored_bets = bets.merge(team_scores, on="time", how="left")

    fill_cols = [
        "pontos_grupos",
        "pontos_mata_mata",
        "pontos_totais_time"
    ]

    for col in fill_cols:
        scored_bets[col] = scored_bets[col].fillna(0).astype(int)

    for col in ["ultima_data", "ultima_fase", "ultimo_resultado"]:
        scored_bets[col] = scored_bets[col].fillna("")

    ranking = (
        scored_bets
        .groupby("jogador", as_index=False)
        .agg(
            pontos_grupos=("pontos_grupos", "sum"),
            pontos_mata_mata=("pontos_mata_mata", "sum"),
            pontos_totais=("pontos_totais_time", "sum"),
            times_apostados=("time", "count")
        )
    )

    ranking = players.merge(ranking, on="jogador", how="left")

    for col in ["pontos_grupos", "pontos_mata_mata", "pontos_totais", "times_apostados"]:
        ranking[col] = ranking[col].fillna(0).astype(int)

    ranking = ranking.sort_values(
        ["pontos_totais", "pontos_mata_mata", "pontos_grupos", "jogador"],
        ascending=[False, False, False, True]
    ).reset_index(drop=True)

    ranking.insert(0, "posição", ranking.index + 1)

    return ranking, scored_bets, team_scores


def make_matches_by_day(matches):
    if matches.empty:
        return {}

    df = matches.copy()
    df["data_dt"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.sort_values(["data_dt", "hora", "time_casa"])

    days = {}

    for data_dt, df_day in df.groupby("data_dt"):
        if pd.isna(data_dt):
            continue

        day_label = data_dt.strftime("%d/%m")

        table = df_day[[
            "hora",
            "fase",
            "grupo",
            "time_casa",
            "gols_casa",
            "gols_fora",
            "time_fora"
        ]].copy()

        table["placar"] = table.apply(
            lambda r: ""
            if clean_text(r["gols_casa"]) == "" or clean_text(r["gols_fora"]) == ""
            else f"{int(float(r['gols_casa']))} - {int(float(r['gols_fora']))}",
            axis=1
        )

        table = table[[
            "hora",
            "fase",
            "grupo",
            "time_casa",
            "placar",
            "time_fora"
        ]]

        table.columns = [
            "Horário",
            "Fase",
            "Grupo",
            "Time 1",
            "Placar",
            "Time 2"
        ]

        days[day_label] = table

    return days


def style_ranking(df):
    return (
        df.style
        .background_gradient(subset=["pontos_totais"], cmap="Greens")
        .format({
            "pontos_grupos": "{:.0f}",
            "pontos_mata_mata": "{:.0f}",
            "pontos_totais": "{:.0f}",
            "times_apostados": "{:.0f}"
        })
    )


def style_player_table(df):
    def color_result(value):
        value = str(value).lower()

        if value == "vitória":
            return "background-color: #bbf7d0; color: #14532d; font-weight: 700;"
        if value == "empate":
            return "background-color: #fef3c7; color: #92400e; font-weight: 700;"
        if value == "derrota":
            return "background-color: #fecaca; color: #991b1b; font-weight: 700;"
        return ""

    return (
        df.style
        .map(color_result, subset=["Último resultado"])
        .background_gradient(subset=["Total"], cmap="Greens")
        .format({
            "Pontos grupos": "{:.0f}",
            "Pontos mata-mata": "{:.0f}",
            "Total": "{:.0f}"
        })
    )


def style_team_scores(df):
    return (
        df.style
        .background_gradient(subset=["pontos_totais_time"], cmap="Greens")
        .format({
            "pontos_grupos": "{:.0f}",
            "pontos_mata_mata": "{:.0f}",
            "pontos_totais_time": "{:.0f}"
        })
    )


def prepare_matches_for_editor(matches):
    df = matches.copy()

    required_cols = [
        "data", "hora", "fase", "grupo",
        "time_casa", "time_fora", "gols_casa", "gols_fora"
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[required_cols].copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.date

    for col in ["hora", "fase", "grupo", "time_casa", "time_fora"]:
        df[col] = df[col].fillna("").astype(str)

    df["gols_casa"] = pd.to_numeric(df["gols_casa"], errors="coerce").astype("Int64")
    df["gols_fora"] = pd.to_numeric(df["gols_fora"], errors="coerce").astype("Int64")

    return df


def prepare_matches_for_saving(matches):
    df = matches.copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["data"] = df["data"].fillna("")

    for col in ["hora", "fase", "grupo", "time_casa", "time_fora"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    for col in ["gols_casa", "gols_fora"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].apply(lambda x: "" if pd.isna(x) else int(x))

    df = df.sort_values(["data", "hora", "fase", "time_casa"]).reset_index(drop=True)

    return df


def table_height(df, row_height=35, header_height=38, max_height=900):
    n_rows = len(df)
    height = header_height + row_height * max(n_rows, 1)
    return min(height, max_height)

# ============================================================
# APP
# ============================================================
create_default_files()

bets = load_csv(BETS_FILE)
matches = load_csv(MATCHES_FILE)

st.markdown(
    """
    <div class="title-card">
        <h1>🏆 Bolão da Copa do Mundo</h1>
        <p>Um único arquivo de jogos controla resultados, pontuação e ranking</p>
    </div>
    """,
    unsafe_allow_html=True
)

if bets.empty:
    st.error("O arquivo data/times_apostados.csv está vazio ou não foi encontrado.")
    st.stop()

if matches.empty:
    st.error("O arquivo data/matches.csv está vazio ou não foi encontrado.")
    st.stop()

ranking, scored_bets, team_scores = compute_ranking_and_bets(bets, matches)

n_players = bets["jogador"].nunique()
n_teams = bets["time"].nunique()
n_matches = len(matches)
n_finished = matches.apply(score_is_available, axis=1).sum()
leader = ranking.iloc[0]["jogador"] if not ranking.empty else "-"
leader_points = ranking.iloc[0]["pontos_totais"] if not ranking.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{n_players}</div>
            <div class="metric-label">Jogadores</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{n_teams}</div>
            <div class="metric-label">Seleções apostadas</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{n_matches}</div>
            <div class="metric-label">Jogos</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{n_finished}</div>
            <div class="metric-label">Resultados</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{leader}</div>
            <div class="metric-label">Líder: {leader_points} pts</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("")

tab_ranking, tab_update, tab_matches, tab_players, tab_teams, tab_rules, tab_files = st.tabs([
    "🏅 Ranking",
    "✏️ Atualizar resultados",
    "📅 Jogos",
    "📝 Apostas",
    "🌍 Seleções",
    "📌 Regras",
    "📂 Arquivos"
])


# ============================================================
# RANKING
# ============================================================
with tab_ranking:
    st.subheader("🏅 Ranking geral")

    st.dataframe(
       style_ranking(ranking),
        use_container_width=True,
        hide_index=True,
        height=table_height(ranking)
    )

    st.markdown("### Pontos totais por jogador")

    chart_df = ranking[["jogador", "pontos_totais"]].copy().set_index("jogador")
    st.bar_chart(chart_df)


# ============================================================
# ATUALIZAR RESULTADOS
# ============================================================
with tab_update:
    st.subheader("✏️ Atualizar resultados no próprio `matches.csv`")

    st.info(
        "Edite apenas os campos de gols. Ao salvar, o app atualiza o arquivo "
        "`data/matches.csv` e recalcula ranking, apostas e pontuação das seleções."
    )

    editor_df = prepare_matches_for_editor(matches)

    edited_matches = st.data_editor(
        editor_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "data": st.column_config.DateColumn("Data"),
            "hora": st.column_config.TextColumn("Hora"),
            "fase": st.column_config.SelectboxColumn(
                "Fase",
                options=PHASE_ORDER
            ),
            "grupo": st.column_config.TextColumn("Grupo"),
            "time_casa": st.column_config.TextColumn("Time 1"),
            "time_fora": st.column_config.TextColumn("Time 2"),
            "gols_casa": st.column_config.NumberColumn(
                "Gols time 1",
                min_value=0,
                step=1,
                format="%d"
            ),
            "gols_fora": st.column_config.NumberColumn(
                "Gols time 2",
                min_value=0,
                step=1,
                format="%d"
            )
        },
        key="matches_editor"
    )

    col_save, col_reload = st.columns([1, 1])

    with col_save:
        if st.button("💾 Salvar resultados no matches.csv"):
            matches_to_save = prepare_matches_for_saving(edited_matches)
            save_matches(matches_to_save)
            st.success("Resultados salvos. O ranking foi atualizado.")
            st.rerun()

    with col_reload:
        if st.button("↻ Recarregar sem salvar"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("### Resultados interpretados pelo dashboard")

    interpreted_results = build_results_from_matches(prepare_matches_for_saving(edited_matches))

    if interpreted_results.empty:
        st.warning("Nenhum resultado completo foi encontrado ainda.")
    else:
        st.dataframe(
            interpreted_results,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# JOGOS POR DIA
# ============================================================
with tab_matches:
    st.subheader("📅 Jogos por dia")

    days = make_matches_by_day(matches)

    if not days:
        st.info("Nenhum jogo disponível.")
    else:
        selected_days = st.multiselect(
            "Selecione os dias para mostrar",
            list(days.keys()),
            default=list(days.keys())
        )

        for day in selected_days:
            st.markdown(
                f"""
                <div class="day-title">📅 {day}</div>
                """,
                unsafe_allow_html=True
            )

            st.dataframe(
                days[day],
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# APOSTAS
# ============================================================
with tab_players:
    st.subheader("📝 Apostas por jogador")

    player_names = sorted(scored_bets["jogador"].unique())

    selected_players = st.multiselect(
        "Selecione jogadores para mostrar",
        player_names,
        default=player_names
    )

    for jogador in selected_players:
        total_row = ranking.loc[ranking["jogador"] == jogador, "pontos_totais"]
        total_player = int(total_row.iloc[0]) if not total_row.empty else 0

        st.markdown(
            f"""
            <div class="player-card">
                <div class="player-name">{jogador}</div>
                <div class="small-note">Total atual: <b>{total_player}</b> pontos</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        df_player = scored_bets.loc[scored_bets["jogador"] == jogador].copy()

        df_show = df_player[[
            "time",
            "ultima_fase",
            "ultimo_resultado",
            "pontos_grupos",
            "pontos_mata_mata",
            "pontos_totais_time"
        ]].copy()

        df_show.columns = [
            "Time",
            "Última fase",
            "Último resultado",
            "Pontos grupos",
            "Pontos mata-mata",
            "Total"
        ]

        df_show = df_show.sort_values(
            ["Total", "Pontos mata-mata", "Pontos grupos", "Time"],
            ascending=[False, False, False, True]
        )

        st.dataframe(
            style_player_table(df_show),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("### Visão geral das apostas")

    bet_matrix = (
        scored_bets
        .pivot_table(
            index="time",
            columns="jogador",
            values="pontos_totais_time",
            aggfunc="first"
        )
        .reset_index()
        .fillna("")
    )

    st.dataframe(
        bet_matrix,
        use_container_width=True,
        hide_index=True,
        height=table_height(bet_matrix)
    )

# ============================================================
# SELEÇÕES
# ============================================================
with tab_teams:
    st.subheader("🌍 Pontuação por seleção")

    if team_scores.empty:
        st.info("Nenhuma seleção pontuou ainda.")
    else:
        show_team_scores = team_scores[[
            "time",
            "ultima_data",
            "ultima_fase",
            "ultimo_resultado",
            "pontos_grupos",
            "pontos_mata_mata",
            "pontos_totais_time"
        ]].copy()

        show_team_scores = show_team_scores.sort_values(
            ["pontos_totais_time", "pontos_mata_mata", "pontos_grupos", "time"],
            ascending=[False, False, False, True]
        )

        st.dataframe(
            style_team_scores(show_team_scores),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# REGRAS
# ============================================================
with tab_rules:
    st.subheader("📌 Regras de pontuação")

    st.markdown(
        """
        ### Fase de Grupos

        Cada seleção apostada soma pontos em cada jogo da fase de grupos.

        | Resultado da seleção | Pontos |
        |---|---:|
        | Vitória | 3 |
        | Empate | 1 |
        | Derrota | 0 |

        ### Depois da Fase de Grupos

        As mesmas seleções escolhidas no início continuam valendo até o final.

        | Fase vencida pela seleção | Pontos por vitoria |
        |---|---:|
        | 16 avos | 4 |
        | Oitavas | 6 |
        | Quartas de final | 8 |
        | Semifinais | 10 |
        | Disputa de 3º lugar | 12 |
        | Final / Campeão | 15 |

        Caso haja empate no final, os apostadores ganhadores dividem o premio igualmente.`.
        """
    )


# ============================================================
# ARQUIVOS
# ============================================================
with tab_files:
    st.subheader("📂 Arquivos usados")

    st.markdown(
        """
        Este dashboard usa apenas dois arquivos principais:

        ```text
        data/times_apostados.csv
        data/matches.csv
        ```

        O ranking, a pontuação por seleção e a situação das apostas são calculados automaticamente.
        """
    )

    st.markdown("### `times_apostados.csv`")

    st.code(
        """jogador,time
Graziela,Argentina
Graziela,Espanha
Graziela,Marrocos
Daniela,Franca
Daniela,Espanha""",
        language="text"
    )

    st.markdown("### `matches.csv`")

    st.code(
        """data,hora,fase,grupo,time_casa,time_fora,gols_casa,gols_fora
2026-06-11,18:00,Fase de Grupos,A,Mexico,Canada,,
2026-06-11,21:00,Fase de Grupos,A,Brasil,Japao,,
2026-06-12,18:00,Fase de Grupos,B,Espanha,Croacia,,
2026-06-12,21:00,Fase de Grupos,B,Franca,Marrocos,,""",
        language="text"
    )

    st.download_button(
        "Baixar matches.csv atual",
        data=matches.to_csv(index=False).encode("utf-8"),
        file_name="matches.csv",
        mime="text/csv"
    )

    st.download_button(
        "Baixar times_apostados.csv atual",
        data=bets.to_csv(index=False).encode("utf-8"),
        file_name="times_apostados.csv",
        mime="text/csv"
    )
