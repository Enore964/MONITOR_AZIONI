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
        "JE00B1VS3770": {"ticker": "PHAU.L", "acquisto": 352.13, "quantita": 30, "nome": "Oro Fisico", "usa": False}, 
        "IE0003BJ2JS4": {"ticker": "URA", "acquisto": 48.54, "quantita": 200, "nome": "Uranio (USA Ticker)", "usa": True},  
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 59.76, "quantita": 200, "nome": "Leonardo", "usa": False},  
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 1.93, "quantita": 3000, "nome": "Expert AI", "usa": False},   
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 36.55, "quantita": 3000, "nome": "Avio Spazio", "usa": False}    
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
        usd_to_eur = get_exchange_rate()
        data_list = []
        for isin, info in STOCKS.items():
            try:
                stock = yf.Ticker(info["ticker"])
                hist = stock.history(period="5d")
                if not hist.empty:
                    raw_price = float(hist['Close'].dropna().iloc[-1])
                    
                    # Se il titolo è USA, convertiamo il prezzo attuale in Euro
                    last_price = raw_price * usd_to_eur if info["usa"] else raw_price
                    
                    prezzo_acq = info["acquisto"]
                    qta = info["quantita"]
                    
                    valore_attuale = last_price * qta
                    investito = prezzo_acq * qta
                    resa_euro = valore_attuale - investito
                    
                    # Calcolo variazione giornaliera
                    prev_close_raw = hist['Close'].dropna().iloc[-2]
                    var_giorno = ((raw_price - prev_close_raw) / prev_close_raw) * 100
                    
                    data_list.append({
                        "Nome": info["nome"], "Ticker": info["ticker"], "Prezzo": last_price, 
                        "Investito": investito, "ValoreTot": valore_attuale,
                        "VarGiorno": var_giorno, "ResaEuro": resa_euro,
                        "ResaPerc": (resa_euro / investito * 100)
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

