import streamlit as st
import yfinance as yf
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
    # --- INSERISCI QUI I TUOI PREZZI DI ACQUISTO REALI ---
    STOCKS = {
        "JE00B1VS3770": {"ticker": "PHAU.MI", "acquisto": 180.00}, # Oro
        "IE0003BJ2JS4": {"ticker": "NCLR.MI", "acquisto": 48.00},  # Uranio
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 15.50},   # Leonardo
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 2.10},   # Expert.ai
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 12.00}   # Avio
    }

    st.set_page_config(page_title="Resa Portafoglio", layout="centered")
    st.title("💰 Resa Portafoglio")

    @st.cache_data(ttl=600)
    def get_data():
        data_list = []
        for isin, info in STOCKS.items():
            try:
                stock = yf.Ticker(info["ticker"])
                hist = stock.history(period="5d")
                if not hist.empty:
                    last_price = float(hist['Close'].iloc[-1])
                    prezzo_acquisto = info["acquisto"]
                    
                    # Calcolo della resa rispetto al tuo acquisto
                    resa_percentuale = ((last_price - prezzo_acquisto) / prezzo_acquisto) * 100
                    guadagno_assoluto = last_price - prezzo_acquisto
                    
                    data_list.append({
                        "Ticker": info["ticker"], 
                        "Attuale": last_price, 
                        "Acquisto": prezzo_acquisto,
                        "Resa": resa_percentuale,
                        "Guadagno": guadagno_assoluto
                    })
                time.sleep(0.3)
            except Exception:
                continue
        return data_list

    current_data = get_data()
    
    if current_data:
        for item in current_data:
            with st.container():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(item['Ticker'])
                    st.write(f"Prezzo Acquisto: **€ {item['Acquisto']:.3f}**")
                    st.write(f"Prezzo Attuale: **€ {item['Attuale']:.3f}**")
                with col2:
                    # Mostra la resa rispetto al tuo prezzo di acquisto
                    st.metric(
                        label="Resa Totale", 
                        value=f"{item['Resa']:.2f}%",
                        delta=f"€ {item['Guadagno']:.2f}"
                    )
                st.divider()
        
        if st.button("🔄 Aggiorna Prezzi"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("Errore nel recupero dati.")

    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
