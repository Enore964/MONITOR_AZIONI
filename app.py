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
    STOCKS = {
        "JE00B1VS3770": {"ticker": "PHAU.MI", "acquisto": 352.79, "quantita": 30, "nome": "Oro Fisico", "usa": False, "corr": 1.0}, 
        "IE0003BJ2JS4": {"ticker": "URA", "acquisto": 48.68, "quantita": 200, "nome": "Uranio (Milano Adapt)", "usa": True, "corr": 1.17},  
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 59.855, "quantita": 200, "nome": "Leonardo", "usa": False, "corr": 1.0},  
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 1.9317, "quantita": 3000, "nome": "Expert AI", "usa": False, "corr": 1.0},   
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 36.6, "quantita": 250, "nome": "Avio Spazio", "usa": False, "corr": 1.0}    
    }

    st.sidebar.title("📱 Menu")
    scelta = st.sidebar.radio("Vai a:", ["📋 Lista", "📊 Grafici"])

    @st.cache_data(ttl=300)
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
                    if info["usa"]:
                        prezzo_eur = (raw_price * usd_to_eur) * info["corr"]
                    else:
                        prezzo_eur = raw_price
                    
                    investito = info["acquisto"] * info["quantita"]
                    valore_tot = prezzo_eur * info["quantita"]
                    resa_eur = valore_tot - investito
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
            
            # --- TACHIMETRO ---
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = tot_u,
                title = {'text': "Utile Totale (€)", 'font': {'size': 24}},
                gauge = {
                    'axis': {'range': [-5000, 5000]},
                    'bar': {'color': "green" if tot_u >= 0 else "red"},
                    'steps': [
                        {'range': [-5000, 0], 'color': "#FFDDDD"},
                        {'range': [0, 5000], 'color': "#DDFFDD"}
                    ]
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.metric("VALORE ATTUALE", f"€ {tot_u:.2f}", delta_color="normal" if tot_u>=0 else "inverse")
            st.divider()

            for item in data:
                color = "#28a745" if item['ResaEuro'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='color: {color};'>{item['Nome']}</h3>", unsafe_allow_html=True)
                with st.container(border=True):
    c1, c2 = st.columns(2)
    c1.metric("Prezzo (€)", f"{item['Prezzo_Eur']:.2f}", f"{item['VarGiorno']:.2f}%")
    c2.metric("Utile (€)", f"{item['ResaEuro']:.2f}", f"{item['ResaPerc']:.2f}%")
    
    # AGGIUNGI QUESTA RIGA QUI SOTTO:
    if "Uranio" in item['Nome']:
        st.info(f"Dati USA: {item['Ticker']} quota {item['Prezzo_Eur']/1.162:.2f}$ | Cambio usato: {item['Prezzo_Eur']/1.162/raw_price:.4f}")
    
    st.caption(f"Investito: € {item['Investito']:.2f} | Valore: € {item['ValoreTot']:.2f}")

        elif scelta == "📊 Grafici":
            st.title("📊 Analisi Portafoglio")
            
            st.subheader("Distribuzione Capitale")
            fig_pie = px.pie(data, values='ValoreTot', names='Nome', hole=0.4)
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

            st.subheader("Resa per Titolo (€)")
            fig_bar = px.bar(
                data, 
                x='Nome', 
                y='ResaEuro', 
                color='ResaEuro', 
                color_continuous_scale=['red', 'green'],
                text_auto='.2f'
            )
            fig_bar.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    if st.sidebar.button("Log out"):
        st.session_state["password_correct"] = False
        st.rerun()




