#!$CORTEX_ROOT/.venv/bin/python3
import os
import sys
import json
import argparse
from pathlib import Path

# Path to all conversation transcripts in the CORTEX environment
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"

def main():
    parser = argparse.ArgumentParser(description="Nexus Conversation Bridge (C5-REAL)")
    parser.add_argument("--query", required=True, help="Keyword a auditar en el historial infinito.")
    parser.add_argument("--limit", type=int, default=100, help="Límite termodinámico de extracciones.")
    args = parser.parse_args()

    print(f"\x1b[1;34m[NEXUS BRIDGE]\x1b[0m Rastreando el multiverso conversacional. Entropía objetivo: '{args.query}' (Límite: {args.limit})")
    
    if not BRAIN_DIR.exists():
        print(f"\x1b[1;31m[CRITICAL]\x1b[0m Brain Directory inalcanzable: {BRAIN_DIR}")
        sys.exit(1)

    matches = 0
    
    # Rastrear iterativamente los transcripts JSONL
    for transcript_file in BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"):
        conversation_id = transcript_file.parts[-4]
        
        try:
            with open(transcript_file, "r", encoding="utf-8") as f:
                for line in f:
                    if args.query.lower() in line.lower():
                        data = json.loads(line)
                        content = data.get("content", "")
                        if content and args.query.lower() in str(content).lower():
                            matches += 1
                            print(f"\n\x1b[1;32m[MATCH {matches}]\x1b[0m Conv: {conversation_id}")
                            snippet = str(content)
                            idx = snippet.lower().find(args.query.lower())
                            start = max(0, idx - 60)
                            end = min(len(snippet), idx + 100)
                            
                            source = data.get("source", "UNKNOWN")
                            print(f"  Fuente:  {source}")
                            print(f"  Payload: ...{snippet[start:end].replace(chr(10), ' ')}...")
                            
                            if matches >= args.limit:
                                print(f"\n\x1b[1;33m[HALT]\x1b[0m Límite termodinámico de {args.limit} alcanzado. Abortando rastreo profundo.")
                                sys.exit(0)
        except Exception:
            pass

    if matches == 0:
        print(f"\n\x1b[1;31m[ANERGÍA]\x1b[0m La entropía '{args.query}' no existe en ningún bloque de la red.")
    else:
        print(f"\n\x1b[1;36m[AUDIT COMPLETE]\x1b[0m Total inyecciones extraídas: {matches}")

if __name__ == "__main__":
    main()
