import os
import sqlite3
import subprocess
import re
import math
import json

REPO_PATH = "/Users/borjafernandezangulo/10_PROJECTS/Teorema-Robinson-Moskv"

def get_git_commits():
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
        print(f"Error reading git: {e}")
    return git_commits

def analyze_sqlite(db_path):
    tables = 0
    triggers = 0
    rows = 0
    indexes = 0
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count tables, triggers, indexes
        cursor.execute("SELECT type, count(*) FROM sqlite_master GROUP BY type")
        for r_type, count in cursor.fetchall():
            if r_type == 'table':
                tables = count
            elif r_type == 'trigger':
                triggers = count
            elif r_type == 'index':
                indexes = count
                
        # Count all rows across all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_names = [r[0] for r in cursor.fetchall()]
        for t_name in table_names:
            try:
                cursor.execute(f"SELECT count(*) FROM {t_name}")
                rows += cursor.fetchone()[0]
            except Exception:
                pass
        conn.close()
    except Exception as e:
        # DB might be locked, read-only, or corrupted. We treat it as 0
        pass
    return tables, triggers, indexes, rows

def analyze_text_file(filepath):
    invariants = 0
    mutations = 0
    
    # Read text
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return 0, 0
        
    # Invariants in Python/JS/Rust/YAML
    # Python/JS/Rust assets: assert, panic!, unwrap, expect, raise, INV_, MUTEX_
    invariants += len(re.findall(r"INV_\w+|MUTEX_\w+|assert|panic!|\.unwrap\(|\.expect\(|raise\s+\w+", content))
    
    # Mutations: writes, updates, database actions, file modification APIs
    # Python/JS/Rust: commit, write, insert, update, delete, fs.write, File::create, execute
    mutations += len(re.findall(r"\.commit\(|write_query|write_to_file|replace_file_content|execute\(|git commit|fs\.write|File::create|std::fs::write", content))
    
    return invariants, mutations

def main():
    git_commits = get_git_commits()
    files_data = []
    exclude_dirs = {".venv", "node_modules", ".git", "target"}
    
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, REPO_PATH)
            
            try:
                size = os.path.getsize(full_path)
            except OSError:
                continue
                
            commits = git_commits.get(full_path, 0)
            invariants = 0
            mutations = 0
            db_metrics = None
            
            # Identify file class
            if file.endswith(".db"):
                # Physical sqlite database analysis
                tables, triggers, indexes, rows = analyze_sqlite(full_path)
                db_metrics = {
                    "tables": tables,
                    "triggers": triggers,
                    "indexes": indexes,
                    "rows": rows
                }
                # Exergy translation of DB assets: 
                # Each trigger = 15 invariants (strict state control)
                # Each table = 5 invariants
                # Each index = 2 invariants
                # Every 100 rows = 1 mutation (kinetic state)
                invariants = tables * 5 + triggers * 15 + indexes * 2
                mutations = math.ceil(rows / 100)
            elif file.endswith(".safetensors"):
                # Weights represent parameters (constraints on inference space). We give a proportional static exergy
                # because they are static weight parameters
                invariants = 1500
                mutations = 0
            else:
                # Text files (Python, Rust, YAML, Javascript, MD, etc.)
                invariants, mutations = analyze_text_file(full_path)
                
            # Exergy Equation (Pure algebraic non-pseudophysics metrics)
            # Ex = 0.3 * ln(Size) + 2.0 * Commits + 4.0 * Invariants + 3.0 * Mutations
            size_term = math.log(size + 1) * 0.3
            commits_term = commits * 2.0
            invariants_term = invariants * 4.0
            mutations_term = mutations * 3.0
            
            exergy_score = size_term + commits_term + invariants_term + mutations_term
            
            # Classification M12
            m12_class = "AP"
            if "master_ledger" in file or "ledger" in file:
                m12_class = "CP-local (Single-writer)"
            elif file == "cortex_memory.db":
                m12_class = "Congelado (RO)"
            elif file == "adapters.safetensors":
                m12_class = "Reglas (R)"
            elif "ontology" in root or "ontology" in file:
                m12_class = "Axiomas (A)"
                
            files_data.append({
                "path": rel_path,
                "size": size,
                "commits": commits,
                "invariants": invariants,
                "mutations": mutations,
                "db_metrics": db_metrics,
                "exergy": round(exergy_score, 2),
                "m12_class": m12_class
            })
            
    # Sort
    files_data.sort(key=lambda x: x["exergy"], reverse=True)
    print(json.dumps(files_data[:10], indent=2))

if __name__ == "__main__":
    main()
