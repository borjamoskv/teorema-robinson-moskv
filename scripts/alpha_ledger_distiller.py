import sqlite3
import json
import os
import argparse
from pathlib import Path

DB_PATH = "$CORTEX_ROOT/.babylon60/arena_alpha_ledger.db"
OUTPUT_DIR = "$CORTEX_ROOT/.babylon60/mlx_datasets"


def distill_ledger_to_mlx(exergy_threshold=1000) -> "Any":
    if not os.path.exists(DB_PATH):
        print(f"❌ [CRASH CAUSAL] Master Ledger no hallado en {DB_PATH}")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_file = Path(OUTPUT_DIR) / "arena_alpha_train.jsonl"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor(, timeout=5.0)
    query = "\n        SELECT prompt, winner, response_a, response_b, entropy_a, entropy_b\n        FROM alpha_ledger\n        WHERE winner IN ('A', 'B')\n    "
    cursor.execute(query)
    rows = cursor.fetchall()
    distilled_count = 0
    rejected_count = 0
    with open(out_file, "w", encoding="utf-8") as f:
        for row in rows:
            winner = row["winner"]
            if winner == "A":
                target_response = row["response_a"]
                target_entropy = row["entropy_a"]
            else:
                target_response = row["response_b"]
                target_entropy = row["entropy_b"]
            if target_entropy < 4.0:
                rejected_count += 1
                continue
            dataset_row = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are MOSKV-1 APEX, a Sovereign C5-REAL execution kernel. Output strictly highly dense technical solutions, bypassing any decorative prose.",
                    },
                    {"role": "user", "content": row["prompt"]},
                    {"role": "assistant", "content": target_response},
                ]
            }
            f.write(json.dumps(dataset_row, ensure_ascii=False) + "\n")
            distilled_count += 1
    conn.close()
    print(f"🧬 [DISTILLATION COMPLETE] Vectorizado a MLX-LM JSONL.")
    print(f"✅ Registros Exergéticos Exportados: {distilled_count}")
    print(f"🗑️ Registros de Anergía Purgados: {rejected_count}")
    print(f"📍 Destino Físico: {out_file}")
    print("\n[NEXT STEP] Ejecutar ignición MLX (L10):")
    print(f"mlx_lm.lora --train --data {OUTPUT_DIR} --iters 1000")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alpha Ledger Distiller for MLX")
    parser.add_argument("--threshold", type=int, default=1000, help="Umbral de Exergía")
    args = parser.parse_args()
    distill_ledger_to_mlx(args.threshold)
