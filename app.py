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

    st.set_page_config(page_title="Monitor Avanzato", layout="centered")
    st.title("📈 Monitor Portafoglio")

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
                    
                    # 1. Calcolo Scostamento Giornaliero (Rispetto a ieri)
                    if len(hist) >= 2:
                        prev_close = float(hist['Close'].iloc[-2])
                        var_giornaliera = ((last_price - prev_close) / prev_close) * 100
                    else:
                        var_giornaliera = 0.0
                    
                    # 2. Calcolo Resa Totale (Rispetto al tuo acquisto)
                    resa_totale = ((last_price - prezzo_acquisto) / prezzo_acquisto) * 100
                    guadagno_assoluto = last_price - prezzo_acquisto
                    
                    data_list.append({
                        "Ticker": info["ticker"], 
                        "Attuale": last_price, 
                        "Acquisto": prezzo_acquisto,
                        "VarGiorno": var_giornaliera,
                        "ResaTot": resa_totale,
                        "Guadagno": guadagno_assoluto
                    })
                time.sleep(0.3)
            except Exception:
                continue
        return data_list

    current_data = get_data()
    
    if current_data:
        for item in current_data:
            with st.expander(f"**{item['Ticker']}** - € {item['Attuale']:.3f}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Metrica per l'andamento di oggi
                    st.metric(
                        label="Oggi", 
                        value=f"€ {item['Attuale']:.3f}", 
                        delta=f"{item['VarGiorno']:.2f}% (24h)"
                    )
                
                with col2:
                    # Metrica per la resa dal tuo acquisto
                    st.metric(
                        label="Resa Totale", 
                        value=f"{item['ResaTot']:.2f}%",
                        delta=f"€ {item['Guadagno']:.2f}",
                        delta_color="normal"
                    )
                st.caption(f"Prezzo medio acquisto: € {item['Acquisto']:.3f}")
        
        if st.button("🔄 Aggiorna Dati"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("Errore nel recupero dati da Milano.")

    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
