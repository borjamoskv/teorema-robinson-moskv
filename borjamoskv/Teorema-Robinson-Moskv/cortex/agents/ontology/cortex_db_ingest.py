#!/usr/bin/env python3
# C5-REAL: Cortex SQLite WAL Ingestor
# Parsea la matriz SSoT Markdown y la inyecta atómicamente en ~/.babylon60/cortex.db

import os
import sqlite3
import glob

DB_DIR = os.path.expanduser("~/.babylon60")
DB_PATH = os.path.join(DB_DIR, "cortex.db")

def parse_markdown_table(filepath):
    entities = []
    headers = []
    in_table = False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('|') and not line.startswith('|-'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if not in_table:
                    if parts and 'ID' in parts[0].upper():
                        headers = [h.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').lower() for h in parts]
                        in_table = True
                else:
                    if len(parts) == len(headers) and parts[0].startswith(('PRIM', 'INV', 'ANTI', 'RED', 'VEC')):
                        entities.append(dict(zip(headers, parts)))
            elif line.startswith('|-'):
                continue
            else:
                in_table = False
                
    return headers, entities

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH, timeout=5.0) # busy_timeout 5000ms
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn

def main():
    print("[*] Iniciando Extractor Causal C5-REAL -> SQLite")
    conn = init_db()
    cursor = conn.cursor()
    
    md_files = glob.glob("0*.md")
    total_ingested = 0
    
    for md_file in sorted(md_files):
        table_name = md_file.split('_', 1)[1].replace('.md', '').lower()
        headers, rows = parse_markdown_table(md_file)
        
        if not headers or not rows:
            continue
            
        print(f"[*] Cristalizando {table_name} ({len(rows)} nodos)...")
        
        # Drop table if exists to ensure zero drift
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        
        # Create table dynamically based on MD headers
        columns_def = ", ".join([f"{h} TEXT" for h in headers])
        cursor.execute(f"CREATE TABLE {table_name} ({columns_def}, PRIMARY KEY(id));")
        
        # Insert rows
        placeholders = ", ".join(["?"] * len(headers))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(headers)}) VALUES ({placeholders})"
        
        for row in rows:
            values = [row[h] for h in headers]
            cursor.execute(insert_sql, values)
            total_ingested += 1
            
    conn.commit()
    conn.close()
    
    print(f"[+] ÉXITO. {total_ingested} Entidades Inyectadas en {DB_PATH} (Modo WAL).")

if __name__ == '__main__':
    main()
