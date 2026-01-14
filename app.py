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

    @st.cache_data(ttl=30) 
    def fetch_data():
        results = []
        for k, info in LISTA_TITOLI.items():
            try:
                stock = yf.Ticker(info["t"])
                # Scarichiamo dati intraday con intervallo 5 minuti per il grafico
                h = stock.history(period="1d", interval="5m") 
                if h.empty: # Se mercato chiuso o errore, prendiamo ultimi 5 giorni
                    h = stock.history(period="5d")
                
                if not h.empty:
                    last_p = float(h['Close'].iloc[-1])
                    p_eur = last_p * info["corr"]
                    # Prezzi corretti per il grafico lineare
                    prezzi_storia = (h['Close'] * info["corr"]).tolist()
                    
                    ora_it = datetime.datetime.now() + timedelta(hours=1)
                    ora_azione = ora_it.strftime('%H:%M:%S')
                    inv = info["acq"] * info["q"]
                    val = p_eur * info["q"]
                    gain = val - inv
                    
                    # Calcolo variazione rispetto alla chiusura precedente
                    h_prec = stock.history(period="5d")
                    prec_close = h_prec['Close'].iloc[-2] * info["corr"]
                    var = ((p_eur - prec_close) / prec_close) * 100
                    
                    results.append({
                        "Nome": info["n"], "Prezzo": p_eur, "Inv": inv,
                        "Val": val, "Gain": gain, "Var": var,
                        "Perc": (gain / inv * 100), "Ora": ora_azione,
                        "Storia": prezzi_storia
                    })
                time.sleep(0.2)
            except: continue
        return results

    def crea_tachimetro(valore, titolo="Utile Totale"):
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = valore,
            number = {'valueformat': '.3f', 'suffix': ' €', 'font': {'size': 30, 'weight': 'bold'}},
            title = {'text': titolo, 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [-5000, 5000], 'tickformat': '.0f'},
                'bar': {'color': "green" if valore >= 0 else "red"},
                'bgcolor': "#F5F5DC", 
                'threshold': {'line': {'color': "black", 'width': 3}, 'thickness': 0.8, 'value': valore}
            }
        ))
        fig.update_layout(height=350, margin=dict(t=80, b=20, l=30, r=30))
        return fig

    def crea_sparkline(dati, colore):
        fig = go.Figure(data=go.Scatter(y=dati, mode='lines', line=dict(color=colore, width=3)))
        fig.update_layout(
            height=60, margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    data = fetch_data()

    if data:
        df = pd.DataFrame(data)
        tot_gain = df['Gain'].sum()

        if scelta == "📋 Lista":
            color_stat = "#28a745" if tot_gain >= 0 else "#dc3545"
            st.markdown(f"<h2 style='font-style: italic; font-size: 26px; white-space: nowrap; color: {color_stat};'>Portafoglio Enore</h2>", unsafe_allow_html=True)
            st.plotly_chart(crea_tachimetro(tot_gain), use_container_width=True)
            st.markdown(f"<div style='text-align: center; margin-top: -20px;'><p style='font-size: 16px; font-weight: bold; color: {color_stat};'>UTILE ATTUALE</p><p style='font-size: 32px; font-weight: bold; color: {color_stat};'>€ {tot_gain:.3f}</p></div>", unsafe_allow_html=True)
            st.divider()

            for i in data:
                if i['Gain'] >= 0:
                    bg_color = "#eaffea"; border_color = "#28a745"; text_color = "#28a745"
                else:
                    bg_color = "#ffeaea"; border_color = "#dc3545"; text_color = "#dc3545"

                st.markdown(f"<h3 style='margin-bottom:0; color: {text_color}; font-weight: bold;'>{i['Nome']}</h3>", unsafe_allow_html=True)
                st.markdown(f"🕒 *Aggiornato alle: {i['Ora']}*") 
                
                with st.container():
                    st.markdown(f"""<div style="background-color: {bg_color}; border: 2px solid {border_color}; padding: 15px; border-radius: 10px; margin-bottom: 5px;">
                        <div style="display: flex; justify-content: space-between;">
                            <div><p style="margin:0; font-size: 14px; color: black;">Prezzo</p>
                                 <p style="margin:0; font-size: 20px; font-weight: bold; color: {text_color};">€ {i['Prezzo']:.3f} <span style="font-size: 14px;">({i['Var']:.3f}%)</span></p></div>
                            <div style="text-align: right;"><p style="margin:0; font-size: 14px; color: black;">Utile</p>
                                 <p style="margin:0; font-size: 20px; font-weight: bold; color: {text_color};">€ {i['Gain']:.3f} <span style="font-size: 14px;">({i['Perc']:.3f}%)</span></p></div>
                        </div></div>""", unsafe_allow_html=True)
                    
                    # Inserimento del mini grafico (Sparkline)
                    st.plotly_chart(crea_sparkline(i['Storia'], text_color), use_container_width=True, config={'displayModeBar': False})
                    
                    st.markdown(f"""<div style="background-color: {bg_color}; border: 1px solid {border_color}; padding: 10px; border-radius: 5px; margin-top: -15px;">
                        <p style="margin: 0; font-size: 12px; color: #444; font-weight: bold;">Valore: € {i['Val']:.3f} | Investito: € {i['Inv']:.3f}</p>
                    </div><br>""", unsafe_allow_html=True)

        elif scelta == "📊 Grafici":
            st.title("📊 Analisi Avanzata")
            st.plotly_chart(crea_tachimetro(tot_gain, "Riepilogo Totale"), use_container_width=True)
            st.divider()
            fig_bar = px.bar(df, x='Nome', y='Gain', color='Gain', color_continuous_scale='RdYlGn', text_auto='.3f')
            st.plotly_chart(fig_bar, use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state["p_ok"] = False
        st.rerun()
