#!/usr/bin/env python3
# [C5-REAL] CENTURIA FORGE
# SYS_ID: borjamoskv
# Surface Mapping Engine - 100 Threads

import os
import sqlite3
import math
import ast
import re
import json
import logging
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

IGNORED_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".next", "dist", "build"}
IGNORED_EXTS = {".pyc", ".db", ".png", ".jpg", ".pdf", ".zip", ".tar", ".gz"}

DB_PATH = "cortex_surface_map.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS surface_map (
            file_path TEXT PRIMARY KEY,
            extension TEXT,
            entropy REAL,
            lines INTEGER,
            classes TEXT,
            functions TEXT,
            imports TEXT
        )
    ''')
    conn.commit()
    conn.close()

def calculate_shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    frequencies = {}
    for char in text:
        frequencies[char] = frequencies.get(char, 0) + 1
    total_len = len(text)
    entropy = 0.0
    for count in frequencies.values():
        p = count / total_len
        entropy -= p * math.log2(p)
    return round(entropy, 4)

def extract_python_primitives(content: str):
    classes = []
    functions = []
    imports = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception:
        pass
    return classes, functions, list(set(imports))

def extract_generic_primitives(content: str):
    classes = re.findall(r"class\s+([a-zA-Z0-9_]+)", content)
    functions = re.findall(r"function\s+([a-zA-Z0-9_]+)", content)
    functions += re.findall(r"(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:function|\()", content)
    imports = re.findall(r"(?:import|require)\s*\(?['\"]([^'\"]+)['\"]", content)
    return list(set(classes)), list(set(functions)), list(set(imports))

def analyze_file(filepath: Path):
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None
    
    entropy = calculate_shannon_entropy(content)
    lines = len(content.splitlines())
    
    if filepath.suffix == ".py":
        classes, functions, imports = extract_python_primitives(content)
    else:
        classes, functions, imports = extract_generic_primitives(content)
        
    return {
        "file_path": str(filepath),
        "extension": filepath.suffix,
        "entropy": entropy,
        "lines": lines,
        "classes": json.dumps(classes),
        "functions": json.dumps(functions),
        "imports": json.dumps(imports)
    }

def worker_thread(filepath: Path):
    data = analyze_file(filepath)
    if not data:
        return None
    
    # R10: Concurrencia aislada SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    try:
        conn.execute('''
            INSERT OR REPLACE INTO surface_map 
            (file_path, extension, entropy, lines, classes, functions, imports)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["file_path"], data["extension"], data["entropy"],
            data["lines"], data["classes"], data["functions"], data["imports"]
        ))
        conn.commit()
    except Exception as e:
        logging.error(f"DB Error on {filepath}: {e}")
    finally:
        conn.close()
    return filepath

def get_target_files(root_dir: Path):
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Apply ignores
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for f in filenames:
            path = Path(dirpath) / f
            if path.suffix not in IGNORED_EXTS:
                files.append(path)
    return files

def main():
    parser = argparse.ArgumentParser(description="Centuria Forge Surface Mapping")
    parser.add_argument("--dir", default=".", help="Target directory")
    args = parser.parse_args()
    
    target_dir = Path(args.dir).resolve()
    logging.info(f"Initiating Centuria Forge (100 cycles) on {target_dir}")
    
    init_db()
    files = get_target_files(target_dir)
    logging.info(f"Discovered {len(files)} target files for surface mapping.")
    
    success_count = 0
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(worker_thread, f): f for f in files}
        for future in as_completed(futures):
            res = future.result()
            if res:
                success_count += 1
                
    logging.info(f"Surface Mapping Complete. Successfully mapped {success_count} / {len(files)} files.")
    logging.info(f"Results crystallized in {DB_PATH}")

if __name__ == "__main__":
    main()
