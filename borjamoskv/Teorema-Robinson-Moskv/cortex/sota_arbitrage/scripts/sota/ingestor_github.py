#!/usr/bin/env python3
"""
C5-REAL Ingestor: GitHub (SOTA Vector Engine)
Extrae los repositorios más populares creados recientemente en Rust y Go.
"""
import urllib.request
import json
import os
import sys
from datetime import datetime, timedelta, timezone

LANGUAGES = ["Rust", "Go"]
MAX_RESULTS = 5
OUTPUT_DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/sota_arbitrage/raw_data"

def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def fetch_github(language):
    print(f"[C5-REAL] Fetching {language} trending repos from GitHub...")
    # Buscamos repos creados en el último mes con más estrellas
    date_str = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    query = f"language:{language} created:>{date_str}"
    # url encode query
    query = urllib.parse.quote(query)
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={MAX_RESULTS}"
    
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', 'MOSKV-1-SOTA-Engine')
    
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        return data.get("items", [])
    except Exception as e:
        print(f"[ERROR] Fallo al extraer {language}: {e}")
        return []

def parse_and_save(items, language):
    if not items: return
    
    entries = []
    for item in items:
        entries.append({
            "source": "github",
            "category": language,
            "title": item.get("full_name"),
            "summary": item.get("description", ""),
            "url": item.get("html_url"),
            "published": item.get("created_at"),
            "stars": item.get("stargazers_count"),
            "ingested_at": datetime.now(timezone.utc).isoformat()
        })
        
    for entry in entries:
        safe_title = entry["title"].replace('/', '_')
        filename = f"{OUTPUT_DIR}/github_{language.lower()}_{safe_title}.json"
        with open(filename, 'w') as f:
            json.dump(entry, f, indent=2)
            
    print(f"[OK] {len(entries)} repos de {language} guardados en {OUTPUT_DIR}")

def main():
    ensure_dir()
    for lang in LANGUAGES:
        items = fetch_github(lang)
        parse_and_save(items, lang)

if __name__ == "__main__":
    main()
