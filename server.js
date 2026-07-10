const http = require('http');
const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');
const { spawn } = require('child_process');
const crypto = require('crypto');
const initTelemetryWS = require('./telemetry_ws');

const PORT = process.env.PORT || 8080;
const WS_PORT = 8081;
const PUBLIC_DIR = path.join(__dirname, 'public');

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

    CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_logs(timestamp);

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

// Initialize WebSockets decoupled
const telemetryServer = initTelemetryWS(WS_PORT, db);

const MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.svg': 'image/svg+xml'
};

// Perform sync validation exactly once at boot time (Fail-Fast)
const venvPython = path.join(__dirname, '.venv', 'bin', 'python3');
if (!fs.existsSync(venvPython)) {
    console.error('\x1b[1;31m[CORTEX APOPTOSIS]\x1b[0m .venv/bin/python3 missing. Crashing to prevent global env contamination.');
    process.exit(1);
}

function runPython(script, args, inputData) {
    return new Promise((resolve, reject) => {
        
        const child = spawn(venvPython, [path.join(__dirname, script), ...args], { cwd: __dirname });
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
        
        
        // [C5-REAL] Thermodynamic Timeout Apoptosis
        const timeoutId = setTimeout(() => {
            child.kill('SIGKILL');
            reject(new Error(`Python script ${script} exceeded execution timeout bounds.`));
        }, 15000);
        
        child.on('close', code => {
            clearTimeout(timeoutId);
            if (code !== 0) {
                reject(new Error(`Python script ${script} exited with code ${code}. Stderr: ${stderr}`));
            } else {
                try {
                    resolve(JSON.parse(stdout));
                } catch (e) {
                    reject(new Error(`[L12] K1 FAIL-FAST: Invalid JSON output from ${script}. Raw: ${stdout}`));
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
            if (body.length > 1048576) { // 1MB payload boundary
                req.connection.destroy();
            }
        });
        req.on('end', () => {
            try {
                const payload = JSON.parse(body);
                telemetryServer.broadcast(payload);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ status: 'ok', clients: telemetryServer.wss.clients.size }));
            } catch (e) {
                console.error('\x1b[1;31m[CORTEX HTTP ERROR]\x1b[0m', e.message);
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
            if (body.length > 5242880) { // 5MB payload boundary for scientific
                req.connection.destroy();
            }
        });
        req.on('end', async () => {
            try {
                const payload = JSON.parse(body);
                const query = payload.query || "Por qué falló el proceso en el tiempo";
                const action = payload.action || "inference";
                const toolPayload = payload.payload || {};

                // 1. Run inference logic
                const inferenceTrace = await runPython('cortex_inference.py', ['--json', query], null);

                // 2. Run scientific logic
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

                // 4. Compute integrity hash for auditability
                const traceString = combinedResult.query + combinedResult.mode + combinedResult.reasoning_steps + combinedResult.scientific_result;
                const hash = crypto.createHash('sha256').update(traceString).digest('hex');
                combinedResult.hash = hash;

                // 5. Store in SQLite audit ledger
                insertAuditLog.run(combinedResult);

                // 6. Broadcast to all WebSockets
                telemetryServer.broadcast({
                    type: 'audit_entry',
                    timestamp: new Date().toISOString(),
                    ...combinedResult
                });

                // 7. Respond
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
            console.error('\x1b[1;31m[CORTEX HTTP ERROR]\x1b[0m', e.message);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Failed to retrieve audit ledger' }));
        }
        return;
    }

    // [C5-REAL] Mitigación de Path Traversal
    const normalizedUrl = path.normalize(req.url);
    let filePath = path.join(PUBLIC_DIR, normalizedUrl === '/' || normalizedUrl === '\\' ? 'index.html' : normalizedUrl);

    try {
        const realPath = fs.realpathSync(filePath);
        if (!realPath.startsWith(fs.realpathSync(PUBLIC_DIR))) {
            throw new Error("Path traversal violation");
        }
        filePath = realPath;
    } catch (e) {
        res.writeHead(403, { 'Content-Type': 'text/html' });
        return res.end('<h1>403 Forbidden - Vector Adversarial Bloqueado</h1>', 'utf-8');
    }

    let extname = path.extname(filePath);
    let contentType = MIME_TYPES[extname] || 'application/octet-stream';

    // [C5-REAL] Optimal streaming replacing Buffered readFile
    const stat = fs.statSync(filePath, { throwIfNoEntry: false });
    if (!stat) {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        return res.end('<h1>404 Not Found - Entropy Error</h1>', 'utf-8');
    }

    res.writeHead(200, { 'Content-Type': contentType, 'Content-Length': stat.size });
    const stream = fs.createReadStream(filePath);
    stream.on('error', error => {
        console.error('\x1b[1;31m[CORTEX FS STREAM ERROR]\x1b[0m', error.message);
        res.writeHead(500);
        res.end(`Server Error: ${error.code}`);
    });
    stream.pipe(res);
});

// Start HTTP Server
server.listen(PORT, () => {
    console.log(`\x1b[1;34m[CORTEX]\x1b[0m Node.js Sovereign Kernel Server running on http://localhost:${PORT}`);
    console.log(`\x1b[1;32m[CORTEX]\x1b[0m Anergy level minimal. Reality: C5-REAL`);
});

// Clean shutdown handlers
const shutdown = () => {
    console.log('\x1b[1;33m[CORTEX]\x1b[0m Shutting down servers...');
    telemetryServer.shutdown();
    db.close();
    
    // Attempt graceful disconnect
    if (server.closeAllConnections) server.closeAllConnections();
    
    server.close(() => {
        console.log('\x1b[1;32m[CORTEX]\x1b[0m Server terminated cleanly.');
        process.exit(0);
    });
    setTimeout(() => {
        console.log('\x1b[1;31m[CORTEX]\x1b[0m Force exit triggered.');
        process.exit(1);
    }, 2000);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
