const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const cors = require('cors');
const os = require('os');

const app = express();
app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

// Path to CORTEX DB
const DB_PATH = path.join(os.homedir(), '.babylon60', 'cortex.db');

// Connect to SQLite DB in WAL mode
const db = new sqlite3.Database(DB_PATH, sqlite3.OPEN_READONLY, (err) => {
    if (err) {
        console.error('[C5-REAL] Error connecting to DB:', err.message);
    } else {
        console.log('[C5-REAL] Connected to SQLite DB (Read-Only).');
    }
});

// API endpoint to get all entities
app.get('/api/entities', (req, res) => {
    const query = `
        SELECT 'PRIMITIVAS' as category, id, primitiva as title, mecanismo_causal as description FROM primitivas_de_colapso
        UNION ALL
        SELECT 'INVARIANTES' as category, id, invariante as title, implicacion_operacional as description FROM invariantes_termodinamicas
        UNION ALL
        SELECT 'ANTIPATRONES' as category, id, antipatron as title, disfuncion_causal as description FROM antipatrones_estocasticos
        UNION ALL
        SELECT 'REDUNDANCIAS' as category, id, redundancia_c5 as title, funcion_topologica as description FROM redundancias_activas
        UNION ALL
        SELECT 'VECTORES' as category, id, vector_adversarial as title, mecanismo_de_explotacion as description FROM vectores_adversariales
    `;
    
    db.all(query, [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ data: rows });
    });
});

const PORT = 3060;
app.listen(PORT, () => {
    console.log(`[CORTEX NEXUS] Dashboard Server running on http://localhost:${PORT}`);
});
