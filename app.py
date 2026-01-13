import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time
import datetime
from datetime import timedelta

# --- ACCESSO ---
CHIAVE_SITO = "1"

def login():
    if "p_ok" not in st.session_state:
        st.session_state["p_ok"] = False
    if st.session_state["p_ok"]: return True
    st.title("🔒 Area Riservata")
    cod = st.text_input("Codice:", type="password")
    if st.button("Entra"):
        if cod == CHIAVE_SITO:
            st.session_state["p_ok"] = True
            st.rerun()
        else: st.error("❌ Errato")
    return False

if login():
    # --- DATI PORTAFOGLIO ---
    LISTA_TITOLI = {
        "GOLD": {"t": "PHAU.MI", "acq": 352.79, "q": 30,   "n": "Oro Fisico", "usa": False}, 
        "URA":  {"t": "URA",     "acq": 48.68,  "q": 200,  "n": "Uranio Milano", "usa": True},  
        "LDO":  {"t": "LDO.MI",  "acq": 59.855, "q": 200,  "n": "Leonardo", "usa": False},  
        "EXA":  {"t": "EXAI.MI", "acq": 1.9317, "q": 3000, "n": "Expert AI", "usa": False},   
        "AVI":  {"t": "AVIO.MI", "acq": 36.6,   "q": 250,  "n": "Avio Spazio", "usa": False}    
    }

    st.sidebar.title("📱 Menu")
    scelta = st.sidebar.radio("Vai a:", ["📋 Lista", "📊 Grafici"])

    @st.cache_data(ttl=60) 
    def fetch_data():
        try:
            ex = yf.Ticker("USDEUR=X").history(period="1d")['Close'].iloc[-1]
        except: ex = 0.92
        
        results = []
        ora_it = datetime.datetime.now() + timedelta(hours=1)
        ora_attuale = ora_it.strftime('%H:%M:%S')
        
        for k, info in LISTA_TITOLI.items():
            try:
                stock = yf.Ticker(info["t"])
                h = stock.history(period="5d")
                if not h.empty:
                    last_p = float(h['Close'].iloc[-1])
                    if info["usa"]:
                        p_eur = (last_p * ex) * 1.15 
                    else:
                        p_eur = last_p
                    
                    inv = info["acq"] * info["q"]
                    val = p_eur * info["q"]
                    gain = val - inv
                    prec = h['Close'].iloc[-2]
                    var = ((last_p - prec) / prec) * 100
                    
                    results.append({
                        "Nome": info["n"], "Prezzo": p_eur, "Inv": inv,
                        "Val": val, "Gain": gain, "Var": var,
                        "Perc": (gain / inv * 100), "Ora": ora_attuale
                    })
                time.sleep(0.4)
            except: continue
        return results

    data = fetch_data()

    if data:
        if scelta == "📋 Lista":
            st.title("📋 Portafoglio")
            tot_gain = sum(i['Gain'] for i in data)
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = tot_gain,
                title = {'text': "Utile Totale (€)"},
                gauge = {'axis': {'range': [-5000, 5000]},
                         'bar': {'color': "green" if tot_gain >= 0 else "red"}}
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.metric("UTILE ATTUALE", f"€ {tot_gain:.2f}")
            st.divider()

            for i in data:
                color = "#28a745" if i['Gain'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='margin-bottom:0; color: {color};'>{i['Nome']}</h3>", unsafe_allow_html=True)
                st.caption(f"🕒 Aggiornato alle: {i['Ora']}") 
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("Prezzo", f"€ {i['Prezzo']:.2f}", f"{i['Var']:.2f}%")
                    c2.metric("Utile", f"€ {i['Gain']:.2f}", f"{i['Perc']:.2f}%")
                    st.caption(f"Valore: € {i['Val']:.2f}")

        elif scelta == "📊 Grafici":
            st.title("📊 Analisi Avanzata")
            
            # 1. MAPPA TREEMAP (Molto professionale)
            st.subheader("Mappa del Portafoglio (Dimensione = Valore)")
            fig_tree = px.treemap(
                data, 
                path=['Nome'], 
                values='Val',
                color='Gain',
                color_continuous_scale='RdYlGn',
                hover_data=['Perc']
            )
            st.plotly_chart(fig_tree, use_container_width=True)

            # 2. GRAFICO A BOLLE (Effetto dinamico)
            st.subheader("Rendimento vs Dimensione Investimento")
            fig_bubble = px.scatter(
                data, 
                x="Nome", 
                y="Gain",
                size="Val", 
                color="Gain",
                hover_name="Nome", 
                size_max=60,
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_bubble, use_container_width=True)

            # 3. BARRE CLASSICHE
            st.subheader("Utile per Titolo (€)")
            fig_bar = px.bar(data, x='Nome', y='Gain', color='Gain', 
                             color_continuous_scale='RdYlGn', text_auto='.2f')
            st.plotly_chart(fig_bar, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state["p_ok"] = False
        st.rerun()
