import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
from requests import Session

# --- CONFIGURAZIONE SICUREZZA ---
PASSWORD_CORRETTA = "TuaPassword123" 

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]:
        return True
    st.title("🔒 Accesso Riservato")
    password = st.text_input("Inserisci la password:", type="password")
    if st.button("Accedi"):
        if password == PASSWORD_CORRETTA:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Password errata")
    return False

if check_password():
    # Mappatura ISIN dai tuoi appunti
    STOCKS = {
        "JE00B1VS3770": "PHAU.MI",   # WisdomTree Gold
        "IE0003BJ2JS4": "NCLR.MI",   # WisdomTree Uranium
        "IT0003856405": "LDO.MI",    # Leonardo
        "IT0004496029": "EXAI.MI",   # Expert.ai
        "IT0005119810": "AVIO.MI"    # Avio
    }

    st.set_page_config(page_title="Il Mio Portafoglio", layout="wide")
    
    # --- FUNZIONE DI RECUPERO DATI ANTI-BLOCCO ---
    @st.cache_data(ttl=600) # Cache di 10 minuti per evitare rate limit
    def get_data():
        data_list = []
        # Creiamo una sessione con User-Agent per evitare il blocco Yahoo
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        
        for isin, ticker in STOCKS.items():
            try:
                stock = yf.Ticker(ticker, session=session)
                hist = stock.history(period="5d")
                if not hist.empty and len(hist) >= 2:
                    last_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    pct_change = ((last_price - prev_close) / prev_close) * 100
                    data_list.append({"Ticker": ticker, "Prezzo": float(last_price), "Var": float(pct_change)})
            except Exception:
                continue
        return data_list

    st.title("📈 Monitor Portafoglio")
    
    current_data = get_data()
    if current_data:
        cols = st.columns(len(current_data))
        for i, item in enumerate(current_data):
            cols[i].metric(item['Ticker'], f"€{item['Prezzo']:.3f}", f"{item['Var']:.2f}%")
    else:
        st.warning("⚠️ Yahoo Finance sta limitando le richieste. Riprova tra qualche minuto.")

    st.divider()

    # --- GRAFICO STORICO ---
    st.subheader("Analisi Storica")
    selected_isin = st.selectbox("Seleziona titolo:", list(STOCKS.keys()), format_func=lambda x: STOCKS[x])
    
    # Scarichiamo i dati per il grafico usando la stessa sessione sicura
    session_chart = requests.Session()
    session_chart.headers.update({'User-Agent': 'Mozilla/5.0'})
    df_hist = yf.download(STOCKS[selected_isin], period="1y", session=session_chart)
    
    if not df_hist.empty:
        fig = go.Figure(data=[go.Scatter(x=df_hist.index, y=df_hist['Close'], line=dict(color='#00ffcc'))])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
