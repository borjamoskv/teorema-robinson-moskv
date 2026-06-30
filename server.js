const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');

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
    console.log(`[CORTEX] Node.js Sovereign Kernel Server running on http://localhost:${PORT}`);
    console.log(`[CORTEX] Anergy level minimal. Reality: C5-REAL`);
});

// Start WebSocket Server on WS_PORT
const wss = new WebSocket.Server({ port: WS_PORT });
const os = require('os');

console.log(`[CORTEX] WebSocket Telemetry Server running on ws://localhost:${WS_PORT}`);

wss.on('connection', (ws) => {
    console.log('[CORTEX WS] New UI agent linked. Commencing physical telemetry feed.');

    ws.on('message', (message) => {
        const payloadStr = message.toString();
        try {
            const data = JSON.parse(payloadStr);
            if (data.type === 'telemetry') {
                console.log(`[CORTEX TELEMETRY] ${data.log?.module || 'VM'} -> ${data.log?.text || ''}`);
            }
        } catch (_) {}

        wss.clients.forEach((client) => {
            if (client !== ws && client.readyState === WebSocket.OPEN) {
                client.send(payloadStr);
            }
        });
    });

    ws.on('close', () => {
        console.log('[CORTEX WS] UI agent unlinked.');
    });
});

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
    
    const payload = JSON.stringify({
        type: 'telemetry',
        exergy: exergy,
        anergy: anergy,
        yield: exergy / (anergy + 1),
        mccabe: Math.floor(cpuLoad * 10),
        nesting: cpus.length,
        deadcode: Math.floor(memUsage.heapUsed / 1024 / 1024),
        entropy: cpuLoad / cpus.length,
        log: {
            module: 'OS_KERNEL_C5',
            text: `Physical telemetry vector mapped. Load Avg: ${cpuLoad.toFixed(2)}`,
            type: (cpuLoad > cpus.length / 2) ? 'critical' : 'stable',
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
    console.log('[CORTEX] Shutting down telemetry server...');
    wss.close(() => {
        server.close(() => {
            console.log('[CORTEX] Server terminated cleanly.');
            process.exit(0);
        });
    });
    setTimeout(() => {
        console.log('[CORTEX] Force exit triggered.');
        process.exit(1);
    }, 2000);
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
