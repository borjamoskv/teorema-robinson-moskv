#!/usr/bin/env python3
"""
C5-REAL Ingestor: CyberSecurity (SOTA Vector Engine)
Extrae feeds RSS de seguridad (HackerNews RSS / Zero Days).
"""
import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import sys
from datetime import datetime, timezone

# Utiliza HNRSS buscando keywords de seguridad
URLS = {
    "hn_sec": "https://hnrss.org/newest?q=security"
}
MAX_RESULTS = 5
OUTPUT_DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/sota_arbitrage/raw_data"

def ensure_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def fetch_rss(url):
    print(f"[C5-REAL] Fetching RSS from {url}...")
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'MOSKV-1-SOTA-Engine')
    try:
        response = urllib.request.urlopen(req)
        data = response.read()
        return data
    except Exception as e:
        print(f"[ERROR] Fallo al extraer RSS: {e}")
        return None

def parse_and_save(xml_data, source_name):
    if not xml_data: return
    try:
        root = ET.fromstring(xml_data)
    except Exception as e:
        print(f"[ERROR] XML parser failed: {e}")
        return
        
    entries = []
    # Dependiendo de si es RSS 2.0
    channel = root.find('channel')
    if not channel: return
    
    for item in channel.findall('item')[:MAX_RESULTS]:
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        description = item.find('description').text if item.find('description') is not None else ""
        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
        
        entries.append({
            "source": "cybersec_rss",
            "category": source_name,
            "title": title.strip().replace('\n', ' '),
            "summary": description.strip().replace('\n', ' '),
            "url": link,
            "published": pubDate,
            "ingested_at": datetime.now(timezone.utc).isoformat()
        })
        
    for entry in entries:
        safe_title = "".join([c for c in entry["title"] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = f"{OUTPUT_DIR}/cybersec_{source_name}_{safe_title[:30].replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(entry, f, indent=2)
            
    print(f"[OK] {len(entries)} items de {source_name} guardados en {OUTPUT_DIR}")

def main():
    ensure_dir()
    for name, url in URLS.items():
        xml_data = fetch_rss(url)
        parse_and_save(xml_data, name)

if __name__ == "__main__":
    main()
