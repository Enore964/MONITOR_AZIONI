import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time
import datetime
from datetime import timedelta

# --- LOGIN ---
def check_auth():
    if "p_ok" not in st.session_state:
        st.session_state["p_ok"] = False
    if st.session_state["p_ok"]: return True
    st.title("Area Riservata")
    cod = st.text_input("Codice:", type="password")
    if st.button("Entra"):
        if cod == "1":
            st.session_state["p_ok"] = True
            st.rerun()
        else: st.error("Codice Errato")
    return False

if check_auth():
    # --- DATI ---
    TITOLI = {
        "GOLD": {"t": "PHAU.MI", "acq": 352.79, "q": 30,   "n": "Oro Fisico", "usa": False}, 
        "URA":  {"t": "URA",     "acq": 48.68,  "q": 200,  "n": "Uranio Milano", "usa": True},  
        "LDO":  {"t": "LDO.MI",  "acq": 59.855, "q": 200,  "n": "Leonardo", "usa": False},  
        "EXA":  {"t": "EXAI.MI", "acq": 1.9317, "q": 3000, "n": "Expert AI", "usa": False},   
        "AVI":  {"t": "AVIO.MI", "acq": 36.6,   "q": 250,  "n": "Avio Spazio", "usa": False}    
    }

    scelta = st.sidebar.radio("Menu", ["Lista", "Grafici"])

    @st.cache_data(ttl=60) 
    def scarica_dati():
        try:
            cambio = yf.Ticker("USDEUR=X").history(period="1d")['Close'].iloc[-1]
        except: cambio = 0.92
        output = []
        ora_it = (datetime.datetime.now() + timedelta(hours=1)).strftime('%H:%M:%S')
        for k, info in TITOLI.items():
            try:
                tk = yf.Ticker(info["t"])
                h = tk.history(period="5d")
                if not h.empty:
                    last = float(h['Close'].iloc[-1])
                    p_eur = (last * cambio * 1.15) if info["usa"] else last
                    inv = info["acq"] * info["q"]
                    val = p_eur * info["q"]
                    guadagno = val - inv
                    var = ((last - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
                    output.append({
                        "Nome": info["n"], "Prezzo": p_eur, "Inv": inv,
                        "Val": val, "Gain": guadagno, "Var": var,
                        "Perc": (guadagno / inv * 100), "Ora": ora_it
                    })
                time.sleep(0.1)
            except: continue
        return output

    data = scarica_dati()

    if data:
        if scelta == "Lista":
            st.title("Monitor Portafoglio")
            tot_gain = sum(i['Gain'] for i in data)
            
            # --- TACHIMETRO UTILE TOTALE ---
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number", value = tot_gain,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Utile Totale (EUR)"},
                gauge = {
                    'axis': {'range': [-5000, 5000]},
                    'bar': {'color': "green" if tot_gain >= 0 else "red"},
                    'steps': [
                        {'range': [-5000, 0], 'color': "mistyrose"},
                        {'range': [0, 5000], 'color': "honeydew"}
                    ],
                }
            ))
            fig_gauge.update_layout(height=350)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.metric("GUADAGNO ATTUALE", f"EUR {tot_gain:.2f}")
            st.divider()

            for i in data:
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.subheader(i['Nome'])
                    c1.metric("Prezzo", f"{i['Prezzo']:.2f}", f"{i['Var']:.2f}%")
                    c2.metric("Utile", f"{i['Gain']:.2f}", f"{i['Perc']:.2f}%")

        elif scelta == "Grafici":
            st.title("Visualizzazione 3D e Analisi")
            
            # --- GRAFICO 3D SOLIDO ---
            st.subheader("Performance 3D")
            # Creiamo un set di dati per le coordinate 3D
            fig3d = go.Figure(data=[go.Bar3d(
                x=[i['Nome'] for i in data],
                y=[0] * len(data),
                z=[i['Gain'] for i in data],
                width=0.5,
                depth=0.5,
                marker=dict(color=[i['Gain'] for i in data], colorscale='RdYlGn')
            )] if hasattr(go, 'Bar3d') else [go.Bar(
                x=[i['Nome'] for i in data],
                y=[i['Gain'] for i in data],
                marker=dict(color=[i['Gain'] for i in data], colorscale='RdYlGn')
            )])
            
            # Fallback per garantire la visualizzazione se Bar3d non e disponibile
            if not hasattr(go, 'Bar3d'):
                fig3d = px.bar(data, x='Nome', y='Gain', color='Gain', 
                               template="plotly_dark", color_continuous_scale='RdYlGn')
                fig3d.update_layout(title="Rendimento (Visualizzazione Ottimizzata)")

            st.plotly_chart(fig3d, use_container_width=True)

            # --- RIPARTIZIONE PESI ---
            st.subheader("Distribuzione Capitale")
            fig_pie = px.pie(data, values='Val', names='Nome', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state["p_ok"] = False
        st.rerun()
