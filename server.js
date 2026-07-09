const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const os = require('os');
const Database = require('better-sqlite3');
const { execFile, spawn } = require('child_process');
const crypto = require('crypto');

const PORT = process.env.PORT || 8080;
const WS_PORT = 8081;
const PUBLIC_DIR = path.join(__dirname, 'public');

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.svg': 'image/svg+xml'
};

function runPython(script, args, inputData) {
    return new Promise((resolve, reject) => {
        const venvPython = path.join(__dirname, '.venv', 'bin', 'python');
        const pythonExecutable = fs.existsSync(venvPython) ? venvPython : 'python3';
        const child = spawn(pythonExecutable, [path.join(__dirname, script), ...args], { cwd: __dirname });
        let stdout = '';
        let stderr = '';
        
        if (inputData) {
            child.stdin.write(JSON.stringify(inputData));
            child.stdin.end();
        }
        
        child.stdout.on('data', data => {
            stdout += data.toString();
        });
        
        child.stderr.on('data', data => {
            stderr += data.toString();
        });
        
        child.on('close', code => {
            if (code !== 0) {
                reject(new Error(`Python script ${script} exited with code ${code}. Stderr: ${stderr}`));
            } else {
                try {
                    resolve(JSON.parse(stdout));
                } catch (e) {
                    resolve({ raw: stdout });
                }
            }
        });
    });
}

const server = http.createServer((req, res) => {
    if (req.url === '/api/telemetry' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                const payload = JSON.parse(body);
                // Retransmitir a los WebSockets
                wss.clients.forEach((client) => {
                    if (client.readyState === WebSocket.OPEN) {
                        try {
                            client.send(JSON.stringify(payload));
                        } catch (e) {
                            console.error('\x1b[1;31m[CORTEX WS BROADCAST ERROR]\x1b[0m', e.message);
                        }
                    }
                });
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ status: 'ok', clients: wss.clients.size }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid JSON payload' }));
            }
        });
        return;
    }

    if (req.url === '/api/scientific' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', async () => {
            try {
                const payload = JSON.parse(body);
                const query = payload.query || "Por qué falló el proceso en el tiempo";
                const action = payload.action || "inference";
                const toolPayload = payload.payload || {};

                // 1. Run inference logic using cortex_inference.py
                const inferenceTrace = await runPython('cortex_inference.py', ['--json', query], null);

                // 2. Run scientific logic if action != 'inference'
                let scientificResult = {};
                if (action !== 'inference') {
                    scientificResult = await runPython('scientific_engine.py', [action], toolPayload);
                }

                // 3. Construct the trace audit entry
                const combinedResult = {
                    query: query,
                    mode: inferenceTrace.mode_activated || 'MODE-01-CAUSAL-DEDUCTION',
                    proof_base: inferenceTrace.proof?.Base || 'CORTEX-db',
                    proof_confidence: inferenceTrace.proof?.Confidence || 'C5-REAL',
                    primitives_used: JSON.stringify(inferenceTrace.retrieved_nodes || []),
                    isomorphisms_used: JSON.stringify(inferenceTrace.applied_isomorphisms || []),
                    reasoning_steps: JSON.stringify(inferenceTrace.reasoning_steps || []),
                    scientific_result: JSON.stringify(scientificResult)
                };

                // 4. Compute integrity hash for auditability (C7 compliance)
                const traceString = combinedResult.query + combinedResult.mode + combinedResult.reasoning_steps + combinedResult.scientific_result;
                const hash = crypto.createHash('sha256').update(traceString).digest('hex');
                combinedResult.hash = hash;

                // 5. Store in SQLite audit ledger
                insertAuditLog.run(combinedResult);

                // 6. Broadcast to all WebSockets
                wss.clients.forEach((client) => {
                    if (client.readyState === WebSocket.OPEN) {
                        try {
                            client.send(JSON.stringify({
                                type: 'audit_entry',
                                timestamp: new Date().toISOString(),
                                ...combinedResult
                            }));
                        } catch (e) {
                            console.error('\x1b[1;31m[CORTEX WS BROADCAST ERROR]\x1b[0m', e.message);
                        }
                    }
                });

                // 7. Respond with combined results
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    inference: inferenceTrace,
                    scientific: scientificResult,
                    audit: combinedResult
                }));
            } catch (e) {
                console.error('[CORTEX SCIENTIFIC ERROR]', e);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message || 'Scientific compute failed' }));
            }
        });
        return;
    }

    if (req.url === '/api/audit' && req.method === 'GET') {
        try {
            const logs = getAuditLogs.all();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(logs));
        } catch (e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to retrieve audit ledger' }));
        }
        return;
    }

    // [C5-REAL] Mitigación de Path Traversal (Anergía de Seguridad)
    const normalizedUrl = path.normalize(req.url);
    let filePath = path.join(PUBLIC_DIR, normalizedUrl === '/' || normalizedUrl === '\\' ? 'index.html' : normalizedUrl);

    // Evitar bypass de prefijo de directorio hermano (ej. public-secret)
    const safePrefix = PUBLIC_DIR.endsWith(path.sep) ? PUBLIC_DIR : PUBLIC_DIR + path.sep;
    if (!filePath.startsWith(safePrefix) && filePath !== PUBLIC_DIR) {
        res.writeHead(403, { 'Content-Type': 'text/html' });
        return res.end('<h1>403 Forbidden - Vector Adversarial Bloqueado</h1>', 'utf-8');
    }

    let extname = path.extname(filePath);
    let contentType = MIME_TYPES[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code == 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/html' });
                res.end('<h1>404 Not Found - Entropy Error</h1>', 'utf-8');
            } else {
                res.writeHead(500);
                res.end(`Server Error: ${error.code}`);
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
});

// Start HTTP Server
server.listen(PORT, () => {
    console.log(`\x1b[1;34m[CORTEX]\x1b[0m Node.js Sovereign Kernel Server running on http://localhost:${PORT}`);
    console.log(`\x1b[1;32m[CORTEX]\x1b[0m Anergy level minimal. Reality: C5-REAL`);
});

// Start WebSocket Server on WS_PORT
const wss = new WebSocket.Server({ port: WS_PORT });

console.log(`\x1b[1;34m[CORTEX]\x1b[0m WebSocket Telemetry Server running on ws://localhost:${WS_PORT}`);

wss.on('connection', (ws) => {
    console.log('\x1b[1;36m[CORTEX WS]\x1b[0m New UI agent linked. Commencing physical telemetry feed.');

    ws.on('message', (message) => {
        const payloadStr = message.toString();
        try {
            const data = JSON.parse(payloadStr);
            if (data.type === 'telemetry') {
                console.log(`\x1b[1;35m[CORTEX TELEMETRY]\x1b[0m ${data.log?.module || 'VM'} -> ${data.log?.text || ''}`);
            }
        } catch (wsParseErr) { console.error('\x1b[1;31m[CORTEX WS PARSE ERROR]\x1b[0m', wsParseErr.message); }

        wss.clients.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                try {
                    client.send(payloadStr);
                } catch (e) {
                    console.error('\x1b[1;31m[CORTEX WS ERROR]\x1b[0m', e.message);
                }
            }
        });
    });

    ws.on('close', () => {
        console.log('\x1b[1;33m[CORTEX WS]\x1b[0m UI agent unlinked.');
    });
});

// [C5-REAL] Database persistence with WAL mode and busy_timeout
const dbPath = path.join(__dirname, 'telemetry.db');
const db = new Database(dbPath, { timeout: 5000 });
db.pragma('journal_mode = WAL');

db.exec(`
    CREATE TABLE IF NOT EXISTS telemetry_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        exergy REAL,
        anergy REAL,
        yield REAL,
        mccabe INTEGER,
        nesting INTEGER,
        deadcode INTEGER,
        entropy REAL,
        log_module TEXT,
        log_text TEXT,
        log_type TEXT
    );

    CREATE TABLE IF NOT EXISTS audit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        query TEXT,
        mode TEXT,
        proof_base TEXT,
        proof_confidence TEXT,
        primitives_used TEXT,
        isomorphisms_used TEXT,
        reasoning_steps TEXT,
        scientific_result TEXT,
        hash TEXT
    );

    CREATE UNIQUE INDEX IF NOT EXISTS idx_audit_hash ON audit_ledger(hash);

    CREATE TRIGGER IF NOT EXISTS trg_audit_no_update
    BEFORE UPDATE ON audit_ledger
    BEGIN SELECT RAISE(ABORT, 'LEDGER_IMMUTABLE'); END;

    CREATE TRIGGER IF NOT EXISTS trg_audit_no_delete
    BEFORE DELETE ON audit_ledger
    BEGIN SELECT RAISE(ABORT, 'LEDGER_IMMUTABLE'); END;
`);

const insertAuditLog = db.prepare(`
    INSERT INTO audit_ledger (query, mode, proof_base, proof_confidence, primitives_used, isomorphisms_used, reasoning_steps, scientific_result, hash)
    VALUES (@query, @mode, @proof_base, @proof_confidence, @primitives_used, @isomorphisms_used, @reasoning_steps, @scientific_result, @hash)
`);

const getAuditLogs = db.prepare(`
    SELECT * FROM audit_ledger ORDER BY timestamp DESC LIMIT 50
`);

const insertTelemetry = db.prepare(`
    INSERT INTO telemetry_logs (exergy, anergy, yield, mccabe, nesting, deadcode, entropy, log_module, log_text, log_type)
    VALUES (@exergy, @anergy, @yield, @mccabe, @nesting, @deadcode, @entropy, @log_module, @log_text, @log_type)
`);

const deleteOldLogs = db.prepare(`
    DELETE FROM telemetry_logs WHERE id NOT IN (
        SELECT id FROM telemetry_logs ORDER BY timestamp DESC LIMIT 1000
    )
`);

// Broadcast real physical metrics (C5-REAL) every 1.5 seconds
setInterval(() => {
    const memUsage = process.memoryUsage();
    const freeMem = os.freemem();
    const totalMem = os.totalmem();
    const cpus = os.cpus();
    const cpuLoad = os.loadavg()[0];

    const memPercent = (freeMem / totalMem) * 100;
    const anergy = (100 - memPercent);
    const exergy = memPercent;

    const metricData = {
        exergy: exergy,
        anergy: anergy,
        yield: exergy / (anergy + 1),
        mccabe: Math.floor(cpuLoad * 10),
        nesting: cpus.length,
        deadcode: Math.floor(memUsage.heapUsed / 1024 / 1024),
        entropy: cpuLoad / cpus.length,
        log_module: 'OS_KERNEL_C5',
        log_text: `Physical telemetry vector mapped. Load Avg: ${cpuLoad.toFixed(2)}`,
        log_type: (cpuLoad > cpus.length / 2) ? 'critical' : 'stable'
    };

    // Falsación Empírica: Persistencia Atómica
    insertTelemetry.run(metricData);
    deleteOldLogs.run();

    const payload = JSON.stringify({
        type: 'telemetry',
        ...metricData,
        log: {
            module: metricData.log_module,
            text: metricData.log_text,
            type: metricData.log_type,
            metric: `${Math.floor(memUsage.rss / 1024 / 1024)}MB RSS`
        }
    });

    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            try {
                client.send(payload);
            } catch (e) {
                console.error('\x1b[1;31m[CORTEX WS TELEMETRY ERROR]\x1b[0m', e.message);
            }
        }
    });
}, 1500);

// Clean shutdown handlers
const shutdown = () => {
    console.log('\x1b[1;33m[CORTEX]\x1b[0m Shutting down telemetry server...');
    db.close();
    wss.close(() => {
        server.close(() => {
            console.log('\x1b[1;32m[CORTEX]\x1b[0m Server terminated cleanly.');
            process.exit(0);
        });
    });
    setTimeout(() => {
        console.log('\x1b[1;31m[CORTEX]\x1b[0m Force exit triggered.');
        process.exit(1);
    }, 2000);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
