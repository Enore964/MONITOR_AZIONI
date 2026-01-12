import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

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
    # Elenco ISIN aggiornato dai tuoi appunti
    STOCKS = {
        "JE00B1VS3770": "PHAU.MI",   # WisdomTree Physical Gold (EUR)
        "IE0003BJ2JS4": "NCLR.MI",   # WisdomTree Uranium
        "IT0003856405": "LDO.MI",    # Leonardo S.p.A.
        "IT0004496029": "EXAI.MI",   # Expert.ai
        "IT0005119810": "AVIO.MI"    # Avio S.p.A.
    }

    st.set_page_config(page_title="Portfolio Monitor", layout="wide")
    st.title("📈 Monitor Portafoglio")
    
    @st.cache_data(ttl=600)
    def get_data():
        data_list = []
        for isin, ticker in STOCKS.items():
            try:
                stock = yf.Ticker(ticker)
                # Chiediamo un periodo più lungo per essere sicuri di trovare dati
                hist = stock.history(period="1mo") 
                if not hist.empty:
                    last_price = hist['Close'].iloc[-1]
                    # Se c'è solo un giorno di dati, mettiamo variazione 0 invece di saltare il titolo
                    if len(hist) > 1:
                        prev_close = hist['Close'].iloc[-2]
                        pct_change = ((last_price - prev_close) / prev_close) * 100
                    else:
                        pct_change = 0.0
                    
                    data_list.append({
                        "Ticker": ticker, 
                        "Prezzo": float(last_price), 
                        "Var": float(pct_change)
                    })
                time.sleep(0.5) 
            except Exception:
                continue
        return data_list

    current_data = get_data()
    if current_data:
        cols = st.columns(len(current_data))
        for i, item in enumerate(current_data):
            cols[i].metric(item['Ticker'], f"€{item['Prezzo']:.3f}", f"{item['Var']:.2f}%")
    else:
        st.info("🔄 Recupero dati... Se l'errore persiste, Yahoo sta limitando l'accesso. Riprova tra 10 minuti.")

    st.divider()
    st.subheader("Analisi Storica")
    
    selected_isin = st.selectbox("Seleziona titolo:", list(STOCKS.keys()), format_func=lambda x: STOCKS[x])
    
    # Download semplificato senza parametri session
    df_hist = yf.download(STOCKS[selected_isin], period="1y")
    
    if not df_hist.empty:
        fig = go.Figure(data=[go.Scatter(x=df_hist.index, y=df_hist['Close'], line=dict(color='#00ffcc'))])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)




