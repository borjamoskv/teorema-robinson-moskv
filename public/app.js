// CORTEX Exergy Telemetry Kernel
// Level: C5-REAL JIT
// Author: borjamoskv

const DOM = {
    totalExergy: document.getElementById('total-exergy'),
    anergyLevel: document.getElementById('anergy-level'),
    exergyYield: document.getElementById('exergy-yield'),
    exergyBar: document.getElementById('exergy-bar'),
    mccabeVal: document.getElementById('mccabe-val'),
    nestingVal: document.getElementById('nesting-val'),
    deadcodeVal: document.getElementById('deadcode-val'),
    entropyVal: document.getElementById('entropy-val'),
    logContainer: document.getElementById('telemetry-log'),
    filterBtns: document.querySelectorAll('.filter-btn')
};

// State
let exergyState = {
    total: 85.0,
    anergy: 15.0,
    yield: 1.5,
    mccabe: 12,
    nesting: 3,
    deadcode: 45,
    entropy: 0.12,
    logs: [],
    filter: 'all'
};

// [C5-REAL] Variables estocásticas purgadas. Cero Anergía.

function formatTime(date) {
    return date.toTimeString().split(' ')[0] + '.' + String(date.getMilliseconds()).padStart(3, '0');
}

function flashElement(el) {
    el.classList.remove('value-flash');
    void el.offsetWidth; // trigger reflow
    el.classList.add('value-flash');
}

function updateDOM() {
    DOM.totalExergy.textContent = exergyState.total.toFixed(2) + '%';
    DOM.anergyLevel.textContent = exergyState.anergy.toFixed(2) + '%';
    DOM.exergyYield.textContent = exergyState.yield.toFixed(2) + 'x';
    DOM.exergyBar.style.width = exergyState.total + '%';
    
    // Update colors based on thresholds
    if (exergyState.total > 90) DOM.totalExergy.style.color = 'var(--stable)';
    else if (exergyState.total < 75) DOM.totalExergy.style.color = 'var(--warning)';
    else DOM.totalExergy.style.color = 'var(--accent-blue)';

    if (exergyState.anergy > 20) DOM.anergyLevel.style.color = 'var(--warning)';
    else DOM.anergyLevel.style.color = 'var(--stable)';

    // Matrix updates with flash
    if (DOM.mccabeVal.textContent !== String(exergyState.mccabe)) flashElement(DOM.mccabeVal);
    DOM.mccabeVal.textContent = exergyState.mccabe;

    if (DOM.nestingVal.textContent !== String(exergyState.nesting)) flashElement(DOM.nestingVal);
    DOM.nestingVal.textContent = exergyState.nesting;

    if (DOM.deadcodeVal.textContent !== String(exergyState.deadcode)) flashElement(DOM.deadcodeVal);
    DOM.deadcodeVal.textContent = exergyState.deadcode;

    const newEntropy = exergyState.entropy.toFixed(3);
    if (DOM.entropyVal.textContent !== newEntropy) flashElement(DOM.entropyVal);
    DOM.entropyVal.textContent = newEntropy;
}

function addLogEntry(module, text, type, metric) {
    const entry = {
        time: formatTime(new Date()),
        module, text, type, metric
    };
    exergyState.logs.unshift(entry);
    if (exergyState.logs.length > 50) exergyState.logs.pop();
    renderLogs();
}

function renderLogs() {
    DOM.logContainer.innerHTML = '';
    const filteredLogs = exergyState.logs.filter(log => {
        if (exergyState.filter === 'all') return true;
        return log.type === exergyState.filter;
    });

    filteredLogs.forEach(log => {
        const el = document.createElement('div');
        el.className = `log-entry ${log.type}`;
        el.innerHTML = `
            <div class="log-time">${log.time}</div>
            <div class="log-module">[${log.module}]</div>
            <div class="log-message">${log.text}</div>
            <div class="log-metric">${log.metric}</div>
        `;
        DOM.logContainer.appendChild(el);
    });
}

// [C5-REAL] Función estocástica simulateTick() eliminada. Cero anergía.

// Event Listeners
DOM.filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        DOM.filterBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        exergyState.filter = e.target.dataset.filter;
        renderLogs();
    });
});

// WebSocket Connection
let socket = null;

function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    socket = new WebSocket(`${protocol}//${host}:8081`);

    socket.onopen = () => {
        console.log('[CORTEX UI] Connected to telemetry WebSocket.');
        document.querySelector('.status-indicator').innerHTML = '<span class="pulse" style="background-color: var(--stable); box-shadow: 0 0 8px var(--stable);"></span> C5-REAL LINKED';
        document.querySelector('.status-indicator').style.color = 'var(--stable)';
        document.querySelector('.status-indicator').style.background = 'rgba(43, 229, 148, 0.05)';
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'telemetry') {
                exergyState.total = data.exergy;
                exergyState.anergy = data.anergy;
                exergyState.yield = data.yield;
                exergyState.mccabe = data.mccabe;
                exergyState.nesting = data.nesting;
                exergyState.deadcode = data.deadcode;
                exergyState.entropy = data.entropy;
                
                if (data.log) {
                    addLogEntry(data.log.module, data.log.text, data.log.type, data.log.metric);
                }
                updateDOM();
            }
        } catch (e) {
            console.error('[CORTEX ERROR] Failed to parse telemetry frame', e);
        }
    };

    socket.onclose = () => {
        console.log('[CORTEX UI] Telemetry WebSocket unlinked. Freezing state. NO C4-SIM ALLOWED.');
        document.querySelector('.status-indicator').innerHTML = '<span class="pulse" style="background-color: var(--warning); box-shadow: 0 0 8px var(--warning);"></span> DISCONNECTED';
        document.querySelector('.status-indicator').style.color = 'var(--warning)';
        document.querySelector('.status-indicator').style.background = 'rgba(229, 43, 43, 0.05)';
        
        // Reconexión determinista en 5000ms. Cero simulación estocástica.
        setTimeout(connectWS, 5000);
    };
}

// Initialization
addLogEntry('CORTEX_SYS', 'Kernel bootstrap sequence initiated', 'stable', '0.00ms');
addLogEntry('EXERGY_CORE', 'Metrics matrix synchronized', 'stable', '1.24ms');
updateDOM();
connectWS();
