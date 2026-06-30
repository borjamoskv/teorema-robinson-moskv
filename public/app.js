// CORTEX Exergy Simulation Kernel
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

const MODULES = ['AST_PARSER', 'JIT_COMPILER', 'EXERGY_CORE', 'GIT_SENTINEL', 'MEMORY_VAULT'];
const MESSAGES = [
    { text: 'Optimizing recursive depth tree', type: 'stable' },
    { text: 'Dead code token purged', type: 'stable' },
    { text: 'Entropy spike detected in execution block', type: 'critical' },
    { text: 'McCabe complexity exceeded threshold', type: 'critical' },
    { text: 'Anergy levels stabilized', type: 'stable' },
    { text: 'Recompiling JIT graph', type: 'stable' },
    { text: 'Green theater patterns suppressed', type: 'stable' },
    { text: 'Bypass Narrative triggered', type: 'critical' }
];

function formatTime(date) {
    return date.toTimeString().split(' ')[0] + '.' + String(date.getMilliseconds()).padStart(3, '0');
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

    // Matrix
    DOM.mccabeVal.textContent = exergyState.mccabe;
    DOM.nestingVal.textContent = exergyState.nesting;
    DOM.deadcodeVal.textContent = exergyState.deadcode;
    DOM.entropyVal.textContent = exergyState.entropy.toFixed(3);
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

function simulateTick() {
    // Random walks for metrics
    exergyState.total = Math.max(0, Math.min(100, exergyState.total + (Math.random() - 0.45) * 2));
    exergyState.anergy = 100 - exergyState.total;
    exergyState.yield = exergyState.total / 50;

    // Occasionally change matrix
    if (Math.random() > 0.8) {
        exergyState.mccabe = Math.max(1, Math.floor(exergyState.mccabe + (Math.random() - 0.5) * 3));
        exergyState.nesting = Math.max(1, Math.floor(exergyState.nesting + (Math.random() - 0.5) * 2));
        exergyState.deadcode = Math.max(0, Math.floor(exergyState.deadcode + (Math.random() - 0.6) * 10));
        exergyState.entropy = Math.max(0, exergyState.entropy + (Math.random() - 0.48) * 0.05);
    }

    // Add random log
    if (Math.random() > 0.7) {
        const msg = MESSAGES[Math.floor(Math.random() * MESSAGES.length)];
        const mod = MODULES[Math.floor(Math.random() * MODULES.length)];
        const metric = `${(Math.random() * 10).toFixed(2)}ms`;
        addLogEntry(mod, msg.text, msg.type, metric);
    }

    updateDOM();
}

// Event Listeners
DOM.filterBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        DOM.filterBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        exergyState.filter = e.target.dataset.filter;
        renderLogs();
    });
});

// Initialization
addLogEntry('CORTEX_SYS', 'Kernel bootstrap sequence initiated', 'stable', '0.00ms');
addLogEntry('EXERGY_CORE', 'Metrics matrix synchronized', 'stable', '1.24ms');
updateDOM();
setInterval(simulateTick, 1000);
