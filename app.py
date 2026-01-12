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
    if st.session_state["password_correct"]:
        return True
    st.title("🔒 Accesso Riservato")
    password = st.text_input("Inserisci la password:", type="password")
    if st.button("Accedi"):
        if password == PASSWORD_CORRETTA:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Password errata")
    return False

if check_password():
    # --- CONFIGURAZIONE TITOLI ---
    STOCKS = {
        "JE00B1VS3770": {"ticker": "PHAU.MI", "acquisto": 180.00, "quantita": 10, "nome": "Oro Fisico"}, 
        "IE0003BJ2JS4": {"ticker": "U3O8.L", "acquisto": 48.00, "quantita": 50, "nome": "Uranio (ETF)"},  
        "IT0003856405": {"ticker": "LDO.MI", "acquisto": 15.50, "quantita": 100, "nome": "Leonardo"},  
        "IT0004496029": {"ticker": "EXAI.MI", "acquisto": 2.10, "quantita": 500, "nome": "Expert AI"},   
        "IT0005119810": {"ticker": "AVIO.MI", "acquisto": 12.00, "quantita": 80, "nome": "Avio Spazio"}    
    }

    st.set_page_config(page_title="Portfolio App", layout="centered")

    # --- MENU A TENDINA LATERALE ---
    with st.sidebar:
        st.title("📱 Navigazione")
        scelta = st.radio("Vai a:", ["📋 Lista Titoli", "📊 Analisi Grafica"])
        st.divider()
        if st.button("🔄 Forza Aggiornamento"):
            st.cache_data.clear()
            st.rerun()
        if st.button("🚪 Log out"):
            st.session_state["password_correct"] = False
            st.rerun()

    @st.cache_data(ttl=600)
    def get_data():
        data_list = []
        for isin, info in STOCKS.items():
            try:
                stock = yf.Ticker(info["ticker"])
                hist = stock.history(period="10d")
                if not hist.empty:
                    last_price = float(hist['Close'].dropna().iloc[-1])
                    prezzo_acq = info["acquisto"]
                    qta = info["quantita"]
                    
                    valid_closes = hist['Close'].dropna()
                    var_giorno = ((last_price - valid_closes.iloc[-2]) / valid_closes.iloc[-2]) * 100 if len(valid_closes) >= 2 else 0.0
                    
                    valore_attuale = last_price * qta
                    investito = prezzo_acq * qta
                    resa_euro = valore_attuale - investito
                    resa_perc = (resa_euro / investito) * 100 if investito > 0 else 0
                    
                    data_list.append({
                        "Nome": info["nome"],
                        "Ticker": info["ticker"], 
                        "Prezzo": last_price, 
                        "Investito": investito,
                        "ValoreTot": valore_attuale,
                        "VarGiorno": var_giorno,
                        "ResaEuro": resa_euro,
                        "ResaPerc": resa_perc
                    })
                time.sleep(0.2)
            except: continue
        return data_list

    data = get_data()

    if data:
        tot_investito = sum(item['Investito'] for item in data)
        tot_attuale = sum(item['ValoreTot'] for item in data)
        tot_utile_euro = tot_attuale - tot_investito
        tot_utile_perc = (tot_utile_euro / tot_investito) * 100 if tot_investito > 0 else 0

        if scelta == "📋 Lista Titoli":
            st.title("📋 I Tuoi Titoli")
            
            # Header Totale
            st.metric("UTILE TOTALE", f"€ {tot_utile_euro:.2f}", f"{tot_utile_perc:.2f}%")
            st.divider()

            for item in data:
                # Colore dinamico per il nome
                colore = "#28a745" if item['ResaEuro'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='color: {colore};'>{item['Nome']}</h3>", unsafe_allow_html=True)
                
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("Prezzo", f"€ {item['Prezzo']:.3f}", f"{item['VarGiorno']:.2f}%")
                    c2.metric("Utile", f"€ {item['ResaEuro']:.2f}", f"{item['ResaPerc']:.2f}%")
                    st.caption(f"Valore: € {item['ValoreTot']:,.2f} | Ticker: {item['Ticker']}")

        elif scelta == "📊 Analisi Grafica":
            st.title("📊 Analisi Portafoglio")
            
            # 1. Grafico Torta (Composizione)
            st.subheader("Distribuzione Capitale")
            fig_pie = px.pie(data, values='ValoreTot', names='Nome', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            

            # 2. Grafico Barre (Utili per Titolo)
            st.subheader("Confronto Utili (€)")
            fig_bar = px.bar(data, x='Nome', y='ResaEuro', 
                             color='ResaEuro', 
                             color_continuous_scale=['red', 'green'])
            st.plotly_chart(fig_bar, use_container_width=True)
            

            # 3. Gauge Totale
            st.subheader("Salute Portafoglio")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = tot_utile_euro,
                title = {'text': "Utile Totale (€)"},
                gauge = {'bar': {'color': "green" if tot_utile_euro >= 0 else "red"}}
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

    else:
        st.error("Dati non disponibili.")
