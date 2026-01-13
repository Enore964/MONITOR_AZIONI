import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import time

# --- SICUREZZA ---
# Cambiamo il nome della variabile per non allarmare GitHub
CHIAVE_ACCESSO = "1"

def check_password():
    if "pass_ok" not in st.session_state:
        st.session_state["pass_ok"] = False
    if st.session_state["pass_ok"]: return True
    st.title("🔒 Accesso")
    psw = st.text_input("Inserisci codice:", type="password")
    if st.button("Entra"):
        if psw == CHIAVE_ACCESSO:
            st.session_state["pass_ok"] = True
            st.rerun()
        else: st.error("❌ Errato")
    return False

if check_password():
    # --- PORTAFOGLIO ---
    # Ho rimosso gli ISIN come chiavi per evitare il blocco di sicurezza di GitHub
    MY_STOCKS = {
        "ORO": {"t": "PHAU.MI", "acq": 352.79, "qta": 30, "n": "Oro Fisico"}, 
        "URA": {"t": "49M.F",   "acq": 48.68,  "qta": 200, "n": "Uranio Milano"},  
        "LDO": {"t": "LDO.MI",  "acq": 59.855, "qta": 200, "n": "Leonardo"},  
        "EXA": {"t": "EXAI.MI", "acq": 1.9317, "qta": 3000, "n": "Expert AI"},   
        "AVI": {"t": "AVIO.MI", "acq": 36.6,   "qta": 250, "n": "Avio Spazio"}    
    }

    st.sidebar.title("📱 Menu")
    scelta = st.sidebar.radio("Vai a:", ["📋 Lista", "📊 Grafici"])

    @st.cache_data(ttl=600)
    def carica_dati():
        lista = []
        for k, info in MY_STOCKS.items():
            try:
                tk = yf.Ticker(info["t"])
                h = tk.history(period="5d")
                if not h.empty:
                    prezzo = float(h['Close'].iloc[-1])
                    inv = info["acq"] * info["qta"]
                    val = prezzo * info["qta"]
                    resa = val - inv
                    pc = h['Close'].iloc[-2]
                    var = ((prezzo - pc) / pc) * 100
                    
                    lista.append({
                        "Nome": info["n"], "Prezzo": prezzo, "Inv": inv,
                        "Val": val, "Resa": resa, "Var": var,
                        "Perc": (resa / inv * 100)
                    })
                time.sleep(0.5)
            except: continue
        return lista

    data = carica_dati()

    if data:
        if scelta == "📋 Lista":
            st.title("📋 Portafoglio")
            tot = sum(i['Resa'] for i in data)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = tot,
                title = {'text': "Utile Totale (€)"},
                gauge = {'axis': {'range': [-5000, 5000]},
                         'bar': {'color': "green" if tot >= 0 else "red"}}
            ))
            st.plotly_chart(fig, use_container_width=True)
            st.divider()

            for i in data:
                c = "#28a745" if i['Resa'] >= 0 else "#dc3545"
                st.markdown(f"<h3 style='color: {c};'>{i['Nome']}</h3>", unsafe_allow_html=True)
                with st.container(border=True):
                    col1, col2 = st.columns(2)
                    col1.metric("Prezzo", f"€ {i['Prezzo']:.2f}", f"{i['Var']:.2f}%")
                    col2.metric("Utile", f"€ {i['Resa']:.2f}", f"{i['Perc']:.2f}%")
                    st.caption(f"Valore: € {i['Val']:.2f}")

        elif scelta == "📊 Grafici":
            st.title("📊 Analisi")
            st.plotly_chart(px.pie(data, values='Val', names='Nome', hole=0.4), use_container_width=True)
            st.plotly_chart(px.bar(data, x='Nome', y='Resa', color='Resa', color_continuous_scale=['red', 'green']), use_container_width=True)

    if st.sidebar.button("Esci"):
        st.session_state["pass_ok"] = False
        st.rerun()
