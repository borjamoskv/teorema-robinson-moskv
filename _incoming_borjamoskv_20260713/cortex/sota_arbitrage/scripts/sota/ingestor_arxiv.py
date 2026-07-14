#!/usr/bin/env python3
"""
C5-REAL Ingestor: ArXiv (SOTA Vector Engine)
Extrae los últimos papers de cs.AI, cs.CR y cs.DS.
"""
import urllib.request
import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime, timezone

CATEGORIES = ["cs.AI", "cs.CR", "cs.DS"]
MAX_RESULTS = 5
OUTPUT_DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/sota_arbitrage/raw_data"

def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def fetch_arxiv(category):
    print(f"[C5-REAL] Fetching {category} from ArXiv...")
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results={MAX_RESULTS}"
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        return data
    except Exception as e:
        print(f"[ERROR] Fallo al extraer {category}: {e}")
        return None

def parse_and_save(xml_data, category):
    if not xml_data: return
    root = ET.fromstring(xml_data)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    
    entries = []
    for entry in root.findall('atom:entry', namespace):
        title = entry.find('atom:title', namespace).text.strip().replace('\n', ' ')
        summary = entry.find('atom:summary', namespace).text.strip().replace('\n', ' ')
        link = entry.find('atom:id', namespace).text.strip()
        published = entry.find('atom:published', namespace).text.strip()
        
        entries.append({
            "source": "arxiv",
            "category": category,
            "title": title,
            "summary": summary,
            "url": link,
            "published": published,
            "ingested_at": datetime.now(timezone.utc).isoformat()
        })
        
    for entry in entries:
        safe_title = "".join([c for c in entry["title"] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = f"{OUTPUT_DIR}/arxiv_{category.replace('.','_')}_{safe_title[:30].replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(entry, f, indent=2)
            
    print(f"[OK] {len(entries)} papers de {category} guardados en {OUTPUT_DIR}")

def main():
    ensure_dir()
    for cat in CATEGORIES:
        xml_data = fetch_arxiv(cat)
        parse_and_save(xml_data, cat)

if __name__ == "__main__":
    main()
