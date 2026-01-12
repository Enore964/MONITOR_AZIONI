import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time

# --- CONFIGURAZIONE SICUREZZA ---
PASSWORD_CORRETTA = "TuaPassword123"

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if st.session_state["password_correct"]: return True
    st.title("🔒 Accesso Riservato")
    password = st.text_input("Password:", type="password")
    if st.button("Accedi"):
        if password == PASSWORD_CORRETTA:
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("❌ Errata")
    return False

if check_password():
    # --- CONFIGURAZIONE TITOLI ---
    # Nota: Per l'Uranio ora usiamo "URA" (USA)
    STOCKS = {
        "JE00B1VS3770": {"ticker": "PHAU.MI", "acquisto": 352.13, "quantita": 30, "nome": "Oro Fisico", "usa": False}, 
        "IE0003BJ2JS4": {"ticker": "URA.MI", "acquisto": 48.54, "quantita": 200, "nome": "Uranio (USA Ticker)", "usa": True},  
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 59.76, "quantita": 200, "nome": "Leonardo", "usa": False},  
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 1.93, "quantita": 3000, "nome": "Expert AI", "usa": False},   
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 36.55, "quantita": 250, "nome": "Avio Spazio", "usa": False}    
    }

    st.sidebar.title("📱 Menu")
    scelta = st.sidebar.radio("Vai a:", ["📋 Lista", "📊 Grafici"])

    @st.cache_data(ttl=3600)
    def get_exchange_rate():
        # Recupera il cambio Euro/Dollaro
        try:
            fx = yf.Ticker("EURUSD=X")
            return 1 / fx.history(period="1d")['Close'].iloc[-1]
        except: return 0.92 # Valore di backup se il cambio fallisce

    @st.cache_data(ttl=3600)
    def get_data():
        # 1. Recuperiamo il cambio attuale Dollaro -> Euro
        try:
            # Ticker per il cambio: quanto vale 1 Dollaro in Euro
            fx = yf.Ticker("USDEUR=X") 
            usd_to_eur = float(fx.history(period="1d")['Close'].iloc[-1])
        except:
            usd_to_eur = 0.92 # Valore di emergenza se Yahoo non risponde

        data_list = []
        for isin, info in STOCKS.items():
            try:
                stock = yf.Ticker(info["ticker"])
                hist = stock.history(period="5d")
                
                if not hist.empty:
                    # Prezzo grezzo (Euro per i titoli .MI, Dollari per URA)
                    raw_price = float(hist['Close'].dropna().iloc[-1])
                    
                    # --- LOGICA DI CONVERSIONE ---
                    if info["usa"]:
                        # Se il titolo è americano (URA), trasformiamo il prezzo in Euro
                        prezzo_attuale_eur = raw_price * usd_to_eur
                    else:
                        # Se è italiano (.MI), il prezzo è già in Euro
                        prezzo_attuale_eur = raw_price
                    
                    prezzo_acq_eur = info["acquisto"]
                    qta = info["quantita"]
                    
                    # --- CALCOLO RENDIMENTI (Tutto in Euro) ---
                    investimento_iniziale = prezzo_acq_eur * qta
                    valore_attuale_totale = prezzo_attuale_eur * qta
                    utile_netto_eur = valore_attuale_totale - investimento_iniziale
                    percentuale_resa = (utile_netto_eur / investimento_iniziale) * 100
                    
                    # Calcolo scostamento giornaliero (basato sul prezzo originale del mercato)
                    prev_close = hist['Close'].dropna().iloc[-2]
                    var_giorno_perc = ((raw_price - prev_close) / prev_close) * 100
                    
                    data_list.append({
                        "Nome": info["nome"],
                        "Prezzo_Eur": prezzo_attuale_eur,
                        "Investito": investimento_iniziale,
                        "ValoreTot": valore_attuale_totale,
                        "ResaEuro": utile_netto_eur,
                        "ResaPerc": percentuale_resa,
                        "VarGiorno": var_giorno_perc,
                        "Ticker": info["ticker"]
                    })
                time.sleep(1)
            except: continue
        return data_list

    data = get_data()

    if data:
        if scelta == "📋 Lista":
            st.title("📋 Portafoglio")
            tot_utile = sum(item['ResaEuro'] for item in data)
            st.metric("UTILE TOTALE", f"€ {tot_utile:.2f}")
            
            for item in data:
                color = "#28a745" if item['ResaEuro'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='color: {color};'>{item['Nome']}</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("Prezzo (€)", f"{item['Prezzo']:.2f}", f"{item['VarGiorno']:.2f}%")
                    c2.metric("Resa (€)", f"{item['ResaEuro']:.2f}", f"{item['ResaPerc']:.2f}%")
        
        elif scelta == "📊 Grafici":
            st.title("📊 Analisi")
            fig = px.pie(data, values='ValoreTot', names='Nome', hole=0.4, title="Composizione")
            st.plotly_chart(fig)
            
            fig_bar = px.bar(data, x='Nome', y='ResaEuro', color='ResaEuro', 
                             color_continuous_scale=['red', 'green'], title="Utile per Titolo")
            st.plotly_chart(fig_bar)

    if st.sidebar.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()



