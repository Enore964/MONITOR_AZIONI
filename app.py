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
        body { font-family: 'Inter', sans-serif; }
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
                <!-- Titolo 1 -->
                <div class="p-4 bg-neutral-50 rounded-2xl border border-neutral-100 space-y-3">
                    <label class="text-[11px] font-bold text-neutral-400 uppercase ml-1">Asset 1</label>
                    <input type="text" id="isin1" value="JE00B1VS3770" placeholder="ISIN" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:ring-2 focus:ring-black outline-none font-mono text-sm">
                    <input type="number" id="qty1" value="10" placeholder="Quantità" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:ring-2 focus:ring-black outline-none text-sm">
                </div>
                <!-- Titolo 2 -->
                <div class="p-4 bg-neutral-50 rounded-2xl border border-neutral-100 space-y-3">
                    <label class="text-[11px] font-bold text-neutral-400 uppercase ml-1">Asset 2</label>
                    <input type="text" id="isin2" value="JE00B1VS3333" placeholder="ISIN" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:ring-2 focus:ring-black outline-none font-mono text-sm">
                    <input type="number" id="qty2" value="5" placeholder="Quantità" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:ring-2 focus:ring-black outline-none text-sm">
                </div>
                <!-- Titolo 3 -->
                <div class="p-4 bg-neutral-50 rounded-2xl border border-neutral-100 space-y-3">
                    <label class="text-[11px] font-bold text-neutral-400 uppercase ml-1">Asset 3</label>
                    <input type="text" id="isin3" value="" placeholder="ISIN" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:ring-2 focus:ring-black outline-none font-mono text-sm">
                    <input type="number" id="qty3" value="" placeholder="Quantità" class="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:ring-2 focus:ring-black outline-none text-sm">
                </div>
            </div>
        </div>

        <!-- Risultati -->
        <div id="resultsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <!-- Cards dinamiche -->
        </div>
    </main>

    <script>
        const apiKey = ""; 
        const charts = {};

        async function fetchMarketData(isin) {
            const prompt = `Analizza rigorosamente sulla Borsa di Milano (BIT) il titolo con ISIN ${isin}.
            1. Nome completo del titolo/ETF/ETC.
            2. Prezzo attuale in EURO (€) come stringa (es. "123,45 €").
            3. Estrai solo il valore numerico del prezzo per calcoli (es. 123.45).
            4. Segnale operativo: "COMPRA", "VENDI" o "MANTIENI".
            5. Andamento storico mensile (6 numeri).
            6. Motivazione strategica in italiano.
            Rispondi solo in JSON: {
                "nome": "string",
                "prezzoTesto": "string",
                "prezzoNumero": number,
                "segnale": "COMPRA"|"VENDI"|"MANTIENI",
                "storico": [num1, num2, num3, num4, num5, num6],
                "motivo": "string"
            }`;

            const payload = {
                contents: [{ parts: [{ text: prompt }] }],
                tools: [{ "google_search": {} }]
            };

            let delay = 1000;
            for (let i = 0; i < 5; i++) {
                try {
                    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await response.json();
                    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
                    const cleanJson = text.match(/\{[\s\S]*\}/)[0];
                    return JSON.parse(cleanJson);
                } catch (e) {
                    if (i === 4) throw e;
                    await new Promise(r => setTimeout(r, delay));
                    delay *= 2;
                }
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
                    datasets: [{
                        data: storico,
                        borderColor: color,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 3,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { ticks: { font: { size: 8 } } } }
                }
            });
        }

        async function analyzeAll() {
            const btn = document.getElementById('btnAnalyze');
            const icon = document.getElementById('syncIcon');
            btn.disabled = true;
            icon.classList.add('animate-spin');

            const grid = document.getElementById('resultsGrid');
            grid.innerHTML = '';

            for (let i = 1; i <= 3; i++) {
                const isin = document.getElementById(`isin${i}`).value.trim();
                const qty = parseFloat(document.getElementById(`qty${i}`).value) || 0;
                if (!isin) continue;

                const cardId = `card-${i}`;
                const canvasId = `chart-${i}`;
                
                grid.innerHTML += `
                    <div id="${cardId}" class="bg-white rounded-3xl p-6 border border-neutral-200 card-shadow flex flex-col h-[560px]">
                        <div class="flex justify-between items-center mb-4">
                            <span class="px-3 py-1 bg-neutral-100 rounded-lg text-[10px] font-bold font-mono text-neutral-500">${isin}</span>
                            <div id="status-${i}" class="loader"></div>
                        </div>
                        
                        <div id="content-${i}" class="opacity-0 transition-opacity duration-500 flex flex-col h-full">
                            <h3 id="nome-${i}" class="text-sm font-bold text-neutral-800 mb-1 leading-tight h-10 overflow-hidden">...</h3>
                            
                            <div class="flex flex-col mb-4">
                                <span id="prezzo-${i}" class="text-2xl font-black text-neutral-900">...</span>
                                <div class="flex justify-between items-center mt-2 p-2 bg-neutral-50 rounded-xl border border-neutral-100">
                                    <div class="flex flex-col">
                                        <span class="text-[9px] font-bold text-neutral-400 uppercase">Quantità</span>
                                        <span class="text-xs font-bold text-neutral-700">${qty} pz</span>
                                    </div>
                                    <div class="flex flex-col text-right">
                                        <span class="text-[9px] font-bold text-neutral-400 uppercase">Valore Totale</span>
                                        <span id="totale-${i}" class="text-xs font-black text-indigo-600">€ 0,00</span>
                                    </div>
                                </div>
                            </div>

                            <div class="flex-grow mb-4">
                                <p class="text-[10px] font-bold text-neutral-400 uppercase mb-2 tracking-widest text-center">Trend Milano</p>
                                <div class="h-32 w-full">
                                    <canvas id="${canvasId}"></canvas>
                                </div>
                            </div>

                            <div id="signal-box-${i}" class="py-3 rounded-2xl mb-4 text-center font-black text-xs tracking-[0.2em] uppercase">
                                ---
                            </div>
                            
                            <p id="motivo-${i}" class="text-[11px] text-neutral-500 italic leading-snug border-t pt-3">...</p>
                        </div>
                    </div>
                `;

                try {
                    const data = await fetchMarketData(isin);
                    document.getElementById(`status-${i}`).style.display = 'none';
                    document.getElementById(`content-${i}`).classList.remove('opacity-0');
                    document.getElementById(`nome-${i}`).innerText = data.nome;
                    document.getElementById(`prezzo-${i}`).innerText = data.prezzoTesto;
                    document.getElementById(`motivo-${i}`).innerText = `"${data.motivo}"`;
                    
                    const totale = (data.prezzoNumero * qty).toLocaleString('it-IT', { style: 'currency', currency: 'EUR' });
                    document.getElementById(`totale-${i}`).innerText = totale;
                    
                    const segnale = data.segnale.toUpperCase();
                    const sBox = document.getElementById(`signal-box-${i}`);
                    sBox.innerText = segnale;
                    sBox.className = `py-3 rounded-2xl mb-4 text-center font-black text-xs tracking-[0.2em] uppercase signal-${segnale.toLowerCase()}`;
                    renderChart(canvasId, data.storico, segnale);
                } catch (err) {
                    document.getElementById(cardId).innerHTML = `<div class="flex flex-center h-full text-neutral-300 italic text-xs">Errore dati</div>`;
                }
            }
            btn.disabled = false;
            icon.classList.remove('animate-spin');
        }

        window.onload = analyzeAll;
    </script>
</body>
</html>

