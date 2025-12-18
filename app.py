import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="SNIPER TACTICAL VAULT v7", layout="wide")

# Funzione Invio Alert Telegram
def send_telegram_alert(message):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Errore invio Telegram: {e}")

# Titolo e Header
st.title("🎯 SNIPER TACTICAL VAULT v7")
st.subheader("Championship (E1) Strategy Manager")

# --- SEZIONE LEGENDA AGGIORNATA ---
with st.expander("📖 LEGENDA & GUIDA OPERATIVA (Inclusi Corner)"):
    st.markdown(f"""
    ### 🏟️ CAMPIONATO: Championship (E1)
    * **Strategia:** GoalMiner (Over 2.5)
    * **Yield Atteso:** 19.7%
    * **Range Quota:** 1.85 - 1.95

    ### 🚩 GUIDA CORNER (Novità v7)
    * **Corner 1H:** Media corner nel primo tempo. Se > 4.5, alta pressione offensiva.
    * **Total Corner:** Somma totale attesa. In E1, un valore > 10.5 correla spesso con l'Over 2.5.
    * **Corner Race:** Chi raggiunge prima X corner. Indica chi ha il comando del gioco.

    ### 📊 INDICATORI GOAL
    * **G-Miner Index:** Potenziale di Over 2.5 calcolato su algoritmi storici.
    * **Entry Point:** Il momento perfetto per entrare a mercato (solitamente tra il 20' e il 35').
    """)

# --- INPUT DATI MATCH ---
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    match_name = st.text_input("Match (es. Leeds - Watford)")
    quota = st.number_input("Quota Attuale", min_value=1.0, max_value=10.0, value=1.90, step=0.01)

with col2:
    corners = st.number_input("Corner Totali (Live)", min_value=0, value=0)
    minute = st.number_input("Minuto di Gioco", min_value=0, max_value=100, value=0)

with col3:
    note = st.text_area("Note Tecniche")

# --- BOTTONE SALVATAGGIO & ALERT ---
if st.button("🚀 SALVA MATCH & INVIA ALERT"):
    if match_name:
        # Messaggio per Telegram
        alert_msg = (
            f"🎯 *NUOVO SIGNAL SNIPER*\n\n"
            f"🏟️ Match: {match_name}\n"
            f"📈 Quota: {quota}\n"
            f"⏱️ Minuto: {minute}'\n"
            f"🚩 Corner: {corners}\n"
            f"📝 Note: {note}\n\n"
            f"💰 *Target Yield: 19.7%*"
        )
        
        # Invio
        send_telegram_alert(alert_msg)
        st.success(f"Match {match_name} salvato e alert inviato al bot!")
    else:
        st.warning("Inserisci il nome del match prima di salvare.")

# --- DATABASE LOCALE (Visualizzazione) ---
st.divider()
st.subheader("📂 Archivio Operativo Recente")
# Qui andrebbe la logica di persistenza (es. CSV o Database), per ora mostriamo struttura
st.info("I match salvati vengono inviati direttamente al tuo bot Telegram.")
