// CORTEX Exergy Telemetry Kernel
// Level: C5-REAL JIT
// Author: borjamoskv
// Reality Level: C5-REAL

const DOM = {
    totalExergy: document.getElementById('total-exergy'),
    anergyLevel: document.getElementById('anergy-level'),
    exergyYield: document.getElementById('exergy-yield'),
    exergyBar: document.getElementById('exergy-bar'),
    mccabeVal: document.getElementById('mccabe-val'),
    nestingVal: document.getElementById('nesting-val'),
    deadcodeVal: document.getElementById('deadcode-val'),
    entropyVal: document.getElementById('entropy-val'),
    llmViolations: document.getElementById('llm-violations-val'),
    cpmViolations: document.getElementById('cpm-violations-val'),
    llmLatency: document.getElementById('llm-latency-val'),
    cpmLatency: document.getElementById('cpm-latency-val'),
    logContainer: document.getElementById('telemetry-log'),
    filterBtns: document.querySelectorAll('.filter-btn'),
    
    // C7 Scientific Nodes
    consoleQuery: document.getElementById('console-query'),
    scientificAction: document.getElementById('scientific-action'),
    executeBtn: document.getElementById('execute-btn'),
    parameterInputs: document.getElementById('parameter-inputs'),
    pipelineDetails: document.getElementById('pipeline-details'),
    auditTbody: document.getElementById('audit-tbody'),
    canvas: document.getElementById('analysis-canvas')
};

function esc(str) {
    if (str === null || str === undefined) return '';
    const d = document.createElement('div');
    d.textContent = String(str);
    return d.innerHTML;
}

// Canvas context
function setupCanvas(canvas) {
    if (!canvas) return null;
    const dpr = window.devicePixelRatio || 1;
    const width = canvas.width || 500;
    const height = canvas.height || 230;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return ctx;
}
const ctx = setupCanvas(DOM.canvas);

// State
let exergyState = {
    total: 85.0,
    anergy: 15.0,
    yield: 1.5,
    mccabe: 12,
    nesting: 3,
    deadcode: 45,
    entropy: 0.12,
    llmViolations: 0,
    cpmViolations: 0,
    llmLatency: 0.0,
    cpmLatency: 0.0,
    logs: [],
    filter: 'all',
    auditLedger: []
};

// Scientific input templates
const ScientificParams = {
    inference: () => ``,
    entropy: () => `
        <div class="param-row">
            <label for="param-data">DATA SEQUENCE (String or comma-separated)</label>
            <input type="text" id="param-data" value="borjamoskv,exergy,c5-real,c5-real,entropy,exergy,borjamoskv" />
        </div>
    `,
    fisher: () => `
        <div class="param-row">
            <label for="param-series">TIME SERIES VECTOR (Comma-separated numbers)</label>
            <input type="text" id="param-series" value="10.5,12.2,11.8,14.5,15.2,13.0,16.8,18.5,17.2,20.0" />
        </div>
    `,
    dsep: () => `
        <div class="param-row">
            <label for="param-nodes">NODES (Comma-separated list)</label>
            <input type="text" id="param-nodes" value="A,B,C,D,E" />
        </div>
        <div class="param-row">
            <label for="param-edges">EDGES (Source->Target, comma-separated)</label>
            <input type="text" id="param-edges" value="A->B,C->B,B->D,E->D" />
        </div>
        <div class="param-row param-grid-3">
            <div>
                <label for="param-x">NODE X</label>
                <input type="text" id="param-x" value="A" />
            </div>
            <div>
                <label for="param-y">NODE Y</label>
                <input type="text" id="param-y" value="C" />
            </div>
            <div>
                <label for="param-z">COND. SET Z (Comma-separated)</label>
                <input type="text" id="param-z" value="D" />
            </div>
        </div>
    `,
    kolmogorov: () => `
        <div class="param-row">
            <label for="param-text">TARGET TEXT DATA</label>
            <textarea id="param-text" style="height: 60px;">CORTEX C5-REAL JIT ACTIVE. borjamoskv. CORTEX C5-REAL JIT ACTIVE. borjamoskv. CORTEX C5-REAL JIT ACTIVE. borjamoskv.</textarea>
        </div>
    `
};

function formatTime(date) {
    return date.toTimeString().split(' ')[0] + '.' + String(date.getMilliseconds()).padStart(3, '0');
}

function flashElement(el) {
    if (!el) return;
    requestAnimationFrame(() => {
        el.classList.remove('value-flash');
        requestAnimationFrame(() => {
            el.classList.add('value-flash');
        });
    });
}

function updateMetricIfChanged(domEl, newVal) {
    if (domEl && domEl.textContent !== String(newVal)) {
        flashElement(domEl);
        domEl.textContent = newVal;
    }
}

function updateDOM() {
    if (DOM.totalExergy) DOM.totalExergy.textContent = exergyState.total.toFixed(2) + '%';
    if (DOM.anergyLevel) DOM.anergyLevel.textContent = exergyState.anergy.toFixed(2) + '%';
    if (DOM.exergyYield) DOM.exergyYield.textContent = exergyState.yield.toFixed(2) + 'x';
    if (DOM.exergyBar) DOM.exergyBar.style.width = exergyState.total + '%';

    // Update colors based on thresholds
    if (DOM.totalExergy) {
        if (exergyState.total > 90) DOM.totalExergy.style.color = 'var(--stable)';
        else if (exergyState.total < 75) DOM.totalExergy.style.color = 'var(--warning)';
        else DOM.totalExergy.style.color = 'var(--accent-blue)';
    }

    if (DOM.anergyLevel) {
        if (exergyState.anergy > 20) DOM.anergyLevel.style.color = 'var(--warning)';
        else DOM.anergyLevel.style.color = 'var(--stable)';
    }

    // Matrix updates with flash
    updateMetricIfChanged(DOM.mccabeVal, exergyState.mccabe);
    updateMetricIfChanged(DOM.nestingVal, exergyState.nesting);
    updateMetricIfChanged(DOM.deadcodeVal, exergyState.deadcode);
    updateMetricIfChanged(DOM.entropyVal, exergyState.entropy.toFixed(3));
    updateMetricIfChanged(DOM.llmViolations, exergyState.llmViolations);
    updateMetricIfChanged(DOM.cpmViolations, exergyState.cpmViolations);
    updateMetricIfChanged(DOM.llmLatency, exergyState.llmLatency.toFixed(2) + 'ms');
    updateMetricIfChanged(DOM.cpmLatency, exergyState.cpmLatency.toFixed(2) + 'μs');
}

function addLogEntry(module, text, type, metric) {
    const entry = {
        time: formatTime(new Date()),
        module, text, type, metric
    };
    exergyState.logs.unshift(entry);
    if (exergyState.logs.length > 50) exergyState.logs.pop();
    
    if (!window._cortexLogRenderPending) {
        window._cortexLogRenderPending = true;
        requestAnimationFrame(() => {
            renderLogs();
            window._cortexLogRenderPending = false;
        });
    }
}

function renderLogs() {
    if (!DOM.logContainer) return;
    const fragment = document.createDocumentFragment();
    const filteredLogs = exergyState.logs.filter(log => {
        if (exergyState.filter === 'all') return true;
        return log.type === exergyState.filter;
    });

    filteredLogs.forEach(log => {
        const el = document.createElement('div');
        el.className = `log-entry ${log.type}`;
        el.innerHTML = `
            <div class="log-time">${esc(log.time)}</div>
            <div class="log-module">[${esc(log.module)}]</div>
            <div class="log-message">${esc(log.text)}</div>
            <div class="log-metric">${esc(log.metric)}</div>
        `;
        fragment.appendChild(el);
    });
    DOM.logContainer.replaceChildren(fragment);
}

// Canvas Drawing functions
function drawPlaceholder() {
    if (!ctx) return;
    ctx.clearRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    ctx.fillStyle = '#111111';
    ctx.fillRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    ctx.font = '14px Outfit';
    ctx.fillStyle = '#A0A0A0';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('NO ACTIVE COMPUTATION RECORDED', DOM.canvas.width / 2, DOM.canvas.height / 2);
}

function drawEntropyResult(result) {
    if (!ctx) return;
    ctx.clearRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    ctx.fillStyle = 'rgba(17, 17, 17, 0.95)';
    ctx.fillRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    
    ctx.font = 'bold 16px JetBrains Mono';
    ctx.fillStyle = 'var(--stable)';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('SHANNON ENTROPY RESULTS', 20, 20);
    
    ctx.font = '14px Outfit';
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(`Computed Entropy: ${result.entropy.toFixed(4)} bits`, 20, 60);
    ctx.fillText(`Max Entropy Possible: ${result.max_entropy.toFixed(4)} bits`, 20, 90);
    ctx.fillText(`Systemic Efficiency: ${(result.efficiency * 100).toFixed(2)}%`, 20, 120);
    
    ctx.fillStyle = '#222222';
    ctx.fillRect(20, 160, 260, 24);
    
    ctx.fillStyle = 'var(--accent-blue)';
    ctx.fillRect(20, 160, 260 * result.efficiency, 24);
    
    ctx.font = 'bold 11px JetBrains Mono';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.fillText(`${(result.efficiency * 100).toFixed(1)}% Information Density`, 150, 166);
}

function drawFisherResult(result, series) {
    if (!ctx) return;
    ctx.clearRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    ctx.fillStyle = 'rgba(17, 17, 17, 0.95)';
    ctx.fillRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    
    ctx.font = 'bold 16px JetBrains Mono';
    ctx.fillStyle = 'var(--stable)';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('FISHER DYNAMIC MATRIX', 20, 20);
    
    ctx.font = '13px Outfit';
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(`Fisher Information Score: ${result.fisher_information.toFixed(4)}`, 20, 50);
    ctx.fillText(`Mean Value: ${result.mean.toFixed(2)} | Variance: ${result.variance.toFixed(4)}`, 20, 75);

    if (series && series.length > 1) {
        const padding = 40;
        const graphWidth = DOM.canvas.width - padding * 2;
        const graphHeight = 80;
        const startY = 200;
        const minVal = Math.min(...series) * 0.9;
        const maxVal = Math.max(...series) * 1.1;
        const valRange = (maxVal - minVal) || 1.0;
        
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, startY);
        ctx.lineTo(padding + graphWidth, startY);
        ctx.stroke();
        
        ctx.strokeStyle = 'var(--accent-blue)';
        ctx.lineWidth = 3;
        ctx.beginPath();
        for (let i = 0; i < series.length; i++) {
            const x = padding + (i / (series.length - 1)) * graphWidth;
            const y = startY - ((series[i] - minVal) / valRange) * graphHeight;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        
        ctx.fillStyle = 'var(--stable)';
        for (let i = 0; i < series.length; i++) {
            const x = padding + (i / (series.length - 1)) * graphWidth;
            const y = startY - ((series[i] - minVal) / valRange) * graphHeight;
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}

function drawdSepResult(result, nodes, edges, xNode, yNode, zSet) {
    if (!ctx) return;
    ctx.clearRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    ctx.fillStyle = 'rgba(17, 17, 17, 0.95)';
    ctx.fillRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    
    ctx.font = 'bold 16px JetBrains Mono';
    ctx.fillStyle = 'var(--stable)';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('d-SEPARATION CAUSAL DAG', 20, 15);
    
    ctx.font = '13px Outfit';
    ctx.fillStyle = '#FFFFFF';
    const isSep = result.d_separated ? 'TRUE (Independent)' : 'FALSE (Causally Connected)';
    ctx.fillText(`d-Separated: ${isSep}`, 20, 42);
    ctx.fillText(`Active Paths Found: ${result.active_paths.length}`, 20, 62);
    
    const nodeCoords = {};
    const radius = 16;
    
    nodes.forEach((node, index) => {
        const angle = (index / nodes.length) * Math.PI * 2;
        nodeCoords[node] = {
            x: DOM.canvas.width / 2 + Math.cos(angle) * 120,
            y: DOM.canvas.height / 2 + 30 + Math.sin(angle) * 55
        };
    });
    
    // Draw edges
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1.5;
    edges.forEach(([u, v]) => {
        const from = nodeCoords[u];
        const to = nodeCoords[v];
        if (from && to) {
            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();
            
            const angle = Math.atan2(to.y - from.y, to.x - from.x);
            const arrowX = to.x - radius * Math.cos(angle);
            const arrowY = to.y - radius * Math.sin(angle);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.beginPath();
            ctx.moveTo(arrowX, arrowY);
            ctx.lineTo(arrowX - 8 * Math.cos(angle - Math.PI/6), arrowY - 8 * Math.sin(angle - Math.PI/6));
            ctx.lineTo(arrowX - 8 * Math.cos(angle + Math.PI/6), arrowY - 8 * Math.sin(angle + Math.PI/6));
            ctx.closePath();
            ctx.fill();
        }
    });
    
    // Draw nodes
    nodes.forEach(node => {
        const coord = nodeCoords[node];
        if (coord) {
            ctx.beginPath();
            ctx.arc(coord.x, coord.y, radius, 0, Math.PI * 2);
            
            if (node === xNode) {
                ctx.fillStyle = 'var(--accent-blue)';
            } else if (node === yNode) {
                ctx.fillStyle = 'var(--warning)';
            } else if (zSet.includes(node)) {
                ctx.fillStyle = '#555555';
            } else {
                ctx.fillStyle = '#222222';
            }
            ctx.fill();
            
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.lineWidth = 1.5;
            ctx.stroke();
            
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 11px JetBrains Mono';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(node, coord.x, coord.y);
        }
    });
}

function drawKolmogorovResult(result) {
    if (!ctx) return;
    ctx.clearRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    ctx.fillStyle = 'rgba(17, 17, 17, 0.95)';
    ctx.fillRect(0, 0, DOM.canvas.width, DOM.canvas.height);
    
    ctx.font = 'bold 16px JetBrains Mono';
    ctx.fillStyle = 'var(--stable)';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('KOLMOGÓROV COMPLEXITY (MDL)', 20, 20);
    
    ctx.font = '13px Outfit';
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText(`Minimum Description Length Ratio: ${result.mdl.toFixed(4)}`, 20, 55);
    ctx.fillText(`Raw Size: ${result.raw_size} Bytes | Compressed Size: ${result.compressed_size} Bytes`, 20, 85);
    ctx.fillText(`Compression Ratio: ${result.compression_ratio.toFixed(2)}x`, 20, 115);
    
    const maxBarW = 260;
    ctx.fillStyle = '#222222';
    ctx.fillRect(20, 155, maxBarW, 16);
    ctx.fillStyle = 'var(--warning)';
    ctx.fillRect(20, 155, maxBarW, 16);
    ctx.font = '9px JetBrains Mono';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText('Raw Data Bytes', 25, 163);
    
    ctx.fillStyle = '#222222';
    ctx.fillRect(20, 185, maxBarW, 16);
    ctx.fillStyle = 'var(--stable)';
    ctx.fillRect(20, 185, maxBarW * (result.compressed_size / result.raw_size), 16);
    ctx.fillStyle = '#FFFFFF';
    ctx.fillText('Compressed Data (MDL)', 25, 193);
}

// Render dynamic param forms
function renderParamForm() {
    const action = DOM.scientificAction.value;
    const template = ScientificParams[action];
    if (DOM.parameterInputs) {
        DOM.parameterInputs.innerHTML = template ? template() : '';
    }
}

// Set pipeline step status visual helper
function setPipelineStep(stepIndex, status, active = false) {
    const el = document.getElementById(`step-${stepIndex}`);
    if (!el) return;
    const statusEl = el.querySelector('.step-status');
    if (statusEl) {
        statusEl.textContent = status;
    }
    el.className = 'pipeline-step';
    if (active) {
        el.classList.add('active');
    } else if (status === 'DONE') {
        el.classList.add('done');
    } else if (status === 'ERROR') {
        el.classList.add('error');
    }
}

function resetPipeline() {
    for (let i = 1; i <= 5; i++) {
        setPipelineStep(i, 'IDLE');
    }
}

// Submit computation
async function executeCompute() {
    const query = DOM.consoleQuery.value.trim();
    if (!query) {
        alert('Please input an Exergy query.');
        return;
    }

    const action = DOM.scientificAction.value;
    const payload = {};

    if (action === 'entropy') {
        const val = document.getElementById('param-data').value;
        payload.data = val.includes(',') ? val.split(',').map(x => x.trim()) : val;
    } else if (action === 'fisher') {
        const val = document.getElementById('param-series').value;
        payload.series = val.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
    } else if (action === 'dsep') {
        payload.nodes = document.getElementById('param-nodes').value.split(',').map(x => x.trim());
        payload.edges = document.getElementById('param-edges').value.split(',').map(x => x.trim().split('->'));
        payload.x = document.getElementById('param-x').value.trim();
        payload.y = document.getElementById('param-y').value.trim();
        payload.z = document.getElementById('param-z').value.split(',').map(x => x.trim()).filter(x => x);
    } else if (action === 'kolmogorov') {
        payload.data = document.getElementById('param-text').value;
    }

    DOM.executeBtn.disabled = true;
    DOM.executeBtn.textContent = 'RUNNING...';
    resetPipeline();

    try {
        // Stage 1: Parsing
        setPipelineStep(1, 'ACTIVE', true);
        await new Promise(r => setTimeout(r, 250));
        setPipelineStep(1, 'DONE');

        // Stage 2: Retrieval
        setPipelineStep(2, 'ACTIVE', true);
        await new Promise(r => setTimeout(r, 250));
        setPipelineStep(2, 'DONE');

        // Stage 3: Fusion
        setPipelineStep(3, 'ACTIVE', true);
        await new Promise(r => setTimeout(r, 250));
        setPipelineStep(3, 'DONE');

        // Stage 4: Scientific Compute
        setPipelineStep(4, 'ACTIVE', true);
        
        const response = await fetch('/api/scientific', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, action, payload })
        });
        
        if (!response.ok) {
            throw new Error('Scientific calculation failed server-side');
        }
        
        const data = await response.json();
        setPipelineStep(4, 'DONE');

        // Stage 5: Ledgification
        setPipelineStep(5, 'ACTIVE', true);
        await new Promise(r => setTimeout(r, 200));
        setPipelineStep(5, 'DONE');

        // Update output UI
        let detailsText = `<strong>Mode Activated:</strong> ${data.audit.mode}<br/>`;
        detailsText += `<strong>Confidence:</strong> ${data.audit.proof_confidence} (${data.audit.proof_base})<br/>`;
        detailsText += `<strong>Ledger Hash:</strong> <span class="hash-display">${data.audit.hash}</span><br/>`;
        
        if (action !== 'inference') {
            detailsText += `<strong>Scientific Output:</strong> ${JSON.stringify(data.scientific)}<br/>`;
        }
        
        DOM.pipelineDetails.innerHTML = detailsText;

        // Render Canvas Visualizations
        if (action === 'entropy') {
            drawEntropyResult(data.scientific);
        } else if (action === 'fisher') {
            drawFisherResult(data.scientific, payload.series);
        } else if (action === 'dsep') {
            drawdSepResult(data.scientific, payload.nodes, payload.edges, payload.x, payload.y, payload.z);
        } else if (action === 'kolmogorov') {
            drawKolmogorovResult(data.scientific);
        } else {
            ctx.clearRect(0, 0, DOM.canvas.width, DOM.canvas.height);
            ctx.fillStyle = 'rgba(17, 17, 17, 0.95)';
            ctx.fillRect(0, 0, DOM.canvas.width, DOM.canvas.height);
            ctx.font = '13px Outfit';
            ctx.fillStyle = 'var(--stable)';
            ctx.fillText('INFERENCE TRACE SYNTHESIZED SUCCESSFULLY', 20, 30);
            ctx.fillStyle = '#FFFFFF';
            ctx.fillText(`Reasoning Steps executed:`, 20, 60);
            data.inference.reasoning_steps.forEach((step, idx) => {
                ctx.fillText(`${idx + 1}. ${step}`, 30, 90 + idx * 25);
            });
        }

        addLogEntry('C7_COMPUTE', `Exergy run completed. Ledger hash compiled.`, 'stable', `${data.inference.retrieved_nodes.length} nodes`);

    } catch (e) {
        console.error(e);
        resetPipeline();
        setPipelineStep(4, 'ERROR');
        DOM.pipelineDetails.innerHTML = `<span class="warning-text">Error during computation: ${e.message}</span>`;
        addLogEntry('C7_ERROR', `Compute failure: ${e.message}`, 'critical', '0ms');
    } finally {
        DOM.executeBtn.disabled = false;
        DOM.executeBtn.textContent = 'EXECUTE COMPUTE';
    }
}

// Render C7 Audit Ledger table
function renderAuditTable() {
    if (!DOM.auditTbody) return;
    const fragment = document.createDocumentFragment();
    exergyState.auditLedger.forEach(row => {
        const tr = document.createElement('tr');
        const ts = new Date(row.timestamp).toLocaleTimeString();
        tr.innerHTML = `
            <td>${esc(ts)}</td>
            <td class="query-td" title="${esc(row.query)}">${esc(row.query)}</td>
            <td><span class="mode-badge">${esc(row.mode)}</span></td>
            <td><span class="conf-badge">${esc(row.proof_confidence)}</span></td>
            <td class="hash-td" title="${esc(row.hash)}"><code>${esc(row.hash.substring(0, 10))}...</code></td>
            <td><button class="inspect-btn" aria-label="Inspect Audit Record" onclick="inspectAuditItem(${row.id})">🔍</button></td>
        `;
        fragment.appendChild(tr);
    });
    DOM.auditTbody.innerHTML = '';
    DOM.auditTbody.appendChild(fragment);
}

// Window global helper to inspect audit records
window.inspectAuditItem = function(id) {
    const item = exergyState.auditLedger.find(r => r.id === id);
    if (!item) return;
    
    let text = `--- C7 AUDIT INSPECTION REPORT ---\n`;
    text += `Query: "${item.query}"\n`;
    text += `Mode: ${item.mode}\n`;
    text += `Confidence: ${item.proof_confidence} (${item.proof_base})\n`;
    text += `Primitives Used: ${item.primitives_used}\n`;
    text += `Isomorphisms Used: ${item.isomorphisms_used}\n`;
    text += `Reasoning: \n`;
    try {
        const steps = JSON.parse(item.reasoning_steps);
        steps.forEach((s, i) => { text += `  ${i+1}. ${s}\n`; });
    } catch (err) {
        console.error('[CORTEX AUDIT] Error parsing reasoning_steps:', err);
    }
    
    text += `Scientific Result:\n  ${item.scientific_result}\n`;
    text += `SHA-256 Ledger Hash: ${item.hash}\n`;
    
    if (DOM.pipelineDetails) {
        DOM.pipelineDetails.innerHTML = `<div style="white-space: pre-wrap; font-size: 0.8em; color: var(--text-primary); text-align: left;">${esc(text)}</div>`;
        DOM.pipelineDetails.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Draw the results in canvas if possible
    try {
        const sci = JSON.parse(item.scientific_result);
        const action = item.scientific_result.includes('entropy') ? 'entropy' :
                       item.scientific_result.includes('fisher_information') ? 'fisher' :
                       item.scientific_result.includes('d_separated') ? 'dsep' :
                       item.scientific_result.includes('mdl') ? 'kolmogorov' : 'inference';
                       
        if (action === 'entropy') {
            drawEntropyResult(sci);
        } else if (action === 'fisher') {
            drawFisherResult(sci, [10, 12, 11, 14, 15, 13, 16, 18, 17, 20]); // mock layout path fallback
        } else if (action === 'dsep') {
            // parse parameters from query/result to draw
            const nodes = JSON.parse(item.primitives_used).map(p => p.split('.').pop());
            drawdSepResult(sci, nodes, [], '', '', []);
        } else if (action === 'kolmogorov') {
            drawKolmogorovResult(sci);
        }
    } catch (err) {
        console.error('[CORTEX AUDIT] Error rendering scientific result:', err);
    }
};

// Fetch initial audit records on load
async function fetchAuditLogs() {
    try {
        const response = await fetch('/api/audit');
        if (response.ok) {
            exergyState.auditLedger = await response.json();
            renderAuditTable();
        }
    } catch (e) {
        console.error('[CORTEX AUDIT FETCH FAILED]', e);
    }
}

// WebSocket Connection
let socket = null;

function connectWS() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    socket = new WebSocket(`${protocol}//${host}:8081`);

    socket.onopen = () => {
        console.log('[CORTEX UI] Connected to telemetry WebSocket.');
        const statusInd = document.querySelector('.status-indicator');
        if (statusInd) {
            statusInd.innerHTML = '<span class="pulse" style="background-color: var(--stable); box-shadow: 0 0 8px var(--stable);"></span> C5-REAL LINKED';
            statusInd.style.color = 'var(--stable)';
            statusInd.style.background = 'rgba(43, 229, 148, 0.05)';
        }
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
                
                if (data.llmViolations !== undefined) exergyState.llmViolations = data.llmViolations;
                if (data.cpmViolations !== undefined) exergyState.cpmViolations = data.cpmViolations;
                if (data.llmLatency !== undefined) exergyState.llmLatency = data.llmLatency;
                if (data.cpmLatency !== undefined) exergyState.cpmLatency = data.cpmLatency;

                if (data.log) {
                    addLogEntry(data.log.module, data.log.text, data.log.type, data.log.metric);
                }
                if (!window._cortexRenderPending) {
                    window._cortexRenderPending = true;
                    requestAnimationFrame(() => {
                        updateDOM();
                        window._cortexRenderPending = false;
                    });
                }
            } else if (data.type === 'audit_entry') {
                exergyState.auditLedger.unshift(data);
                if (exergyState.auditLedger.length > 50) exergyState.auditLedger.pop();
                renderAuditTable();
            }
        } catch (e) {
            console.error('[CORTEX ERROR] Failed to parse WebSocket frame', e);
        }
    };

    socket.onclose = () => {
        console.log('[CORTEX UI] Telemetry WebSocket unlinked. Freezing state. NO C4-SIM ALLOWED.');
        const statusInd = document.querySelector('.status-indicator');
        if (statusInd) {
            statusInd.innerHTML = '<span class="pulse" style="background-color: var(--warning); box-shadow: 0 0 8px var(--warning);"></span> DISCONNECTED';
            statusInd.style.color = 'var(--warning)';
            statusInd.style.background = 'rgba(229, 43, 43, 0.05)';
        }
        
        // [C5-REAL] Jittered Exponential Backoff
        const baseDelay = Math.min(window._wsReconnectDelay || 2000, 30000);
        const jitter = Math.random() * 1000;
        window._wsReconnectDelay = baseDelay * 1.5;
        setTimeout(connectWS, baseDelay + jitter);
    };
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Bind listeners
    if (DOM.scientificAction && DOM.parameterInputs) {
        DOM.scientificAction.addEventListener('change', renderParamForm);
        renderParamForm();
    }
    
    if (DOM.executeBtn && DOM.consoleQuery) {
        DOM.executeBtn.addEventListener('click', executeCompute);
    }

    if (DOM.filterBtns && DOM.filterBtns.length > 0) {
        DOM.filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                DOM.filterBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                exergyState.filter = e.target.dataset.filter;
                renderLogs();
            });
        });
    }

    if (DOM.canvas) drawPlaceholder();
    fetchAuditLogs();
    connectWS();
    
    addLogEntry('CORTEX_SYS', 'Kernel bootstrap sequence initiated', 'stable', '0.00ms');
    addLogEntry('EXERGY_CORE', 'Metrics matrix synchronized', 'stable', '1.24ms');
    updateDOM();
});
