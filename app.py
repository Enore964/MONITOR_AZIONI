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
    # --- INSERISCI QUI I TUOI DATI REALI ---
    STOCKS = {
        "JE00B1VS3770": {"ticker": "ORO", "acquisto": 180.00, "quantita": 30}, # Oro
        "IE0003BJ2JS4": {"ticker": "NUCLEARE", "acquisto": 48.00, "quantita": 50},  # Uranio
        "IT0003856405": {"ticker": "LEONARDO", "acquisto": 50.50, "quantita": 100},  # Leonardo
        "IT0004496029": {"ticker": "AI ITALIA", "acquisto": 2.10, "quantita": 3000},   # Expert.ai
        "IT0005119810": {"ticker": "AVIO", "acquisto": 12.00, "quantita": 200}    # Avio
    }

    st.set_page_config(page_title="Gestione Portafoglio", layout="centered")
    st.title("📊 Rendimento Portafoglio")

    @st.cache_data(ttl=600)
    def get_data():
        data_list = []
        for isin, info in STOCKS.items():
            try:
                stock = yf.Ticker(info["ticker"])
                hist = stock.history(period="5d")
                if not hist.empty:
                    last_price = float(hist['Close'].iloc[-1])
                    prezzo_acq = info["acquisto"]
                    qta = info["quantita"]
                    
                    # Calcolo variazione giornaliera
                    if len(hist) >= 2:
                        prev_close = float(hist['Close'].iloc[-2])
                        var_giorno = ((last_price - prev_close) / prev_close) * 100
                    else:
                        var_giorno = 0.0
                    
                    # Calcolo Rendimento Totale
                    valore_attuale = last_price * qta
                    investimento_iniziale = prezzo_acq * qta
                    resa_euro = valore_attuale - investimento_iniziale
                    resa_perc = (resa_euro / investimento_iniziale) * 100 if investimento_iniziale != 0 else 0
                    
                    data_list.append({
                        "Ticker": info["ticker"], 
                        "Prezzo": last_price, 
                        "Qta": qta,
                        "ValoreTot": valore_attuale,
                        "VarGiorno": var_giorno,
                        "ResaEuro": resa_euro,
                        "ResaPerc": resa_perc
                    })
                time.sleep(0.3)
            except Exception:
                continue
        return data_list

    current_data = get_data()
    
    if current_data:
        # Calcolo Totale Portafoglio
        totale_portafoglio = sum(item['ValoreTot'] for item in current_data)
        totale_guadagno = sum(item['ResaEuro'] for item in current_data)
        
        # Header con riassunto totale
        st.subheader("Riepilogo Totale")
        c1, c2 = st.columns(2)
        c1.metric("Valore Portafoglio", f"€ {totale_portafoglio:,.2f}")
        c2.metric("Guadagno/Perdita Tot.", f"€ {totale_guadagno:,.2f}", delta=f"{totale_guadagno:,.2f}€")
        st.divider()

        # Dettaglio per ogni azione
        for item in current_data:
            with st.expander(f"**{item['Ticker']}** (Q.tà: {item['Qta']})", expanded=True):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("Prezzo", f"€{item['Prezzo']:.3f}", f"{item['VarGiorno']:.2f}%")
                
                with col_b:
                    st.metric("Resa in €", f"€{item['ResaEuro']:.2f}")
                
                with col_c:
                    st.metric("Resa %", f"{item['ResaPerc']:.2f}%")
                
                st.caption(f"Valore attuale posizione: € {item['ValoreTot']:,.2f}")
        
        if st.button("🔄 Aggiorna Prezzi"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.error("Caricamento dati fallito.")

    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
