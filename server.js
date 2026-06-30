const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const os = require('os');
const Database = require('better-sqlite3');

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
                        client.send(JSON.stringify(payload));
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

    // [C5-REAL] Mitigación de Path Traversal (Anergía de Seguridad)
    const normalizedUrl = path.normalize(req.url);
    let filePath = path.join(PUBLIC_DIR, normalizedUrl === '/' || normalizedUrl === '\\' ? 'index.html' : normalizedUrl);

    if (!filePath.startsWith(PUBLIC_DIR)) {
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
        } catch (_) {}

        wss.clients.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                client.send(payloadStr);
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
    )
`);

const insertTelemetry = db.prepare(`
    INSERT INTO telemetry_logs (exergy, anergy, yield, mccabe, nesting, deadcode, entropy, log_module, log_text, log_type)
    VALUES (@exergy, @anergy, @yield, @mccabe, @nesting, @deadcode, @entropy, @log_module, @log_text, @log_type)
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
            client.send(payload);
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
