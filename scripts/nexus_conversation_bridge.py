#!/Users/borjafernandezangulo/.venv/bin/python3
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

def process_file(transcript_file: Path, query: str, is_regex: bool, context_lines: int) -> List[Dict[str, Any]]:
    matches = []
    conversation_id = transcript_file.parts[-4]
    
    try:
        pattern = re.compile(query, re.IGNORECASE) if is_regex else None
        query_lower = query.lower()

        with open(transcript_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if (not is_regex and query_lower not in line.lower()) or (is_regex and not pattern.search(line)):
                continue
                
            data = json.loads(line)
            content_str = str(data.get("content", ""))
            
            if not content_str:
                continue
                
            content_lines = content_str.split('\n')
            matched_line_indices = []
            
            for idx, cl in enumerate(content_lines):
                if (is_regex and pattern.search(cl)) or (not is_regex and query_lower in cl.lower()):
                    matched_line_indices.append(idx)
                    
            if not matched_line_indices:
                matched_line_indices = [0]
                
            first_match = matched_line_indices[0]
            last_match = matched_line_indices[-1]
            
            start_line = max(0, first_match - context_lines)
            end_line = min(len(content_lines), last_match + context_lines + 1)
            
            context_snippet = '\n'.join(content_lines[start_line:end_line])
            
            matches.append({
                "conversation_id": conversation_id,
                "source": data.get("source", "UNKNOWN"),
                "step": data.get("step_index", "N/A"),
                "snippet": context_snippet
            })
    except Exception:
        pass
    return matches

def main():
    parser = argparse.ArgumentParser(description="Nexus Conversation Bridge (C5-REAL)")
    parser.add_argument("--query", required=True, help="Keyword o Regex a auditar en el historial infinito.")
    parser.add_argument("--limit", type=int, default=100, help="Límite termodinámico de extracciones.")
    parser.add_argument("--context", type=int, default=2, help="Líneas de contexto (N) arriba y abajo del match.")
    parser.add_argument("--regex", action="store_true", help="Procesar query como Expresión Regular.")
    parser.add_argument("--json", action="store_true", help="Salida en JSON puro para composabilidad de pipelines.")
    parser.add_argument("--workers", type=int, default=4, help="Número de hilos concurrentes para aniquilación de latencia IO.")
    args = parser.parse_args()

    if not args.json:
        mode = "Regex" if args.regex else "Keyword"
        ctx_msg = f" (+ Contexto de {args.context} líneas)" if args.context > 0 else ""
        print(f"\x1b[1;34m[NEXUS BRIDGE]\x1b[0m Rastreando el multiverso conversacional ({mode}). Entropía: '{args.query}' (Límite: {args.limit}){ctx_msg}")
    
    if not BRAIN_DIR.exists():
        if not args.json:
            print(f"\x1b[1;31m[CRITICAL]\x1b[0m Brain Directory inalcanzable: {BRAIN_DIR}")
        sys.exit(1)

    files = list(BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"))
    all_matches = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_file, f, args.query, args.regex, args.context): f for f in files}
        
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
        print(f"\n\x1b[1;32m[MATCH {i+1}]\x1b[0m Conv: {match['conversation_id']} | Step: {match['step']}")
        print(f"  Fuente:  {match['source']}")
        print(f"  Contexto ({args.context} líneas):\n\x1b[36m{match['snippet']}\x1b[0m")
    
    if not all_matches:
        print(f"\n\x1b[1;31m[ANERGÍA]\x1b[0m La entropía '{args.query}' no existe en ningún bloque de la red.")
    else:
        print(f"\n\x1b[1;36m[AUDIT COMPLETE]\x1b[0m Total inyecciones extraídas: {len(all_matches)}")

if __name__ == "__main__":
    main()
