#!/usr/bin/env python3
# C5-REAL: Fact Extractor Masivo

import os
import sqlite3
import json
import glob

def init_db(db_path):
    conn = sqlite3.connect(db_path, timeout=5.0)
    return conn

def extract_from_db(db_path):
    conn = init_db(db_path)
    cursor = conn.cursor()
    facts = []
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facts';")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM facts;")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                fact = dict(zip(columns, row))
                fact['_source_db'] = db_path
                fact['_source_table'] = 'facts'
                facts.append(fact)
                
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vec_facts';")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM vec_facts;")
            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                fact = dict(zip(columns, row))
                fact['_source_db'] = db_path
                fact['_source_table'] = 'vec_facts'
                facts.append(fact)
                
    finally:
        conn.close()
        
    return facts

def main():
    print("[*] Iniciando Extracción Masiva de Facts (C5-REAL)")
    db_paths = []
    db_paths.extend(glob.glob(os.path.expanduser("~/.cortex/*.db")))
    db_paths.extend(glob.glob(os.path.expanduser("~/.cortex/*.sqlite")))
    db_paths.extend(glob.glob(os.path.expanduser("~/.babylon60/*.db")))
    
    all_facts = []
    
    for db in db_paths:
        db_facts = extract_from_db(db)
        if db_facts:
            print(f"[+] {db}: {len(db_facts)} facts encontrados.")
            all_facts.extend(db_facts)
            
    print(f"\\n[*] Total Facts consolidados: {len(all_facts)}")
    
    out_dir = os.path.expanduser("~/.cortex/snapshots")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "facts_raw_export.jsonl")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        for fact in all_facts:
            f.write(json.dumps(fact, ensure_ascii=False) + '\\n')
            
    print(f"[+] Export completado en {out_file}")

if __name__ == '__main__':
    main()
