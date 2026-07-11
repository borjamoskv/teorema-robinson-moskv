#!$CORTEX_ROOT/.venv/bin/python3
# C5-REAL SOVEREIGN: Nexus Conversation Bridge (V2 - Chronological & Grouped)
# Bypasses the 20-context limit of Antigravity by physically exposing and index-searching the brain database.

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Path to all conversation transcripts in the CORTEX environment
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
BUILD_NEXUS_SCRIPT = Path.home() / ".gemini" / "antigravity" / "scratch" / "build_conversations_nexus.py"

def rebuild_dashboard() -> None:
    print("\x1b[1;36m[REBUILDING]\x1b[0m Ejecutando build_conversations_nexus.py...")
    if not BUILD_NEXUS_SCRIPT.exists():
        print(f"\x1b[1;31m[ERROR]\x1b[0m Script indexador no encontrado en: {BUILD_NEXUS_SCRIPT}")
        return
    try:
        res = subprocess.run([sys.executable, str(BUILD_NEXUS_SCRIPT)], capture_output=True, text=True, check=True)
        print(res.stdout)
        print("\x1b[1;32m[SUCCESS]\x1b[0m Dashboard HTML y Markdown actualizados.")
    except subprocess.CalledProcessError as e:
        print(f"\x1b[1;31m[ERROR]\x1b[0m Error durante la indexación:\n{e.stderr}")

def get_chronological_transcripts() -> list[tuple[Path, datetime]]:
    """Devuelve los paths de los transcripts ordenados de más nuevo a más antiguo."""
    transcripts = []
    for transcript_file in BRAIN_DIR.glob("*/.system_generated/logs/transcript.jsonl"):
        try:
            stat = transcript_file.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            transcripts.append((transcript_file, mod_time))
        except Exception:
            continue
    # Ordenar por tiempo de modificación descendente (más recientes primero)
    transcripts.sort(key=lambda x: x[1], reverse=True)
    return transcripts

def print_conversation_details(conv_id: str) -> None:
    """Muestra el diálogo completo de una conversación de forma brutalista."""
    conv_dir = BRAIN_DIR / conv_id
    transcript_file = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
    if not transcript_file.exists():
        # Intentar buscar por prefijo
        matching_dirs = list(BRAIN_DIR.glob(f"{conv_id}*"))
        if matching_dirs and matching_dirs[0].is_dir():
            transcript_file = matching_dirs[0] / ".system_generated" / "logs" / "transcript.jsonl"
            conv_id = matching_dirs[0].name
        else:
            print(f"\x1b[1;31m[ERROR]\x1b[0m Conversación no encontrada: {conv_id}")
            return
            
    print(f"\n\x1b[1;34m[DETAILS]\x1b[0m Desplegando conversación completa: {conv_id}")
    print("=" * 100)
    
    with open(transcript_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                step = json.loads(line)
                step_type = step.get("type", "UNKNOWN")
                source = step.get("source", "SYSTEM")
                content = step.get("content", "").strip()
                
                # Ignorar logs de herramientas de bajo nivel a menos que tengan contenido útil
                if step_type == "USER_INPUT":
                    print(f"\n\x1b[1;32m[USER]\x1b[0m:")
                    print(content)
                elif step_type == "PLANNER_RESPONSE" or source == "MODEL":
                    # Limpiar etiquetas
                    clean_content = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "")
                    print(f"\n\x1b[1;35m[AGENT]\x1b[0m:")
                    print(clean_content[:1500] + ("..." if len(clean_content) > 1500 else ""))
            except Exception:
                continue
    print("\n" + "=" * 100)

def search_nexus(query: str | None, limit: int) -> None:
    transcripts = get_chronological_transcripts()
    
    if not query:
        # Modo lista: Muestra las últimas conversaciones
        print(f"\x1b[1;34m[NEXUS LIST]\x1b[0m Listando últimas {limit} conversaciones...")
        print("-" * 100)
        count = 0
        for transcript_file, mod_time in transcripts:
            conv_id = transcript_file.parts[-4]
            time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
            # Buscar el primer prompt del usuario
            first_intent = "UNKNOWN_INTENT"
            try:
                with open(transcript_file, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        if data.get("type") == "USER_INPUT":
                            content = data.get("content", "")
                            first_intent = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "").strip().split("\n")[0][:80]
                            break
            except Exception:
                pass
            count += 1
            print(f"[{count:03d}] {time_str} | ID: \x1b[1;33m{conv_id[:8]}\x1b[0m... | {first_intent}")
            if count >= limit:
                break
        return

    # Modo búsqueda
    print(f"\x1b[1;34m[NEXUS QUERY]\x1b[0m Entropía objetivo: '{query}' (Límite: {limit})")
    print("-" * 100)
    
    matches_count = 0
    
    for transcript_file, mod_time in transcripts:
        conv_id = transcript_file.parts[-4]
        time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
        conv_matches = []
        
        try:
            with open(transcript_file, "r", encoding="utf-8") as f:
                for line in f:
                    if query.lower() in line.lower():
                        data = json.loads(line)
                        content = data.get("content", "")
                        if content and query.lower() in str(content).lower():
                            snippet = str(content)
                            idx = snippet.lower().find(query.lower())
                            start = max(0, idx - 60)
                            end = min(len(snippet), idx + 100)
                            
                            # Formatear snippet resaltando la keyword
                            raw_snippet = snippet[start:end].replace("\n", " ").strip()
                            highlighted = raw_snippet.replace(query, f"\x1b[1;31m{query}\x1b[0m").replace(query.lower(), f"\x1b[1;31m{query.lower()}\x1b[0m").replace(query.upper(), f"\x1b[1;31m{query.upper()}\x1b[0m")
                            
                            source = data.get("source", "UNKNOWN")
                            conv_matches.append((source, highlighted))
            
            if conv_matches:
                matches_count += 1
                print(f"\n\x1b[1;32m[CONVERSATION MATCH {matches_count}]\x1b[0m ID: \x1b[1;33m{conv_id}\x1b[0m ({time_str})")
                for src, snip in conv_matches[:3]: # Límite de 3 snippets por conversación para evitar inundar la pantalla
                    print(f"  [{src}] ...{snip}...")
                if len(conv_matches) > 3:
                    print(f"  ... y {len(conv_matches) - 3} coincidencia(s) más en esta sesión.")
                
                if matches_count >= limit:
                    print(f"\n\x1b[1;33m[HALT]\x1b[0m Límite de {limit} conversaciones coincidentes alcanzado.")
                    break
        except Exception:
            continue

    if matches_count == 0:
        print(f"\n\x1b[1;31m[ANERGÍA]\x1b[0m La entropía '{query}' no existe en ningún bloque conversacional.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Nexus Conversation Bridge - C5-REAL")
    parser.add_argument("--query", help="Keyword a auditar en el historial infinito.")
    parser.add_argument("--limit", type=int, default=30, help="Límite de conversaciones a retornar.")
    parser.add_argument("--rebuild", action="store_true", help="Reconstruye el Dashboard HTML e índice Markdown.")
    parser.add_argument("--details", help="Muestra el contenido de la conversación con el ID especificado.")
    args = parser.parse_args()

    if args.rebuild:
        rebuild_dashboard()
        return

    if args.details:
        print_conversation_details(args.details)
        return

    if not BRAIN_DIR.exists():
        print(f"\x1b[1;31m[CRITICAL]\x1b[0m Directorio Brain inalcanzable: {BRAIN_DIR}")
        sys.exit(1)

    search_nexus(args.query, args.limit)

if __name__ == "__main__":
    main()
