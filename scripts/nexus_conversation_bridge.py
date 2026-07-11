#!/Users/borjafernandezangulo/.venv/bin/python3
# C5-REAL SOVEREIGN: Nexus Conversation Bridge (V6 - UI Brutalist + Telemetría TTFT)
# Ingesta y búsqueda O(1) usando SQLite WAL + FTS5 con extracción causal forense.

import os
import sys
import json
import time
import socket
import sqlite3
import argparse
import threading
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.text import Text
    console = Console()
except ImportError:
    print("FATAL: 'rich' no instalado. Usa: pip install rich")
    sys.exit(1)

# Path to all conversation transcripts in the CORTEX environment
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
DB_PATH = BRAIN_DIR.parent / "nexus_transcripts.db"
TELEMETRY_DB = BRAIN_DIR.parent / "telemetry.db"

def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    
    # Check if we need to migrate schema (add step_index)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT step_index FROM transcripts_fts LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("DROP TABLE IF EXISTS transcripts_fts")
        conn.execute("DROP TABLE IF EXISTS sync_metadata")

    conn.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS transcripts_fts USING fts5(
            conversation_id UNINDEXED,
            step_index UNINDEXED,
            source UNINDEXED,
            content,
            timestamp UNINDEXED
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sync_metadata (
            conversation_id TEXT PRIMARY KEY,
            last_modified REAL
        )
    ''')
    
    # V10: MLX-LM Vector Embeddings Hook Schema
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transcripts_embeddings (
            conversation_id TEXT,
            step_index INTEGER,
            model_name TEXT,
            embedding BLOB,
            PRIMARY KEY(conversation_id, step_index, model_name)
        )
    ''')
    
    # Init Telemetry DB
    conn_tel = sqlite3.connect(TELEMETRY_DB, isolation_level=None)
    conn_tel.execute("PRAGMA journal_mode=WAL")
    conn_tel.execute('''
        CREATE TABLE IF NOT EXISTS ttft_metrics (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            query TEXT,
            latency_ms REAL,
            results_count INTEGER
        )
    ''')
    conn_tel.close()
    
    return conn

def record_telemetry(query: str, latency_ms: float, results_count: int):
    conn = sqlite3.connect(TELEMETRY_DB, isolation_level=None)
    conn.execute(
        "INSERT INTO ttft_metrics (query, latency_ms, results_count) VALUES (?, ?, ?)",
        (query, latency_ms, results_count)
    )
    conn.close()

def sync_transcripts(conn: sqlite3.Connection, force: bool = False, purge: bool = False):
    with console.status("[bold cyan]Ingestando matriz conversacional en SQLite FTS5...[/bold cyan]") as status:
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
                
                cursor.execute("DELETE FROM transcripts_fts WHERE conversation_id = ?", (conv_id,))
                
                with open(transcript_file, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        data = json.loads(line)
                        content = data.get("content", "")
                        if content:
                            source = data.get("source", "UNKNOWN")
                            step_idx = data.get("step_index", idx)
                            if len(content) > 100000:
                                continue
                            cursor.execute(
                                "INSERT INTO transcripts_fts (conversation_id, step_index, source, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                                (conv_id, step_idx, source, str(content), mtime)
                            )
                
                cursor.execute(
                    "INSERT OR REPLACE INTO sync_metadata (conversation_id, last_modified) VALUES (?, ?)",
                    (conv_id, mtime)
                )
                conn.commit()
                synced += 1
                
                if purge:
                    try:
                        transcript_file.unlink()
                        console.print(f"[bold red]💥 PURGED ENTROPY:[/bold red] {transcript_file}")
                    except OSError as e:
                        console.print(f"[bold red]Error purging {transcript_file}: {e}[/bold red]")
                
            except Exception:
                pass
                
        console.print(f"[bold green]✔ SYNC COMPLETE[/bold green] [cyan]{synced}[/cyan] conversiones mutadas, [dim]{skipped}[/dim] omitidas.")

def search_fts(conn: sqlite3.Connection, query: str, limit: int, context_window: int):
    console.print(Panel(f"Rastreando entropía: [bold red]'{query}'[/bold red] (Límite: {limit}) | Contexto ±{context_window}", title="[bold cyan]NEXUS FTS5 BRUTALIST[/bold cyan]", border_style="cyan"))
    
    start_time = time.perf_counter()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT conversation_id, step_index, source, snippet(transcripts_fts, 3, '[[HIGHLIGHT]]', '[[ENDHIGHLIGHT]]', '...', 64)
            FROM transcripts_fts 
            WHERE transcripts_fts MATCH ? 
            ORDER BY rank 
            LIMIT ?
        ''', (query, limit))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        safe_query = query.replace('"', '""')
        cursor.execute('''
            SELECT conversation_id, step_index, source, snippet(transcripts_fts, 3, '[[HIGHLIGHT]]', '[[ENDHIGHLIGHT]]', '...', 64)
            FROM transcripts_fts 
            WHERE transcripts_fts MATCH '"{safe_query}"'
            ORDER BY rank 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    record_telemetry(query, latency_ms, len(rows))
        
    if not rows:
        console.print(f"\n[bold red]💀 ANERGÍA:[/bold red] La entropía '{query}' no existe en ningún bloque de la red.")
        return
        
    for i, (conv_id, step_idx, source, snip) in enumerate(rows):
        clean_snip = snip.replace(chr(10), ' ')
        clean_snip = clean_snip.replace('[[HIGHLIGHT]]', '[bold red]').replace('[[ENDHIGHLIGHT]]', '[/bold red]')
        
        console.print(Panel(f"[bold yellow]MATCH {i+1}[/bold yellow] | Conv: [dim]{conv_id}[/dim] | Step: {step_idx} | Source: [cyan]{source}[/cyan]\n{clean_snip}", border_style="magenta"))
        
        if context_window > 0:
            try:
                s_idx = int(step_idx)
            except (ValueError, TypeError):
                s_idx = 0
                
            cursor.execute('''
                SELECT step_index, source, content
                FROM transcripts_fts
                WHERE conversation_id = ? AND CAST(step_index AS INTEGER) BETWEEN ? AND ?
                ORDER BY CAST(step_index AS INTEGER) ASC
            ''', (conv_id, s_idx - context_window, s_idx + context_window))
            
            ctx_rows = cursor.fetchall()
            for (c_idx, c_source, c_content) in ctx_rows:
                is_target = str(c_idx) == str(step_idx)
                prefix = ">>" if is_target else "  "
                style = "bold red" if is_target else "dim"
                border = "red" if is_target else "cyan"
                
                raw_content = str(c_content)
                if len(raw_content) > 2000 and not is_target:
                    raw_content = raw_content[:2000] + "\n\n... [TRUNCADO TERMODINÁMICO: >2000 chars] ..."
                
                # Renderizamos con Markdown para evitar romper los saltos de línea (C5-REAL Isomorphism)
                try:
                    renderable = Markdown(raw_content)
                except Exception:
                    renderable = Text(raw_content)
                
                import re
                # V8: Semantic Taint (URLs and absolute paths extraction)
                urls = re.findall(r'(https?://[^\s]+|file://[^\s]+|/[a-zA-Z0-9_/-]+\.[a-zA-Z0-9]+)', raw_content)
                taint_str = f" | 🔗 {len(urls)} refs" if urls else ""
                
                # V9: Git Sentinel Inverted Extraction
                sentinel_hashes = re.findall(r'\[[a-zA-Z0-9_/-]+\s([a-f0-9]{7,40})\]|([a-f0-9]{7,40})\s(?:feat|fix|refactor|docs|chore|test)', raw_content)
                sentinel_str = ""
                for group in sentinel_hashes:
                    hash_val = group[0] or group[1]
                    if hash_val:
                        sentinel_str += f" | [bold green]🛡️ SENTINEL {hash_val[:7]}[/bold green]"
                
                console.print(Panel(renderable, title=f"[{style}]{prefix} Step: {c_idx} | Source: {c_source}{taint_str}[/{style}]{sentinel_str}", border_style=border, padding=(0, 2)))

    console.print(f"\n[bold cyan]⚡ AUDIT COMPLETE[/bold cyan] Total inyecciones extraídas: {len(rows)} | TTFT Latency: [bold yellow]{latency_ms:.2f}ms[/bold yellow]")

def uds_server_thread():
    sock_path = "/tmp/nexus_bridge.sock"
    if os.path.exists(sock_path):
        os.remove(sock_path)
    
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(sock_path)
    server.listen(1)
    
    console.print(f"[bold green]🔌 UDS IPC Socket[/bold green] Listening on {sock_path}")
    
    # SQLite objects created in a thread can only be used in that same thread
    local_conn = sqlite3.connect(DB_PATH, isolation_level=None)
    
    while True:
        try:
            client, _ = server.accept()
            data = client.recv(4096).decode('utf-8').strip()
            if data:
                # C5-REAL Minimal JSON IPC Protocol: {"query": "...", "limit": 10}
                try:
                    payload = json.loads(data)
                    q = payload.get("query", "")
                    limit = payload.get("limit", 10)
                    
                    # Direct query to FTS5 without Rich UI
                    cur = local_conn.cursor()
                    cur.execute('''
                        SELECT conversation_id, step_index, source, snippet(transcripts_fts, 3, '[', ']', '...', 15) 
                        FROM transcripts_fts 
                        WHERE transcripts_fts MATCH ? 
                        ORDER BY rank LIMIT ?
                    ''', (q, limit))
                    results = cur.fetchall()
                    
                    response = json.dumps({"status": "ok", "results": results})
                    client.sendall(response.encode('utf-8'))
                except Exception as e:
                    client.sendall(json.dumps({"error": str(e)}).encode('utf-8'))
            client.close()
        except Exception:
            pass

def start_daemon(conn: sqlite3.Connection):
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        console.print("[bold red]FATAL:[/bold red] 'watchdog' no instalado. Usa: pip install watchdog")
        sys.exit(1)
        
    class TranscriptHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith("transcript.jsonl"):
                sync_transcripts(conn, force=False)
                
    observer = Observer()
    handler = TranscriptHandler()
    observer.schedule(handler, str(BRAIN_DIR), recursive=True)
    observer.start()
    
    # Spawn UDS IPC Thread
    threading.Thread(target=uds_server_thread, daemon=True).start()
    
    console.print(f"[bold magenta]👁️ NEXUS WATCHER[/bold magenta] Daemon iniciado sobre {BRAIN_DIR}. Presiona Ctrl+C para abortar.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    parser = argparse.ArgumentParser(description="Nexus Conversation Bridge (C5-REAL V7)")
    parser.add_argument("--query", help="Keyword para buscar en FTS5.")
    parser.add_argument("--limit", type=int, default=100, help="Límite termodinámico.")
    parser.add_argument("--sync", action="store_true", help="Forzar sincronización delta de logs a SQLite.")
    parser.add_argument("--force-sync", action="store_true", help="Forzar purga y resincronización total.")
    parser.add_argument("--purge", action="store_true", help="Elimina los jsonl tras la ingesta para reducir entropía (C5-REAL).")
    parser.add_argument("--context", type=int, default=0, help="Extrae N pasos anteriores y posteriores a la inyección (Contexto Causal).")
    parser.add_argument("--daemon", action="store_true", help="Inicia un Watcher en segundo plano para ingesta O(1).")
    args = parser.parse_args()
    
    conn = init_db()
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sync_metadata")
    count = cursor.fetchone()[0]
    
    if count == 0 or args.sync or args.force_sync:
        sync_transcripts(conn, force=args.force_sync, purge=args.purge)
        
    if args.daemon:
        start_daemon(conn)
    elif args.query:
        search_fts(conn, args.query, args.limit, args.context)

if __name__ == "__main__":
    main()
