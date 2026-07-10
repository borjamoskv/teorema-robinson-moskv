import os
import sqlite3
import subprocess
import re
import math
import json
import hashlib
import ast
import concurrent.futures
from typing import Dict, Tuple, Any

REPO_PATH = "/Users/borjafernandezangulo/10_PROJECTS/Teorema-Robinson-Moskv"

def get_git_commits() -> Dict[str, int]:
    git_commits = {}
    try:
        res = subprocess.run(
            ["git", "log", "--pretty=format:", "--name-only"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        for line in res.stdout.splitlines():
            line = line.strip()
            if line and os.path.exists(os.path.join(REPO_PATH, line)):
                full_path = os.path.join(REPO_PATH, line)
                git_commits[full_path] = git_commits.get(full_path, 0) + 1
    except Exception as e:
        pass
    return git_commits

def calculate_sha256(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return "ERROR_HASH"

def analyze_sqlite(db_path: str) -> Tuple[int, int, int, int]:
    tables, triggers, indexes, rows = 0, 0, 0, 0
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT type, count(*) FROM sqlite_master GROUP BY type")
        for r_type, count in cursor.fetchall():
            if r_type == 'table': tables = count
            elif r_type == 'trigger': triggers = count
            elif r_type == 'index': indexes = count
                
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        for r in cursor.fetchall():
            try:
                cursor.execute(f"SELECT count(*) FROM {r[0]}")
                rows += cursor.fetchone()[0]
            except Exception:
                pass
        conn.close()
    except Exception:
        pass
    return tables, triggers, indexes, rows

def analyze_ast(content: str) -> int:
    try:
        tree = ast.parse(content)
        # Measure AST density: Functions, Classes, Returns, Yields, Awaits
        density = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Return, ast.Yield, ast.Await)))
        return density
    except Exception:
        return 0

def analyze_text_file(filepath: str) -> Tuple[int, int, int]:
    invariants, mutations, ast_density = 0, 0, 0
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return 0, 0, 0
        
    invariants += len(re.findall(r"INV_\w+|MUTEX_\w+|assert|panic!|\.unwrap\(|\.expect\(|raise\s+\w+", content))
    mutations += len(re.findall(r"\.commit\(|write_query|write_to_file|replace_file_content|execute\(|git commit|fs\.write|File::create|std::fs::write", content))
    
    if filepath.endswith(".py"):
        ast_density = analyze_ast(content)
        
    return invariants, mutations, ast_density

def process_file(full_path: str, commits: int, repo_path: str) -> Dict[str, Any]:
    rel_path = os.path.relpath(full_path, repo_path)
    try:
        size = os.path.getsize(full_path)
    except OSError:
        return None
        
    file_hash = calculate_sha256(full_path)
    invariants, mutations, ast_density = 0, 0, 0
    db_metrics = None
    
    if full_path.endswith(".db"):
        tables, triggers, indexes, rows = analyze_sqlite(full_path)
        db_metrics = {"tables": tables, "triggers": triggers, "indexes": indexes, "rows": rows}
        invariants = tables * 5 + triggers * 15 + indexes * 2
        mutations = math.ceil(rows / 100)
    elif full_path.endswith(".safetensors"):
        invariants = 1500
    else:
        invariants, mutations, ast_density = analyze_text_file(full_path)
        
    # AST Density augments invariants structurally
    total_invariants = invariants + ast_density
    
    size_term = math.log(size + 1) * 0.3
    commits_term = commits * 2.0
    invariants_term = total_invariants * 4.0
    mutations_term = mutations * 3.0
    
    exergy_score = size_term + commits_term + invariants_term + mutations_term
    
    m12_class = "AP"
    if "master_ledger" in rel_path or "ledger" in rel_path:
        m12_class = "CP-local (Single-writer)"
    elif rel_path == "cortex_memory.db":
        m12_class = "Congelado (RO)"
    elif rel_path == "adapters/adapters.safetensors":
        m12_class = "Reglas (R)"
    elif "ontology" in rel_path:
        m12_class = "Axiomas (A)"
        
    return {
        "path": rel_path,
        "sha256": file_hash,
        "size": size,
        "commits": commits,
        "invariants": total_invariants,
        "mutations": mutations,
        "ast_density": ast_density,
        "db_metrics": db_metrics,
        "exergy": round(exergy_score, 2),
        "m12_class": m12_class
    }

def main():
    git_commits = get_git_commits()
    exclude_dirs = {".venv", "node_modules", ".git", "target"}
    
    target_files = []
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            full_path = os.path.join(root, file)
            target_files.append((full_path, git_commits.get(full_path, 0), REPO_PATH))
            
    files_data = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_file, fp, c, rp): fp for fp, c, rp in target_files}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                files_data.append(res)
            
    files_data.sort(key=lambda x: x["exergy"], reverse=True)
    print(json.dumps(files_data[:10], indent=2))

if __name__ == "__main__":
    main()
