#!/usr/bin/env python3
# C5-REAL SOVEREIGN: Nexus Conversation Bridge
# Bypasses the 20-context limit of Antigravity by physically exposing the brain database.

import os
import json
import argparse
from pathlib import Path
from datetime import datetime

def parse_conversations(brain_path: Path, limit: int, query: str | None = None) -> list[dict]:
    conversations = []
    
    if not brain_path.exists():
        raise FileNotFoundError(f"Brain path not found: {brain_path}")
        
    for conv_dir in brain_path.iterdir():
        if not conv_dir.is_dir():
            continue
            
        transcript_path = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if not transcript_path.exists():
            continue
            
        stat = transcript_path.stat()
        mod_time = datetime.fromtimestamp(stat.st_mtime)
        
        # Extracción física del intent inicial
        first_intent = "UNKNOWN_INTENT"
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    step = json.loads(line)
                    if step.get("type") == "USER_INPUT":
                        content = step.get("content", "")
                        clean_content = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "").strip()
                        first_intent = clean_content.split("\n")[0][:80].strip()
                        break
                except json.JSONDecodeError:
                    continue
        
        if query and query.lower() not in first_intent.lower():
            continue
            
        conversations.append({
            "id": conv_dir.name,
            "modified": mod_time,
            "intent": first_intent
        })
        
    # Sort by modification time descending
    conversations.sort(key=lambda x: x["modified"], reverse=True)
    return conversations[:limit]

def main() -> None:
    parser = argparse.ArgumentParser(description="C5-REAL: Exergy Extraction from Antigravity Brain")
    parser.add_argument("--limit", type=int, default=50, help="Number of conversations to retrieve")
    parser.add_argument("--query", type=str, default=None, help="Filter by exact keyword in intent")
    args = parser.parse_args()

    brain_path = Path(os.path.expanduser("~/.gemini/antigravity/brain"))
    
    print("█▄ C5-REAL NEXUS CONVERSATION BRIDGE")
    print(f"Scanning physical brain matrix at: {brain_path}")
    print("-" * 100)
    
    results = parse_conversations(brain_path, args.limit, args.query)
    
    for idx, c in enumerate(results, 1):
        time_str = c["modified"].strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{idx:03d}] {time_str} | ID: {c['id'][:8]}... | {c['intent']}")

if __name__ == "__main__":
    main()
