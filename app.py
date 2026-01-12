import streamlit as st
import yfinance as yf
import time

# --- CONFIGURAZIONE SICUREZZA ---
PASSWORD_CORRETTA = "TuaPassword123" # Cambiala se necessario

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
    # --- DATI DI PORTAFOGLIO (Modifica i valori con i tuoi reali) ---
    STOCKS = {
        "JE00B1VS3770": {"ticker": "PHAU.MI", "acquisto": 180.00, "quantita": 10}, 
        "IE0003BJ2JS4": {"ticker": "NCLR.MI", "acquisto": 48.00, "quantita": 50},  
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 15.50, "quantita": 100},  
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 2.10, "quantita": 500},   
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 12.00, "quantita": 80}    
    }

    st.set_page_config(page_title="Riepilogo Azioni", layout="centered")
    st.title("📋 Riepilogo Singole Azioni")

    @st.cache_data(ttl=600)
    def get_data():
        data_list = []
        for isin, info in STOCKS.items():
            try:
                stock = yf.Ticker(info["ticker"])
                hist = stock.history(period="10d")
                if not hist.empty:
                    last_price = float(hist['Close'].iloc[-1])
                    prezzo_acq = info["acquisto"]
                    qta = info["quantita"]
                    
                    # Variazione Giornaliera (Rispetto a ieri)
                    if len(hist) >= 2:
                        prev_close = float(hist['Close'].iloc[-2])
                        var_giorno = ((last_price - prev_close) / prev_close) * 100
                    else:
                        var_giorno = 0.0
                    
                    # Rendimento Totale (Rispetto all'acquisto)
                    valore_attuale = last_price * qta
                    investimento_iniziale = prezzo_acq * qta
                    resa_euro = valore_attuale - investimento_iniziale
                    resa_perc = (resa_euro / investimento_iniziale) * 100 if investimento_iniziale != 0 else 0
                    
                    data_list.append({
                        "Ticker": info["ticker"], 
                        "Prezzo": last_price, 
                        "Qta": qta,
                        "Acquisto": prezzo_acq,
                        "ValoreTot": valore_attuale,
                        "Investito": investimento_iniziale,
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
        for item in current_data:
            # Crea un box visivo per ogni azione
            with st.container(border=True):
                st.subheader(f"🏷️ {item['Ticker']}")
                
                # Prima riga: Prezzo e Variazione di oggi
                c1, c2 = st.columns(2)
                c1.metric("Prezzo Attuale", f"€ {item['Prezzo']:.3f}")
                c2.metric("Scostamento Oggi", f"{item['VarGiorno']:.2f}%", delta=f"{item['VarGiorno']:.2f}%")
                
                st.write("---")
                
                # Seconda riga: Resa rispetto all'acquisto
                c3, c4 = st.columns(2)
                c3.metric("Resa in Euro", f"€ {item['ResaEuro']:.2f}", delta=f"€ {item['ResaEuro']:.2f}")
                c4.metric("Resa Percentuale", f"{item['ResaPerc']:.2f}%", delta=f"{item['ResaPerc']:.2f}%")
                
                # Terza riga: Dettagli tecnici
                st.info(f"""
                **Dettagli Posizione:**
                * Prezzo Acquisto: € {item['Acquisto']:.3f} | Quantità: {item['Qta']}
                * Capitale Investito: € {item['Investito']:,.2f}
                * Valore Attuale: **€ {item['ValoreTot']:,.2f}**
                """)
        
        if st.button("🔄 Aggiorna Dati"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.warning("⚠️ Caricamento dei dati in corso...")

    if st.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()
