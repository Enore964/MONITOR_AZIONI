import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAZIONE SICUREZZA ---
PASSWORD_CORRETTA = "TuaPassword123"  # <--- CAMBIA QUESTA PASSWORD!

def check_password():
    """Restituisce True se l'utente ha inserito la password corretta."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Visualizza il form di login
    st.title("🔒 Accesso Riservato")
    password = st.text_input("Inserisci la password per visualizzare i titoli:", type="password")
    if st.button("Accedi"):
        if password == PASSWORD_CORRETTA:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Password errata")
    return False

# --- LOGICA DELL'APP ---
if check_password():
    # Se la password è corretta, esegui il resto dell'app
    STOCKS = {
        "JE00B1VS3770": "PHAU.MI",   # Gold
        "IE0003BJ2JS4": "NCLR.MI",   # Uranium
        "IT0003856405": "LDO.MI",    # Leonardo
        "IT0004496029": "EXAI.MI",   # Expert.ai
        "IT0005119810": "AVIO.MI"    # Avio
    }

    st.set_page_config(page_title="Il Mio Portafoglio", layout="wide")
    
    col_t1, col_t2 = st.columns([0.9, 0.1])
    col_t1.title("📈 Monitor Portafoglio")
    if col_t2.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()

    # --- DASHBOARD PREZZI ---
    st.subheader("Prezzi in Tempo Reale")
    
    @st.cache_data(ttl=60) # Aggiorna i dati ogni minuto
    def get_data():
        data_list = []
        for isin, ticker in STOCKS.items():
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                last_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                pct_change = ((last_price - prev_close) / prev_close) * 100
                data_list.append({"Ticker": ticker, "Prezzo": last_price, "Var": pct_change})
        return data_list

    current_data = get_data()
    cols = st.columns(len(current_data))
    for i, item in enumerate(current_data):
        cols[i].metric(item['Ticker'], f"€{item['Prezzo']:.3f}", f"{item['Var']:.2f}%")

    st.divider()

    # --- GRAFICO STORICO ---
    st.subheader("Analisi Storica")
    selected_isin = st.selectbox("Seleziona titolo:", list(STOCKS.keys()), format_func=lambda x: STOCKS[x])
    period = st.select_slider("Orizzonte temporale:", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="1y")

    df_hist = yf.download(STOCKS[selected_isin], period=period)
    
    if not df_hist.empty:
        fig = go.Figure(data=[go.Scatter(x=df_hist.index, y=df_hist['Close'], line=dict(color='#00ffcc'))])
        fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)