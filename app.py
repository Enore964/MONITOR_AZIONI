import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time
import datetime
from datetime import timedelta
import pandas as pd

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
        "URA":  {"t": "URAM.MI",   "acq": 48.68,  "q": 200,  "n": "Uranio Milano", "corr": 1.094},  
        "LDO":  {"t": "LDO.MI",    "acq": 59.855, "q": 200,  "n": "Leonardo",      "corr": 1.0},  
        "EXA":  {"t": "EXAI.MI",   "acq": 1.9317, "q": 3000, "n": "Expert AI",     "corr": 1.0},   
        "AVI":  {"t": "AVIO.MI",   "acq": 36.6,   "q": 250,  "n": "Avio Spazio",   "corr": 1.0},
        "GOLD": {"t": "PHAU.MI",   "acq": 352.79, "q": 30,   "n": "Oro Fisico",    "corr": 1.0}
    }

    st.sidebar.title("📱 Menu")
    scelta = st.sidebar.radio("Vai a:", ["📋 Lista", "📊 Grafici"])

    @st.cache_data(ttl=60) 
    def fetch_data():
        results = []
        for k, info in LISTA_TITOLI.items():
            try:
                stock = yf.Ticker(info["t"])
                h = stock.history(period="5d") 
                if not h.empty:
                    last_p = float(h['Close'].iloc[-1])
                    p_eur = last_p * info["corr"]
                    ora_it = datetime.datetime.now() + timedelta(hours=1)
                    ora_azione = ora_it.strftime('%H:%M:%S')
                    inv = info["acq"] * info["q"]
                    val = p_eur * info["q"]
                    gain = val - inv
                    prec = h['Close'].iloc[-2] * info["corr"]
                    var = ((p_eur - prec) / prec) * 100
                    results.append({
                        "Nome": info["n"], "Prezzo": p_eur, "Inv": inv,
                        "Val": val, "Gain": gain, "Var": var,
                        "Perc": (gain / inv * 100), "Ora": ora_azione
                    })
                time.sleep(0.2)
            except: continue
        return results

    # --- FUNZIONE TACHIMETRO CON SEMICERCHIO GIALLO ---
    def crea_tachimetro(valore, titolo="Utile Totale"):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", 
            value = valore,
            number = {'valueformat': '.3f', 'suffix': ' €'},
            title = {'text': titolo, 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [-5000, 5000], 'tickformat': '.0f'},
                'bar': {'color': "green" if valore >= 0 else "red"},
                'bgcolor': "yellow", # SFONDO DEL SEMICERCHIO GIALLO
                'threshold': {
                    'line': {'color': "black", 'width': 3},
                    'thickness': 0.8,
                    'value': valore
                }
            }
        ))
        fig.update_layout(
            height=350, 
            margin=dict(t=80, b=20, l=30, r=30)
        )
        return fig

    data = fetch_data()

    if data:
        df = pd.DataFrame(data)
        tot_gain = df['Gain'].sum()

        if scelta == "📋 Lista":
            st.markdown("# *Portafoglio Enore*")
            st.plotly_chart(crea_tachimetro(tot_gain), use_container_width=True)
            st.metric("UTILE ATTUALE", f"€ {tot_gain:.3f}")
            st.divider()

            for i in data:
                color = "#28a745" if i['Gain'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='margin-bottom:0; color: {color};'>{i['Nome']}</h3>", unsafe_allow_html=True)
                st.markdown(f"🕒 *Aggiornato alle: {i['Ora']}*") 
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("Prezzo", f"€ {i['Prezzo']:.3f}", f"{i['Var']:.3f}%")
                    c2.metric("Utile", f"€ {i['Gain']:.3f}", f"{i['Perc']:.3f}%")
                    st.caption(f"Valore: € {i['Val']:.3f} | Investito: € {i['Inv']:.3f}")

        elif scelta == "📊 Grafici":
            st.title("📊 Analisi Avanzata")
            st.markdown("### Analisi di *Portafoglio Enore*")
            st.plotly_chart(crea_tachimetro(tot_gain, "Riepilogo Totale"), use_container_width=True)
            st.divider()
            fig_bar = px.bar(
                df, x='Nome', y='Gain', 
                color='Gain',
                color_continuous_scale='RdYlGn', 
                text_auto='.3f',
                title="Dettaglio Utile per Singolo Titolo"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state["p_ok"] = False
        st.rerun()
