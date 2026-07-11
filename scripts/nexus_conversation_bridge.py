#!$CORTEX_ROOT/.venv/bin/python3
import os
import sys
import json
import argparse
import re
from pathlib import Path
import concurrent.futures
from typing import List, Dict, Any

# Path to all conversation transcripts in the CORTEX environment
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"

def process_file_with_context(transcript_file: Path, query: str, is_regex: bool, context_window: int) -> List[Dict[str, Any]]:
    matches = []
    conversation_id = transcript_file.parts[-4]
    
    try:
        pattern = re.compile(query, re.IGNORECASE) if is_regex else None
        query_lower = query.lower()

        # Load all lines for context window indexing
        lines = []
        with open(transcript_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if (not is_regex and query_lower not in line.lower()) or (is_regex and not pattern.search(line)):
                continue
                
            data = json.loads(line)
            content = data.get("content", "")
            content_str = str(content)
            
            if not content_str:
                continue
                
            match_found = False
            if is_regex and pattern.search(content_str):
                match_found = True
            elif not is_regex and query_lower in content_str.lower():
                match_found = True
                
            if match_found:
                idx = content_str.lower().find(query_lower) if not is_regex else pattern.search(content_str).start()
                start = max(0, idx - 60)
                end = min(len(content_str), idx + 100)
                snippet = "..." + content_str[start:end].replace('\n', ' ') + "..."
                
                # Extract Temporal Context
                ctx_start = max(0, i - context_window)
                ctx_end = min(len(lines), i + context_window + 1)
                context_block = []
                
                for ctx_i in range(ctx_start, ctx_end):
                    try:
                        ctx_data = json.loads(lines[ctx_i])
                        context_block.append({
                            "step_index": ctx_data.get("step_index", ctx_i),
                            "source": ctx_data.get("source", "UNKNOWN"),
                            "type": ctx_data.get("type", "UNKNOWN"),
                            "content": str(ctx_data.get("content", ""))[:500] # Truncate long contexts to 500 chars to avoid memory explosion
                        })
                    except Exception:
                        pass

                matches.append({
                    "conversation_id": conversation_id,
                    "source": data.get("source", "UNKNOWN"),
                    "snippet": snippet,
                    "context_window_size": context_window,
                    "trajectory_context": context_block
                })
    except Exception:
        pass
    return matches

def main():
    parser = argparse.ArgumentParser(description="Nexus Conversation Bridge (C5-REAL)")
    parser.add_argument("--query", required=True, help="Keyword o Regex a auditar en el historial infinito.")
    parser.add_argument("--limit", type=int, default=100, help="Límite termodinámico de extracciones.")
    parser.add_argument("--regex", action="store_true", help="Procesar query como Expresión Regular.")
    parser.add_argument("--json", action="store_true", help="Salida en JSON puro para composabilidad de pipelines.")
    parser.add_argument("--workers", type=int, default=4, help="Número de hilos concurrentes para aniquilación de latencia IO.")
    parser.add_argument("--context", type=int, default=0, help="Ventana de contexto temporal: Extrae N pasos anteriores y N pasos posteriores a la inyección.")
    args = parser.parse_args()

    if not args.json:
        mode = "Regex" if args.regex else "Keyword"
        ctx_msg = f" (+ Contexto de ±{args.context} pasos)" if args.context > 0 else ""
        print(f"\x1b[1;34m[NEXUS BRIDGE]\x1b[0m Rastreando el multiverso conversacional ({mode}). Entropía: '{args.query}' (Límite: {args.limit}){ctx_msg}")
    
    if not BRAIN_DIR.exists():
        if not args.json:
            print(f"\x1b[1;31m[CRITICAL]\x1b[0m Brain Directory inalcanzable: {BRAIN_DIR}")
        sys.exit(1)

    files = list(BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"))
    all_matches = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_file_with_context, f, args.query, args.regex, args.context): f for f in files}
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                all_matches.extend(res)
                if len(all_matches) >= args.limit:
                    all_matches = all_matches[:args.limit]
                    break
    
    if args.json:
        print(json.dumps({"query": args.query, "matches": all_matches}, indent=2))
        sys.exit(0)

    for i, match in enumerate(all_matches):
        print(f"\n\x1b[1;32m[MATCH {i+1}]\x1b[0m Conv: {match['conversation_id']}")
        print(f"  Fuente:  {match['source']}")
        print(f"  Payload: {match['snippet']}")
        
        if args.context > 0:
            print(f"  \x1b[1;35m[CONTEXTO TEMPORAL ±{args.context}]\x1b[0m")
            for ctx in match['trajectory_context']:
                prefix = ">>" if ctx['source'] == match['source'] and ctx['content'][:20] in match['snippet'] else "  "
                print(f"    {prefix} [{ctx['step_index']}] {ctx['source']} ({ctx['type']}): {ctx['content'][:100]}...")
    
    if not all_matches:
        print(f"\n\x1b[1;31m[ANERGÍA]\x1b[0m La entropía '{args.query}' no existe en ningún bloque de la red.")
    else:
        print(f"\n\x1b[1;36m[AUDIT COMPLETE]\x1b[0m Total inyecciones extraídas: {len(all_matches)}")

if __name__ == "__main__":
    main()
