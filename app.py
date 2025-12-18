import streamlit as st
import pandas as pd
import requests
import io
import os
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Sniper Tactical Vault v7", layout="wide", page_icon="🎯")

# --- CSS DARK & TACTICAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    h1, h2, h3 { color: #00FFAA !important; text-transform: uppercase; letter-spacing: 2px; }
    [data-testid="stMetricValue"] { color: #00FFAA !important; }
    .stButton>button { 
        background-color: #1A1C24; color: #00FFAA; border: 1px solid #00FFAA; 
        border-radius: 5px; font-weight: bold; width: 100%; transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #00FFAA; color: #0E1117; box-shadow: 0px 0px 15px #00FFAA; }
    </style>
    """, unsafe_allow_html=True)

HISTORY_FILE = "goalminer_corner_vault.csv"
if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=['Data', 'Campionato', 'Match', 'Media', 'Quota', 'Stake', 'Status', 'Profitto']).to_csv(HISTORY_FILE, index=False)

LEAGUES = {
    'Premier League': 'E0', 'Championship': 'E1', 'League 1': 'E2', 'League 2': 'E3', 'Conference': 'EC',
    'Serie A': 'I1', 'Serie B': 'I2', 'Bundesliga 1': 'D1', 'Bundesliga 2': 'D2',
    'La Liga 1': 'SP1', 'La Liga 2': 'SP2', 'Ligue 1': 'F1', 'Ligue 2': 'F2',
    'Eredivisie': 'N1', 'Jupiler League (BE)': 'B1', 'Primeira Liga (PT)': 'P1',
    'Super Turkish Lig': 'T1', 'Ethniki Katigoria (GR)': 'G1',
    'Premiership Scozia': 'SC0', 'Championship Scozia': 'SC1', 'League 1 Scozia': 'SC2', 'League 2 Scozia': 'SC3'
}

@st.cache_data(ttl=3600)
def scan_and_load_data():
    performance, all_teams_medie, league_teams_map = [], {}, {}
    for name, code in LEAGUES.items():
        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
                if 'HC' in df.columns:
                    df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'HC', 'AC'])
                    wins = len(df[(df['HC'] + df['AC']) > 9.5])
                    y = ((wins * 1.85) - len(df)) / len(df) * 100 if len(df) > 0 else 0
                    performance.append({'Lega': name, 'Yield': round(y, 2)})
                    league_teams_map[name] = sorted(df['HomeTeam'].unique())
                    temp_stats = {}
                    for _, row in df.iterrows():
                        tot = row['HC'] + row['AC']
                        for t in [row['HomeTeam'], row['AwayTeam']]:
                            if t not in temp_stats: temp_stats[t] = []
                            temp_stats[t].append(tot)
                    for t, v in temp_stats.items(): all_teams_medie[t] = sum(v)/len(v)
        except: continue
    return pd.DataFrame(performance), all_teams_medie, league_teams_map

# --- LOGICA ---
st.title("🎯 SNIPER TACTICAL VAULT v7")
df_perf, medie_squadre, league_teams_map = scan_and_load_data()

# --- SIDEBAR: FINANCE ---
with st.sidebar:
    st.header("🏦 FINANCE")
    bankroll = st.number_input("Bankroll Totale (€)", value=1000.0)
    current_stake = (bankroll * st.slider("Stake (%)", 1.0, 5.0, 2.0)) / 100
    st.metric("PUNTATA FISSA", f"{current_stake:.2f} €")
    
    st.divider()
    st.header("📖 GUIDA RAPIDA")
    st.markdown("1. Seleziona Lega\n2. Controlla Medie Corner\n3. Salva nel Registro")

# --- DASHBOARD YIELD ---
if not df_perf.empty:
    df_perf = df_perf.sort_values('Yield', ascending=False)
    cols = st.columns(4)
    for i in range(min(4, len(df_perf))):
        row = df_perf.iloc[i]
        cols[i].metric(row['Lega'], f"{row['Yield']}%", f"{row['Yield']-19.7:.1f}%")

st.divider()

# --- AREA OPERATIVA ---
tab1, tab2, tab3 = st.tabs(["🎯 ANALISI MATCH", "📓 REGISTRO BET", "📜 LEGENDA"])

with tab1:
    st.subheader("🔍 VERIFICA INCONTRO")
    c1, c2, c3 = st.columns(3)
    with c1: sel_league = st.selectbox("1. CAMPIONATO", options=[""] + list(league_teams_map.keys()))
    squadre_lega = league_teams_map.get(sel_league, [])
    with c2: casa = st.selectbox("2. TEAM HOME", options=[""] + squadre_lega)
    with c3: ospite = st.selectbox("3. TEAM AWAY", options=[""] + [t for t in squadre_lega if t != casa])

    if casa and ospite:
        m_h, m_o = medie_squadre[casa], medie_squadre[ospite]
        m_comb = (m_h + m_o) / 2
        
        st.write("---")
        det_h, det_comb, det_o = st.columns(3)
        with det_h: st.markdown(f"**Media {casa}**\n## <span style='color:{'green' if m_h >= 9.5 else 'red'}'>{m_h:.2f}</span>", unsafe_allow_html=True)
        with det_comb: st.markdown(f"**Combinata**\n## <span style='color:#00FFAA'>{m_comb:.2f}</span>", unsafe_allow_html=True)
        with det_o: st.markdown(f"**Media {ospite}**\n## <span style='color:{'green' if m_o >= 9.5 else 'red'}'>{m_o:.2f}</span>", unsafe_allow_html=True)
        
        st.write("---")
        quota = st.number_input("Quota Rilevata", value=1.85, step=0.01)

        if st.button("🚀 REGISTRA MATCH NEL VAULT"):
            df_h = pd.read_csv(HISTORY_FILE)
            new_bet = {'Data': datetime.now().strftime("%d/%m"), 'Campionato': sel_league, 'Match': f"{casa} vs {ospite}", 'Media': round(m_comb, 2), 'Quota': quota, 'Stake': current_stake, 'Status': 'Pending', 'Profitto': 0.0}
            pd.concat([df_h, pd.DataFrame([new_bet])], ignore_index=True).to_csv(HISTORY_FILE, index=False)
            st.success("Match archiviato con successo!")

with tab2:
    st.subheader("📓 DIARIO REALE")
    df_hist = pd.read_csv(HISTORY_FILE)
    if not df_hist.empty:
        inv, prof = df_hist['Stake'].sum(), df_hist['Profitto'].sum()
        yr = (prof / inv * 100) if inv > 0 else 0
        st.metric("YIELD REALE DIARIO", f"{yr:.2f}%", f"{yr-19.7:.1f}%")
        edited = st.data_editor(df_hist, use_container_width=True, num_rows="dynamic", column_config={"Status": st.column_config.SelectboxColumn("Status", options=["Pending", "✅ WIN", "❌ LOSE"])})
        if st.button("🔄 AGGIORNA STATISTICHE"):
            for i, row in edited.iterrows():
                if row['Status'] == "✅ WIN": edited.at[i, 'Profitto'] = round((row['Stake'] * row['Quota']) - row['Stake'], 2)
                elif row['Status'] == "❌ LOSE": edited.at[i, 'Profitto'] = -row['Stake']
            edited.to_csv(HISTORY_FILE, index=False)
            st.rerun()

with tab3:
    st.subheader("📜 GUIDA TECNICA CORNER")
    col_leg1, col_leg2 = st.columns(2)
    with col_leg1:
        st.markdown(f"""
        ### 🚩 MERCATO CORNER
        * **Focus:** Calci d'angolo totali (Over 9.5).
        * **Target Campionato:** Championship (E1).
        * **Yield di Riferimento:** 19.7%.
        * **Range Quota Corner:** 1.85 - 1.95.

        ### 📊 METRICHE
        * **Media Squadra:** Corner totali registrati nella stagione 25/26 (fatti + subiti).
        * **Media Combinata:** Somma delle medie diviso due. Parametro chiave per l'ingresso.
        """)
    with col_leg2:
        st.markdown("""
        ### 🚦 SEGNALI OPERATIVI CORNER
        * **🔥 GOLD:** Combinata ≥ 10.5 | Entrambe le squadre ≥ 9.5.
        * **⚖️ SILVER:** Combinata ≥ 9.5 (Conforme alla strategia).
        * **❌ NO BET:** Combinata < 9.5.

        ### 🏦 RISK MANAGEMENT
        * **Stake:** 2% per preservare il bankroll e massimizzare lo yield nel lungo periodo.
        """)
