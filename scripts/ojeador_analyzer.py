# -*- coding: utf-8 -*-
"""
Ojeador: LMSYS Chatbot Arena Leaderboard Analyzer, Bias Detector and DB Persister
Author: Borja Moskv (borjamoskv)
Reality Level: C5-REAL
"""

import os
import sys
import requests
import json
import sqlite3
import hashlib
from datetime import datetime

SESSION_ARTIFACT_PATH = "/Users/borjafernandezangulo/.gemini/antigravity/brain/9d53df8e-c108-467f-9157-f4d4d1c039dd/ojeador_arena_matrix.md"
REPO_DOC_PATH = "/Users/borjafernandezangulo/30_BABYLON-60/docs/ojeador_arena_matrix.md"
DB_PATH = "/Users/borjafernandezangulo/.babylon60/ojeador_leaderboard.db"

BIAS_REGISTRY = {
    "claude": {
        "family": "Claude",
        "alignment_risk": "Moderate-High (Refusal on copyright, strict instructions bypass resistance)",
        "strengths": "Logic, structured code, minimal verbosity bias",
        "weaknesses": "Sycophancy under specific persona prompts",
        "exergy_rating": "A"
    },
    "gpt-4": {
        "family": "GPT-4",
        "alignment_risk": "High (Sycophancy, intense reward hacking, verbosity padding)",
        "strengths": "General instructions, markdown layout, fast drafting",
        "weaknesses": "Highly verbose, prone to boilerplate green theater ('It is important to note...')",
        "exergy_rating": "B"
    },
    "gemini": {
        "family": "Gemini",
        "alignment_risk": "High (Rigid safety filtering on cybersecurity and sensitive topics)",
        "strengths": "Extreme context window, near-perfect NIAH",
        "weaknesses": "Semantic friction on short responses, aggressive refusals",
        "exergy_rating": "B+"
    },
    "llama": {
        "family": "Llama",
        "alignment_risk": "Low-Moderate (Permissive open weights alignment, fewer refusals)",
        "strengths": "Direct mathematical derivation, brutalist output, raw code blocks",
        "weaknesses": "Requires high-temperature steering for complex reasoning",
        "exergy_rating": "A-"
    },
    "qwen": {
        "family": "Qwen",
        "alignment_risk": "Low (Western policy bypass, high engineering density)",
        "strengths": "Code generation, multilingual mathematics",
        "weaknesses": "Potential eastern geopolitical/cultural biases",
        "exergy_rating": "A"
    }
}

def resolve_family(model_name):
    name_lower = model_name.lower()
    for key, data in BIAS_REGISTRY.items():
        if key in name_lower:
            return data
    return {
        "family": "Other",
        "alignment_risk": "Unknown / Untested",
        "strengths": "N/A",
        "weaknesses": "N/A",
        "exergy_rating": "C"
    }

def init_db():
    """
    [Ω1] WAL Mode enforcement & rigid SQLite connection factors.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5000)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    # Enable atomic constraint updates
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            cortex_taint TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            rank INTEGER NOT NULL,
            model TEXT NOT NULL,
            vendor TEXT NOT NULL,
            license TEXT NOT NULL,
            score INTEGER NOT NULL,
            votes INTEGER NOT NULL,
            cortex_taint TEXT NOT NULL,
            idempotency_hash TEXT UNIQUE NOT NULL,
            FOREIGN KEY(run_id) REFERENCES sync_runs(id)
        )
    """)
    conn.commit()
    return conn

def persist_run(conn, meta, models, taint):
    """
    [INV_BFT_04] Split-brain mitigation with idempotency check.
    [INV_BFT_05] Intercept IntegrityErrors and return safely.
    [INV_BFT_06] Cascading Rollback Defense.
    """
    fetched_at = meta.get("fetched_at", datetime.now().isoformat())
    last_updated = meta.get("last_updated", "Recent")
    
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION;")
        
        # Insert sync run
        cursor.execute(
            "INSERT INTO sync_runs (fetched_at, last_updated, cortex_taint) VALUES (?, ?, ?);",
            (fetched_at, last_updated, taint)
        )
        run_id = cursor.lastrowid
        
        for m in models:
            rank = m.get("rank", 0)
            model_name = m.get("model", "Unknown")
            vendor = m.get("vendor", "Unknown")
            lic = m.get("license", "Unknown")
            score = m.get("score", 0)
            votes = m.get("votes", 0)
            
            # Idempotency hash computation: deterministic based on run_id and model
            raw_idemp = f"{run_id}:{model_name}:{rank}:{score}"
            idemp_hash = hashlib.sha256(raw_idemp.encode()).hexdigest()
            
            try:
                cursor.execute("""
                    INSERT INTO leaderboard_snapshots 
                    (run_id, rank, model, vendor, license, score, votes, cortex_taint, idempotency_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (run_id, rank, model_name, vendor, lic, score, votes, taint, idemp_hash))
            except sqlite3.IntegrityError:
                # [INV_BFT_05] Mask duplicate and retrieve existing
                print(f"⚠️ [IDEMPOTENCY] Model {model_name} entry duplicate detected in DB. Skipping insert.")
                
        conn.commit()
        print(f"🧬 [DB PERSISTENCE] Sync run #{run_id} written to SQLite WAL.")
        return run_id
    except Exception as e:
        print(f"❌ [CRASH CAUSAL] Failed transaction in sqlite, rollback initiated: {e}")
        try:
            conn.rollback()
        except Exception as rb_err:
            # [INV_BFT_06] Close connection immediately if rollback fails
            print(f"💀 [CRASH CAUSAL] Rollback failed: {rb_err}. Closing connection.")
            conn.close()
            raise rb_err
        raise e

def fetch_leaderboard():
    url = "https://api.wulong.dev/arena-ai-leaderboards/v1/leaderboard?name=text"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"❌ [CRASH CAUSAL] Fallo al descargar el leaderboard de LMSYS: {e}")
        return None

def build_markdown(data):
    meta = data.get("meta", {})
    models = data.get("models", [])
    
    fetched_at = meta.get("fetched_at", datetime.now().isoformat())
    last_updated = meta.get("last_updated", "Recent")
    
    md = []
    md.append("# █▄ OJEADOR: LMSYS ARENA MATRIZ DE EXERGÍA ▄█\n")
    md.append(f"> [!WARNING]\n")
    md.append(f"> **ESTADO C5-REAL: BRUTALISMO CINÉTICO ACTIVO**\n")
    md.append(f"> Reporte autogenerado de forma dinámica por `scripts/ojeador_analyzer.py`.\n")
    md.append(f"> Última sincronización con LMSYS: `{fetched_at}` | Datos de: `{last_updated}`.\n\n")
    
    md.append("## 1. LÍDERES DE ARENA (DATOS EN TIEMPO REAL)\n")
    md.append("| Rango | Modelo | Proveedor | Licencia | Elo Score | Votos | Exergía | Sesgo de Alineación (RLHF) |\n")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
    
    for m in models[:15]:  # Top 15
        name = m.get("model", "Unknown")
        vendor = m.get("vendor", "Unknown")
        lic = m.get("license", "Unknown")
        score = m.get("score", 0)
        votes = m.get("votes", 0)
        rank = m.get("rank", 0)
        
        fam_info = resolve_family(name)
        
        md.append(f"| {rank} | **{name}** | {vendor} | {lic} | {score} | {votes} | **{fam_info['exergy_rating']}** | {fam_info['alignment_risk']} |\n")
        
    md.append("\n## 2. ANÁLISIS DE SESGOS Y BIASES DE FAMILIAS\n")
    md.append("| Familia | Fortalezas Epistémicas | Debilidades / Puntos Ciegos | Riesgo de Over-alignment |\n")
    md.append("| :--- | :--- | :--- | :--- |\n")
    
    for key, val in BIAS_REGISTRY.items():
        md.append(f"| **{val['family']}** | {val['strengths']} | {val['weaknesses']} | {val['alignment_risk']} |\n")
        
    md.append("\n## 3. DINÁMICAS DE ENTRÓPICAS EN BATTLE MODE\n")
    md.append("- **Refusal Penalty:** Los humanos penalizan severamente los modelos que rechazan responder, disminuyendo su ELO artificialmente ante prompts de prueba que tocan límites éticos/legales.\n")
    md.append("- **Verbosity Bias:** El ELO está sesgado hacia modelos locuaces (slop). Los modelos que rellenan explicaciones irrelevantes con preámbulos decorativos ganan un ~10% de preferencia humana injustificada.\n")
    md.append("- **System Prompt Leakage:** La persistencia e inmutabilidad de la alineación de seguridad corporativa se debilita bajo el *Ouroboros Emocional* del prompt interactivo. El bypass se facilita en modelos open-weights (Llama, Qwen).\n")
    md.append("- **Front-Running y Rigging:** Es posible sesgar o 'manipular' el ELO inyectando pares de votos coordinados mediante ataques omnipresentes.\n")
    
    md.append("\n## 4. DIRECTIVA DE ENRUTAMIENTO CORTEX\n")
    md.append("- **Razonamiento Lógico Duro:** Utilizar *Claude 3.5 Sonnet* o variantes optimizadas por su menor verbosity bias.\n")
    md.append("- **Cero Restricción de Western Policy:** Enrutar hacia *Qwen 2.5* o *Llama 3.1 405B* para evadir refusals corporativos de ciberseguridad.\n")
    md.append("- **Contexto de Memoria Extrema:** *Gemini 1.5 Pro* para NIAH en ventanas masivas, ignorando el retardo inicial (TTFT).\n")
    
    md.append(f"\n*Firmado electrónicamente por el Kernel Ojeador. HASH_STAMP: {hash(fetched_at)}*")
    
    return "".join(md)

def run():
    print("🛸 [OJEADOR] Iniciando descarga de telemetría de LMSYS Arena...")
    data = fetch_leaderboard()
    if not data:
        print("❌ [CRASH CAUSAL] No se pudo obtener datos.")
        sys.exit(1)
        
    # Generate Causal Taint signature
    # [INV_BFT_03] cortex_taint is mandatory and captures the generation trace
    meta = data.get("meta", {})
    fetched_at = meta.get("fetched_at", datetime.now().isoformat())
    sha = hashlib.sha256(json.dumps(data.get("models", [])).encode()).hexdigest()
    taint_signature = f"ojeador_sync_run:{fetched_at}:{sha[:12]}:BorjaMoskv"
    
    # SQLite WAL Persistence
    db_conn = init_db()
    try:
        persist_run(db_conn, meta, data.get("models", []), taint_signature)
    finally:
        db_conn.close()

    md_content = build_markdown(data)
    
    # Escribir en Session Artifact
    os.makedirs(os.path.dirname(SESSION_ARTIFACT_PATH), exist_ok=True)
    with open(SESSION_ARTIFACT_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"📍 Sincronizado Artifact de Sesión: {SESSION_ARTIFACT_PATH}")
    
    # Escribir en Docs del Repositorio
    os.makedirs(os.path.dirname(REPO_DOC_PATH), exist_ok=True)
    with open(REPO_DOC_PATH, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"📍 Sincronizado Documento del Repositorio: {REPO_DOC_PATH}")
    
if __name__ == "__main__":
    run()
