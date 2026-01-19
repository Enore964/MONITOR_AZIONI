import streamlit as st
import streamlit.components.v1 as components

# Configurazione pagina Streamlit
st.set_page_config(layout="wide", page_title="BITMILANO AI")

# Definizione del codice HTML/CSS/JS come stringa Python
# L'uso delle triple virgolette previene errori di interpretazione dei selettori CSS
html_content = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analizzatore ISIN - Borsa Milano</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f9fafb; }
        .card-shadow { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05); }
        .signal-compra { background-color: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
        .signal-vendi { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
        .signal-mantieni { background-color: #fef9c3; color: #a16207; border: 1px solid #fef08a; }
        .loader {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #000;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="bg-neutral-50 min-h-screen">

    <!-- Navbar -->
    <nav class="bg-white border-b px-6 py-4 sticky top-0 z-50">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <div class="flex items-center gap-2">
                <div class="bg-black text-white p-1.5 rounded">
                    <i class="fas fa-landmark text-sm"></i>
                </div>
                <h1 class="text-lg font-black tracking-tight">BIT<span class="text-blue-600">MILANO</span> AI</h1>
            </div>
            <span class="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Quotazioni in Euro (€)</span>
        </div>
    </nav>

    <main class="max-w-6xl mx-auto px-4 py-8">
        
        <!-- Input Portafoglio -->
        <div class="bg-white rounded-3xl p-8 card-shadow mb-10 border border-neutral-100">
            <div class="flex flex-col md:flex-row justify-between items-end mb-8 gap-6">
                <div class="w-full">
                    <h2 class="text-2xl font-bold text-neutral-900 mb-2">Monitoraggio Asset</h2>
                    <p class="text-sm text-neutral-500">Gestisci i tuoi titoli su Borsa Italiana</p>
                </div>
                <button onclick="analyzeAll()" id="btnAnalyze" class="w-full md:w-auto bg-black hover:bg-neutral-800 text-white font-bold py-4 px-10 rounded-2xl transition-all flex justify-center items-center gap-3">
                    <i class="fas fa-bolt" id="syncIcon"></i> AGGIORNA DATI
                </button>
            </div>
            
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="p-4 bg-neutral-50 rounded-2xl border border-neutral-100 space-y-3">
                    <label class="text-[11px] font-bold text-neutral-400 uppercase ml-1">Asset 1</label>
                    <input type="text" id="isin1" value="JE00B1VS3770" placeholder="ISIN" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl outline-none font-mono text-sm">
                    <input type="number" id="qty1" value="10" placeholder="Quantità" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl outline-none text-sm">
                </div>
                <div class="p-4 bg-neutral-50 rounded-2xl border border-neutral-100 space-y-3">
                    <label class="text-[11px] font-bold text-neutral-400 uppercase ml-1">Asset 2</label>
                    <input type="text" id="isin2" value="JE00B1VS3333" placeholder="ISIN" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl outline-none font-mono text-sm">
                    <input type="number" id="qty2" value="5" placeholder="Quantità" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl outline-none text-sm">
                </div>
                <div class="p-4 bg-neutral-50 rounded-2xl border border-neutral-100 space-y-3">
                    <label class="text-[11px] font-bold text-neutral-400 uppercase ml-1">Asset 3</label>
                    <input type="text" id="isin3" value="" placeholder="ISIN" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl outline-none font-mono text-sm">
                    <input type="number" id="qty3" value="" placeholder="Quantità" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl outline-none text-sm">
                </div>
            </div>
        </div>

        <div id="resultsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"></div>
    </main>

    <script>
        const apiKey = ""; 
        const charts = {};

        async function fetchMarketData(isin) {
            const prompt = `Analizza rigorosamente sulla Borsa di Milano (BIT) il titolo con ISIN \${isin}. Rispondi in JSON: {"nome": "string", "prezzoTesto": "string", "prezzoNumero": number, "segnale": "COMPRA"|"VENDI"|"MANTIENI", "storico": [6 numeri], "motivo": "string"}`;
            const payload = { contents: [{ parts: [{ text: prompt }] }], tools: [{ "google_search": {} }] };

            for (let i = 0; i < 3; i++) {
                try {
                    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=\${apiKey}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await response.json();
                    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
                    return JSON.parse(text.match(/\{[\\s\\S]*\}/)[0]);
                } catch (e) { await new Promise(r => setTimeout(r, 1000)); }
            }
        }

        function renderChart(canvasId, storico, segnale) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            const color = segnale === 'COMPRA' ? '#10b981' : (segnale === 'VENDI' ? '#ef4444' : '#f59e0b');
            if (charts[canvasId]) charts[canvasId].destroy();
            charts[canvasId] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['M1', 'M2', 'M3', 'M4', 'M5', 'Oggi'],
                    datasets: [{ data: storico, borderColor: color, fill: false, tension: 0.3 }]
                },
                options: { plugins: { legend: { display: false } }, scales: { x: { display: false } } }
            });
        }

        async function analyzeAll() {
            const btn = document.getElementById('btnAnalyze');
            const icon = document.getElementById('syncIcon');
            btn.disabled = true; icon.classList.add('animate-spin');
            const grid = document.getElementById('resultsGrid');
            grid.innerHTML = '';

            for (let i = 1; i <= 3; i++) {
                const isin = document.getElementById(`isin\${i}`).value.trim();
                const qty = parseFloat(document.getElementById(`qty\${i}`).value) || 0;
                if (!isin) continue;

                const cardId = `card-\${i}`;
                const canvasId = `chart-\${i}`;
                grid.innerHTML += `<div id="\${cardId}" class="bg-white rounded-3xl p-6 border border-neutral-200 card-shadow flex flex-col h-[520px]">
                    <div class="flex justify-between items-center mb-4">
                        <span class="px-3 py-1 bg-neutral-100 rounded-lg text-[10px] font-bold font-mono text-neutral-500">\${isin}</span>
                        <div id="status-\${i}" class="loader"></div>
                    </div>
                    <div id="content-\${i}" class="opacity-0 transition-opacity duration-500 flex flex-col h-full">
                        <h3 id="nome-\${i}" class="text-sm font-bold text-neutral-800 mb-1 leading-tight h-10 overflow-hidden">...</h3>
                        <span id="prezzo-\${i}" class="text-2xl font-black text-neutral-900">...</span>
                        <div class="mt-2 p-2 bg-neutral-50 rounded-xl border border-neutral-100 flex justify-between">
                            <span class="text-[10px] text-neutral-400 uppercase font-bold">Totale: <span id="totale-\${i}" class="text-indigo-600">€ 0,00</span></span>
                        </div>
                        <div class="flex-grow my-4"><canvas id="\${canvasId}"></canvas></div>
                        <div id="signal-box-\${i}" class="py-2 rounded-xl mb-4 text-center font-black text-[10px] tracking-widest uppercase">---</div>
                        <p id="motivo-\${i}" class="text-[10px] text-neutral-500 italic border-t pt-2">...</p>
                    </div>
                </div>`;

                try {
                    const data = await fetchMarketData(isin);
                    document.getElementById(`status-\${i}`).style.display = 'none';
                    document.getElementById(`content-\${i}`).classList.remove('opacity-0');
                    document.getElementById(`nome-\${i}`).innerText = data.nome;
                    document.getElementById(`prezzo-\${i}`).innerText = data.prezzoTesto;
                    document.getElementById(`motivo-\${i}`).innerText = data.motivo;
                    document.getElementById(`totale-\${i}`).innerText = (data.prezzoNumero * qty).toLocaleString('it-IT', { style: 'currency', currency: 'EUR' });
                    const sBox = document.getElementById(`signal-box-\${i}`);
                    sBox.innerText = data.segnale;
                    sBox.className = `py-2 rounded-xl mb-4 text-center font-black text-[10px] tracking-widest uppercase signal-\${data.segnale.toLowerCase()}`;
                    renderChart(canvasId, data.storico, data.segnale);
                } catch (e) { console.error(e); }
            }
            btn.disabled = false; icon.classList.remove('animate-spin');
        }
        window.onload = analyzeAll;
    </script>
</body>
</html>
"""


