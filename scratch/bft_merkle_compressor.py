import subprocess
import hashlib
import json

def get_git_commits(limit=5):
    """Extrae los últimos N hashes de commits del Ledger."""
    result = subprocess.check_output(["git", "log", f"-n{limit}", "--format=%H"])
    return result.decode('utf-8').strip().split('\n')

def compute_merkle_root(hashes):
    """Construye un Merkle Root simplificado a partir de los hashes."""
    if not hashes:
        return None
    if len(hashes) == 1:
        return hashes[0]
    
    next_level = []
    for i in range(0, len(hashes), 2):
        hash1 = hashes[i]
        hash2 = hashes[i+1] if i+1 < len(hashes) else hash1
        combined = (hash1 + hash2).encode('utf-8')
        next_level.append(hashlib.sha256(combined).hexdigest())
        
    return compute_merkle_root(next_level)

def main():
    try:
        commits = get_git_commits(limit=5)
        root_hash = compute_merkle_root(commits)
        
        payload = {
            "protocol": "CORTEX_C5_REAL",
            "type": "MCTS_BUDGET_FORCER_SINK",
            "merkle_root": root_hash,
            "commit_count": len(commits)
        }
        
        # El payload de OP_RETURN (Bitcoin) tiene un límite físico estricto de 80 bytes.
        # Por tanto, extraemos solo el hash maestro para el anclaje.
        op_return_hex = payload["merkle_root"][:64]
        
        yaml_receipt = f"""
Claim: Compresión de Entropía Local para Inyección Blockchain (External Witness Sink).
Proof:
  Base: [Git Commits: {len(commits)}, Merkle Root: {op_return_hex[:16]}...]
  Range: [Local Ledger, BTC OP_RETURN Payload (32 Bytes)]
  Confidence: C5-REAL
"""
        print(yaml_receipt.strip())
        print(f"\n█▄ PAYLOAD OP_RETURN GENERADO: {op_return_hex}")
        print("█▄ STATUS: LISTO PARA TRANSACCIÓN BLOCKCHAIN L1.")
        
    except Exception as e:
        print(f"SIGKILL_State_Purge: Fallo en compresión Merkle -> {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
