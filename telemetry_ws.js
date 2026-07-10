const WebSocket = require('ws');
const os = require('os');

function initTelemetryWS(WS_PORT, db) {
    const wss = new WebSocket.Server({ port: WS_PORT });
    
    console.log(`\x1b[1;34m[CORTEX]\x1b[0m WebSocket Telemetry Server running on ws://localhost:${WS_PORT}`);

    wss.on('connection', (ws) => {
        console.log('\x1b[1;36m[CORTEX WS]\x1b[0m New UI agent linked. Commencing physical telemetry feed.');
        
        // [C5-REAL] Heartbeat State
        ws.isAlive = true;
        ws.on('pong', () => { ws.isAlive = true; });

        ws.on('message', (message) => {
            const payloadStr = message.toString();
            try {
                const data = JSON.parse(payloadStr);
                if (data.type === 'telemetry') {
                    console.log(`\x1b[1;35m[CORTEX TELEMETRY]\x1b[0m ${data.log?.module || 'VM'} -> ${data.log?.text || ''}`);
                }
            } catch (wsParseErr) {
                console.error('\x1b[1;31m[CORTEX WS PARSE ERROR]\x1b[0m', wsParseErr.message);
                // [L12] K1 FAIL-FAST: Purge anergy (malformed JSON) immediately.
                ws.close(1003, 'Anergy Detected: Malformed JSON');
                return;
            }

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

    // [C5-REAL] Ping/Pong Loop (Zombie Connection Pruning)
    const pingInterval = setInterval(() => {
        wss.clients.forEach((ws) => {
            if (ws.isAlive === false) return ws.terminate();
            ws.isAlive = false;
            ws.ping();
        });
    }, 30000);

    const insertTelemetry = db.prepare(`
        INSERT INTO telemetry_logs (exergy, anergy, yield, mccabe, nesting, deadcode, entropy, log_module, log_text, log_type)
        VALUES (@exergy, @anergy, @yield, @mccabe, @nesting, @deadcode, @entropy, @log_module, @log_text, @log_type)
    `);

    const deleteOldLogs = db.prepare(`
        DELETE FROM telemetry_logs WHERE id NOT IN (
            SELECT id FROM telemetry_logs ORDER BY timestamp DESC LIMIT 1000
        )
    `);

    const intervalId = setInterval(() => {
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

        try {
            db.transaction(() => {
                insertTelemetry.run(metricData);
                deleteOldLogs.run();
            })();
        } catch (e) {
            console.error('\x1b[1;31m[CORTEX DB ERROR]\x1b[0m', e.message);
        }

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

        broadcast(payload);
    }, 1500);

    function broadcast(payload) {
        const payloadStr = typeof payload === 'string' ? payload : JSON.stringify(payload);
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                try {
                    client.send(payloadStr);
                } catch (e) {
                    console.error('\x1b[1;31m[CORTEX WS BROADCAST ERROR]\x1b[0m', e.message);
                }
            }
        });
    }

    return {
        wss,
        broadcast,
        shutdown: () => {
            clearInterval(intervalId);
            clearInterval(pingInterval);
            wss.close();
        }
    };
}

module.exports = initTelemetryWS;
