#!/Users/borjafernandezangulo/.venv/bin/python3
# C5-REAL SOVEREIGN: Nexus Conversation Bridge (V3 - SQLite FTS5)
# Ingesta y búsqueda O(1) usando SQLite WAL + FTS5.

import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

# Path to all conversation transcripts in the CORTEX environment
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
DB_PATH = BRAIN_DIR.parent / "nexus_transcripts.db"

def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    
    # Tabla FTS5 para búsquedas ultrarrápidas
    conn.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS transcripts_fts USING fts5(
            conversation_id UNINDEXED,
            source UNINDEXED,
            content,
            timestamp UNINDEXED
        )
    ''')
    
    # Tabla de metadatos para Delta Sync
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sync_metadata (
            conversation_id TEXT PRIMARY KEY,
            last_modified REAL
        )
    ''')
    return conn

def sync_transcripts(conn: sqlite3.Connection, force: bool = False):
    print("\x1b[1;36m[SYNC]\x1b[0m Ingestando matriz conversacional en SQLite FTS5...")
    files = list(BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"))
    
    cursor = conn.cursor()
    synced = 0
    skipped = 0
    
    for transcript_file in files:
        conv_id = transcript_file.parts[-4]
        try:
            mtime = transcript_file.stat().st_mtime
            
            if not force:
                cursor.execute("SELECT last_modified FROM sync_metadata WHERE conversation_id = ?", (conv_id,))
                row = cursor.fetchone()
                if row and row[0] >= mtime:
                    skipped += 1
                    continue
            
            # Borrar datos viejos de esta conversación si existían
            cursor.execute("DELETE FROM transcripts_fts WHERE conversation_id = ?", (conv_id,))
            
            with open(transcript_file, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    content = data.get("content", "")
                    if content:
                        source = data.get("source", "UNKNOWN")
                        # Omitir planner response largo sin sentido para limpiar la base
                        if len(content) > 100000:
                            continue
                        cursor.execute(
                            "INSERT INTO transcripts_fts (conversation_id, source, content, timestamp) VALUES (?, ?, ?, ?)",
                            (conv_id, source, str(content), mtime)
                        )
            
            cursor.execute(
                "INSERT OR REPLACE INTO sync_metadata (conversation_id, last_modified) VALUES (?, ?)",
                (conv_id, mtime)
            )
            synced += 1
            
        except Exception:
            pass
            
    print(f"\x1b[1;32m[SYNC COMPLETE]\x1b[0m {synced} conversaciones ingeridas, {skipped} omitidas (sin cambios).")

def search_fts(conn: sqlite3.Connection, query: str, limit: int):
    print(f"\x1b[1;34m[NEXUS FTS5]\x1b[0m Rastreando entropía: '{query}' (Límite: {limit})")
    
    cursor = conn.cursor()
    # Usar sintaxis FTS5 o fallback simple
    try:
        cursor.execute('''
            SELECT conversation_id, source, snippet(transcripts_fts, 2, '\x1b[1;31m', '\x1b[0m', '...', 64)
            FROM transcripts_fts 
            WHERE transcripts_fts MATCH ? 
            ORDER BY rank 
            LIMIT ?
        ''', (query, limit))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        # Fallback si la query no es un FTS válido (ej. tiene caracteres especiales)
        safe_query = query.replace('"', '""')
        cursor.execute('''
            SELECT conversation_id, source, snippet(transcripts_fts, 2, '\x1b[1;31m', '\x1b[0m', '...', 64)
            FROM transcripts_fts 
            WHERE transcripts_fts MATCH '"{safe_query}"'
            ORDER BY rank 
            LIMIT ?
        ''')
        rows = cursor.fetchall()
        
    if not rows:
        print(f"\n\x1b[1;31m[ANERGÍA]\x1b[0m La entropía '{query}' no existe en ningún bloque de la red.")
        return
        
    for i, (conv_id, source, snip) in enumerate(rows):
        print(f"\n\x1b[1;32m[MATCH {i+1}]\x1b[0m Conv: {conv_id}")
        print(f"  Fuente:  {source}")
        print(f"  Payload: {snip.replace(chr(10), ' ')}")
        
    print(f"\n\x1b[1;36m[AUDIT COMPLETE]\x1b[0m Total inyecciones extraídas: {len(rows)}")

def main():
    parser = argparse.ArgumentParser(description="Nexus Conversation Bridge (C5-REAL V3)")
    parser.add_argument("--query", help="Keyword para buscar en FTS5.")
    parser.add_argument("--limit", type=int, default=100, help="Límite termodinámico.")
    parser.add_argument("--sync", action="store_true", help="Forzar sincronización delta de logs a SQLite.")
    parser.add_argument("--force-sync", action="store_true", help="Forzar purga y resincronización total.")
    args = parser.parse_args()
    
    conn = init_db()
    
    # Auto-sync si la base está vacía
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sync_metadata")
    count = cursor.fetchone()[0]
    
    if count == 0 or args.sync or args.force_sync:
        sync_transcripts(conn, force=args.force_sync)
        
    if args.query:
        search_fts(conn, args.query, args.limit)

if __name__ == "__main__":
    main()
