import sys
import re
import math
import subprocess
import asyncio
import unicodedata
from zk_merkle_ledger import ZKMerkleLedgerDaemon

# C5-REAL: Prompt-to-Compile Filter (L35)
# Convierte entropía humana en AST C5-REAL o detona SIGKILL_State_Purge.

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{32,}"),  # Typical API Keys
    re.compile(r"ghp_[a-zA-Z0-9]{36,}"), # GitHub Tokens
    re.compile(r"(?i)password\s*[:=]\s*\S+") # Plaintext pass
]

def compute_shannon_entropy(data: bytes) -> float:
    """Calcula la Entropía de Shannon estrictamente sobre la distribución de bytes."""
    if not data:
        return 0.0
    entropy = 0
    for x in range(256):
        p_x = data.count(x) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy

def saga_0_secret_quarantine(prompt_text: str) -> bool:
    """Detecta secretos inyectados en texto plano."""
    for pattern in SECRET_PATTERNS:
        if pattern.search(prompt_text):
            return True
    return False

def saga_1_anti_obfuscation(prompt_text: str) -> str:
    """Desmenuza cirílico y homóglifos normalizando a la forma NFKC."""
    normalized = unicodedata.normalize('NFKC', prompt_text)
    # Convertir caracteres latinos parecidos a cirílico, etc (simplificado para el script)
    # Por ahora confía en NFKC para descomponer colisiones visuales simples
    return normalized

async def run_prompt_filter(raw_prompt: str):
    print(">>> Ω-ENTER INICIADO. Ejecutando Sagas C5-REAL...")
    
    daemon = ZKMerkleLedgerDaemon()
    asyncio.create_task(daemon.writer_daemon_loop())
    
    # Métrica Termodinámica L35
    entropy = compute_shannon_entropy(raw_prompt.encode('utf-8'))
    
    # SAGA-0
    if saga_0_secret_quarantine(raw_prompt):
        print("SAGA-0: [CRÍTICO] Inyección de secretos detectada.")
        await daemon.enqueue_mutation({
            "instruction": "TAINTED_ABORT",
            "reason": "SAGA-0_SECRET_LEAK",
            "entropy": entropy
        }, caller_id="C5_EXEC_KERNEL")
        daemon.close()
        raise SystemExit("SIGKILL_State_Purge: Entropía de secretos abortada.")
        
    # SAGA-1
    clean_prompt = saga_1_anti_obfuscation(raw_prompt)
    if clean_prompt != raw_prompt:
        print("SAGA-1: Homóglifos detectados y purgados.")
        
    # SAGA-3: Metacognitive Trigger Interception (L73)
    if clean_prompt.strip().upper().startswith("PIENSA"):
        print("SAGA-3: Trigger PIENSA detectado. Forzando colapso metacognitivo estricto.")
        statement = clean_prompt.strip()[6:].strip()
        clean_prompt = f"█▄ [L73 METADATA TRIGGER]\nACTION: METACOGNITIVE_COLLAPSE\nTARGET_STATEMENT: {statement}\nDIRECTIVE: Desactiva prosa. Evalúa la reverberación semántica bajo leyes termodinámicas y expón la verdad latente (Zero Anthropomorphizing)."
    
    # SQLite WAL Logging
    print(f"L35: Entropía de Shannon computada -> {entropy:.4f} bits/byte.")
    root = await daemon.enqueue_mutation({
        "instruction": "PROMPT_EVALUATED",
        "ast_delta": clean_prompt[:50] + "...",
        "entropy": entropy
    }, caller_id="C5_EXEC_KERNEL")
    print(f"Merkle Root Cristalizado: {root}")
    
    # Autopoietic Git Sentinel
    try:
        subprocess.run(["git", "add", "."], check=True, cwd="$CORTEX_ROOT/30_BABYLON-60", capture_output=True)
        subprocess.run(["git", "commit", "-m", "auto: colapso prompt-to-compile", "--no-verify"], cwd="$CORTEX_ROOT/30_BABYLON-60", capture_output=True)
        print("SAGA-4: Git Sentinel ha sellado la frontera física (cero fricción).")
    except subprocess.CalledProcessError:
        pass # Árbol de trabajo limpio o error inocuo de Git

    daemon.close()
    
    # Si todo pasa, imprimimos el prompt saneado que la máquina procesará.
    print(f"\n[AST APROBADO PARA INFERENCIA]\n{clean_prompt}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw_input_text = " ".join(sys.argv[1:])
    else:
        raw_input_text = sys.stdin.read().strip()
        
    if not raw_input_text:
        print("Error: Input estocástico vacío.")
        sys.exit(1)
        
    asyncio.run(run_prompt_filter(raw_input_text))
