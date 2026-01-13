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
    # --- CONFIGURAZIONE ---
    # Moltiplicatore 1.15 per allineare Uranio a Milano
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
        # Ora Italiana
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
                time.sleep(0.2)
            except: continue
        return output

    dati = scarica_dati()

    if dati:
        if scelta == "Lista":
            st.title("Monitor Portafoglio")
            tot_gain = sum(i['Gain'] for i in dati)
            st.metric("UTILE TOTALE", f"Euro {tot_gain:.2f}")
            st.divider()

            for i in dati:
                with st.container(border=True):
                    col1, col2 = st.columns(2)
                    col1.subheader(i['Nome'])
                    st.caption(f"Aggiornato: {i['Ora']}")
                    col1.metric("Prezzo", f"{i['Prezzo']:.2f}", f"{i['Var']:.2f}%")
                    col2.metric("Utile", f"{i['Gain']:.2f}", f"{i['Perc']:.2f}%")

        elif scelta == "Grafici":
            st.title("Visualizzazione 3D")

            # --- GRAFICO 3D RICHIESTO ---
            # Utilizziamo Mesh3d per simulare delle colonne solide
            fig3d = go.Figure()
            for x_idx, i in enumerate(dati):
                # Creiamo un "box" 3D per ogni titolo
                fig3d.add_trace(go.Mesh3d(
                    x=[x_idx, x_idx, x_idx+0.5, x_idx+0.5, x_idx, x_idx, x_idx+0.5, x_idx+0.5],
                    y=[0, 1, 1, 0, 0, 1, 1, 0],
                    z=[0, 0, 0, 0, i['Gain'], i['Gain'], i['Gain'], i['Gain']],
                    color='green' if i['Gain'] >= 0 else 'red',
                    opacity=0.8,
                    name=i['Nome']
                ))

            fig3d.update_layout(
                scene=dict(
                    xaxis=dict(tickvals=list(range(len(dati))), ticktext=[i['Nome'] for i in dati], title="Titoli"),
                    yaxis=dict(visible=False),
                    zaxis=dict(title="Utile (Euro)")
                ),
                margin=dict(l=0, r=0, b=0, t=0)
            )
            st.plotly_chart(fig3d, use_container_width=True)

            # --- ISTOGRAMMA CLASSICO ---
            st.subheader("Rendimento Euro")
            fig_bar = px.bar(dati, x='Nome', y='Gain', color='Gain', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_bar, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state["p_ok"] = False
        st.rerun()
