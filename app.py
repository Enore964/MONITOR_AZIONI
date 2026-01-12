import streamlit as st
import yfinance as yf
import pandas as pd
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
    # Titoli rigorosamente su Borsa Italiana (Milano)
    STOCKS = {
        "JE00B1VS3770": "PHAU.MI",   # Gold
        "IE0003BJ2JS4": "NCLR.MI",   # Uranium
        "IT0003856405": "LDO.MI",    # Leonardo
        "IT0004496029": "EXAI.MI",   # Expert.ai
        "IT0005119810": "AVIO.MI"    # Avio
    }

    st.set_page_config(page_title="Monitor Prezzi", layout="centered")
    
    st.title("📈 Prezzi Milano")
    st.caption(f"Ultimo aggiornamento: {time.strftime('%H:%M:%S')}")

    @st.cache_data(ttl=600)
    def get_data():
        data_list = []
        for isin, ticker in STOCKS.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty:
                    last_price = float(hist['Close'].iloc[-1])
                    if len(hist) >= 2:
                        prev_close = float(hist['Close'].iloc[-2])
                        pct_change = ((last_price - prev_close) / prev_close) * 100
                    else:
                        pct_change = 0.0
                    
                    data_list.append({
                        "Ticker": ticker, 
                        "Prezzo": last_price, 
                        "Var": pct_change
                    })
                time.sleep(0.3)
            except Exception:
                continue
        return data_list

    # Visualizzazione semplificata per mobile
    current_data = get_data()
    
    if current_data:
        for item in current_data:
            # Crea un box per ogni titolo
            with st.container():
                st.metric(
                    label=item['Ticker'], 
                    value=f"€ {item['Prezzo']:.3f}", 
                    delta=f"{item['Var']:.2f}%"
                )
                st.divider()
        
        if st.button("🔄 Forza Aggiornamento"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("Nessun dato disponibile. Riprova tra poco.")

    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
