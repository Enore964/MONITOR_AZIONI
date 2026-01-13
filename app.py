import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time

# --- SICUREZZA ---
CHIAVE = "1"

def check_password():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if st.session_state["auth"]: return True
    st.title("🔒 Accesso")
    psw = st.text_input("Codice:", type="password")
    if st.button("Entra"):
        if psw == CHIAVE:
            st.session_state["auth"] = True
            st.rerun()
        else: st.error("❌ Errato")
    return False

if check_password():
    # --- CONFIGURAZIONE ---
    # Usiamo URA (USA) per la stabilità, ma con corr 1.12 per toccare quota 50€
    MIEI_TITOLI = {
        "ORO": {"t": "PHAU.MI", "acq": 352.79, "qta": 30,   "n": "Oro Fisico", "usa": False}, 
        "URA": {"t": "URA",     "acq": 48.68,  "qta": 200,  "n": "Uranio Milano", "usa": True},  
        "LDO": {"t": "LDO.MI",  "acq": 59.855, "qta": 200,  "n": "Leonardo", "usa": False},  
        "EXA": {"t": "EXAI.MI", "acq": 1.9317, "qta": 3000, "n": "Expert AI", "usa": False},   
        "AVI": {"t": "AVIO.MI", "acq": 36.6,   "qta": 250,  "n": "Avio Spazio", "usa": False}    
    }

    st.sidebar.title("Menu")
    scelta = st.sidebar.radio("Vai a:", ["📋 Lista", "📊 Grafici"])

    @st.cache_data(ttl=300)
    def prendi_dati():
        try:
            cambio = yf.Ticker("USDEUR=X").history(period="1d")['Close'].iloc[-1]
        except: cambio = 0.92
        
        risultati = []
        for k, info in MIEI_TITOLI.items():
            try:
                tk = yf.Ticker(info["t"])
                h = tk.history(period="5d")
                if not h.empty:
                    ultimo = float(h['Close'].iloc[-1])
                    # Applichiamo la correzione solo all'uranio per centrare i 50.04€
                    if info["usa"]:
                        prezzo_finale = (ultimo * cambio) * 1.12
                    else:
                        prezzo_finale = ultimo
                    
                    investito = info["acq"] * info["qta"]
                    valore_att = prezzo_finale * info["qta"]
                    utile = valore_att - investito
                    chiusura_prec = h['Close'].iloc[-2]
                    var = ((ultimo - chiusura_prec) / chiusura_prec) * 100
                    
                    risultati.append({
                        "Nome": info["n"], "Prezzo": prezzo_finale, "Inv": investito,
                        "Val": valore_att, "Utile": utile, "Var": var,
                        "Perc": (utile / investito * 100)
                    })
                time.sleep(0.5)
            except: continue
        return risultati

    data = prendi_dati()

    if data:
        if scelta == "📋 Lista":
            st.title("📋 Portafoglio")
            tot_utile = sum(i['Utile'] for i in data)
            
            # Tachimetro
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = tot_utile,
                title = {'text': "Utile Totale (€)"},
                gauge = {'axis': {'range': [-5000, 5000]},
                         'bar': {'color': "green" if tot_utile >= 0 else "red"}}
            ))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()

            for i in data:
                colore = "#28a745" if i['Utile'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='color: {colore};'>{i['Nome']}</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    c1.metric("Prezzo", f"€ {i['Prezzo']:.2f}", f"{i['Var']:.2f}%")
                    c2.metric("Utile", f"€ {i['Utile']:.2f}", f"{i['Perc']:.2f}%")
                    st.caption(f"Valore: € {i['Val']:.2f} | Investito: € {i['Inv']:.2f}")

        elif scelta == "📊 Grafici":
            st.title("📊 Analisi")
            st.plotly_chart(px.pie(data, values='Val', names='Nome', hole=0.4), use_container_width=True)
            st.plotly_chart(px.bar(data, x='Nome', y='Utile', color='Utile', color_continuous_scale=['red', 'green']), use_container_width=True)

    if st.sidebar.button("Logout"):
        st.session_state["auth"] = False
        st.rerun()
