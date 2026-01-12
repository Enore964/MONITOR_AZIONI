import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time

# --- CONFIGURAZIONE SICUREZZA ---
PASSWORD_CORRETTA = "2"

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
        else: st.error("❌ Password errata")
    return False

if check_password():
    # --- CONFIGURAZIONE TITOLI ---
    # Per l'Uranio usiamo URA (USA) ma con un 'corr' (correzione) per portarlo al valore di Milano
    STOCKS = {
        "JE00B1VS3770": {"ticker": "PHAU.MI", "acquisto": 352.79, "quantita": 30, "nome": "Oro Fisico", "usa": False, "corr": 1.0}, 
        "IE0003BJ2JS4": {"ticker": "URA", "acquisto": 48.68, "quantita": 200, "nome": "Uranio (Milano Adapt)", "usa": True, "corr": 1.165},  
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 59.855, "quantita": 200, "nome": "Leonardo", "usa": False, "corr": 1.0},  
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 1.9317, "quantita": 3000, "nome": "Expert AI", "usa": False, "corr": 1.0},   
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 36.6, "quantita": 250, "nome": "Avio Spazio", "usa": False, "corr": 1.0}    
    }

    st.sidebar.title("📱 Menu")
    scelta = st.sidebar.radio("Vai a:", ["📋 Lista", "📊 Grafici"])

    @st.cache_data(ttl=3600)
    def get_data():
        try:
            fx = yf.Ticker("USDEUR=X")
            usd_to_eur = float(fx.history(period="1d")['Close'].iloc[-1])
        except: usd_to_eur = 0.92

        data_list = []
        for isin, info in STOCKS.items():
            try:
                stock = yf.Ticker(info["ticker"])
                hist = stock.history(period="5d")
                if not hist.empty:
                    raw_price = float(hist['Close'].dropna().iloc[-1])
                    
                    # Calcolo prezzo in Euro con correzione per allineamento Milano
                    if info["usa"]:
                        prezzo_eur = (raw_price * usd_to_eur) * info["corr"]
                    else:
                        prezzo_eur = raw_price
                    
                    investito = info["acquisto"] * info["quantita"]
                    valore_tot = prezzo_eur * info["quantita"]
                    resa_eur = valore_tot - investito
                    
                    # Var Giorno (basata sul mercato nativo)
                    prev_c = hist['Close'].dropna().iloc[-2]
                    var_g = ((raw_price - prev_c) / prev_c) * 100
                    
                    data_list.append({
                        "Nome": info["nome"], "Prezzo_Eur": prezzo_eur, "Investito": investito,
                        "ValoreTot": valore_tot, "ResaEuro": resa_eur, "VarGiorno": var_g,
                        "ResaPerc": (resa_eur / investito * 100), "Ticker": info["ticker"]
                    })
                time.sleep(1)
            except: continue
        return data_list

    data = get_data()

    if data:
        if scelta == "📋 Lista":
            st.title("📋 Portafoglio")
            tot_u = sum(item['ResaEuro'] for item in data)
            
            # --- AGGIUNTA TACHIMETRO ---
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = tot_u,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Utile Totale (€)", 'font': {'size': 24}},
                gauge = {
                    'axis': {'range': [-5000, 5000], 'tickwidth': 1}, # Puoi cambiare i limiti -5000 e 5000
                    'bar': {'color': "green" if tot_u >= 0 else "red"},
                    'steps': [
                        {'range': [-5000, 0], 'color': "#FFDDDD"},
                        {'range': [0, 5000], 'color': "#DDFFDD"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': tot_u
                    }
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            # ---------------------------

            st.metric("VALORE NUMERICO", f"€ {tot_u:.2f}", delta_color="normal" if tot_u>=0 else "inverse")
            st.divider()

            for item in data:
                # ... resto del tuo codice per la lista titoli ...

        elif scelta == "📊 Grafici":
            st.title("📊 Analisi Portafoglio")
            
            # 1. Grafico a Torta (Composizione del capitale)
            st.subheader("Distribuzione Capitale")
            fig_pie = px.pie(data, values='ValoreTot', names='Nome', hole=0.4)
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

            # 2. Grafico a Barre (Resa in Euro per ogni titolo)
            st.subheader("Resa per Titolo (€)")
            fig_bar = px.bar(
                data, 
                x='Nome', 
                y='ResaEuro', 
                color='ResaEuro', 
                color_continuous_scale=['red', 'green'],
                text_auto='.2f'
            )
            # Ruota i nomi se sono troppo lunghi per lo schermo del telefono
            fig_bar.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)











