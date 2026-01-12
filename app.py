import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time

# --- CONFIGURAZIONE SICUREZZA ---
PASSWORD_CORRETTA = "1"

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
        "JE00B1VS3770": {"ticker": "PHAU.MI", "acquisto": 352.13, "quantita": 30, "nome": "Oro Fisico", "usa": False, "corr": 1.0}, 
        "IE0003BJ2JS4": {"ticker": "URA", "acquisto": 48.54, "quantita": 200, "nome": "Uranio (Milano Adapt)", "usa": True, "corr": 1.162},  
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 59.76, "quantita": 200, "nome": "Leonardo", "usa": False, "corr": 1.0},  
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 1.93, "quantita": 3000, "nome": "Expert AI", "usa": False, "corr": 1.0},   
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 36.55, "quantita": 250, "nome": "Avio Spazio", "usa": False, "corr": 1.0}    
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
            st.metric("UTILE TOTALE", f"€ {tot_u:.2f}", delta_color="normal" if tot_u>=0 else "inverse")
            st.divider()

            for item in data:
                color = "#28a745" if item['ResaEuro'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='color: {color};'>{item['Nome']}</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("Prezzo (€)", f"{item['Prezzo_Eur']:.2f}", f"{item['VarGiorno']:.2f}%")
                    c2.metric("Utile (€)", f"{item['ResaEuro']:.2f}", f"{item['ResaPerc']:.2f}%")
                    st.caption(f"Investito: € {item['Investito']:.2f} | Valore: € {item['ValoreTot']:.2f}")

        elif scelta == "📊 Analisi Grafica":
            st.title("📊 Analisi Portafoglio")
            
            # 1. Grafico Torta (Distribuzione Capitale)
            st.subheader("Distribuzione Capitale")
            fig_pie = px.pie(data, values='ValoreTot', names='Nome', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

            # 2. Grafico Barre (Utili/Perdite) - CORRETTO
            st.subheader("Confronto Utili Reali (€)")
            # Ordiniamo i dati per vedere chi guadagna di più
            data_sorted = sorted(data, key=lambda x: x['ResaEuro'])
            
            fig_bar = px.bar(data_sorted, 
                             x='Nome', 
                             y='ResaEuro', 
                             color='ResaEuro',
                             text_auto='.2f', # Mostra il valore sopra la barra
                             color_continuous_scale=['red', 'yellow', 'green'],
                             labels={'ResaEuro': 'Utile Netto (€)'})
            
            # Miglioriamo l'estetica del grafico a barre
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

            # 3. Gauge di Salute Totale
            st.subheader("Rendimento Totale")
            tot_u = sum(item['ResaEuro'] for item in data)
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = tot_u,
                delta = {'reference': 0},
                gauge = {'axis': {'range': [None, max(tot_u*2, 1000)]},
                         'bar': {'color': "green" if tot_u >= 0 else "red"}}
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)



