import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os

queries = [
    'all:"structural isomorphism" AND all:"representation learning"',
    'all:"relational structure" AND all:"transfer" AND all:"domain"',
    'all:"category theory" AND all:"neural networks"',
    'all:"causal structure" AND all:"isomorphism"',
    'all:"structure-mapping" AND all:"deep learning"'
]

papers = []

for q in queries:
    url = f'http://export.arxiv.org/api/query?search_query={urllib.parse.quote(q)}&start=0&max_results=3'
    try:
        response = urllib.request.urlopen(url)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ')
            link = entry.find('{http://www.w3.org/2005/Atom}id').text.strip()
            
            papers.append({
                "Title": title,
                "URL": link,
                "Abstract": summary
            })
    except Exception as e:
        print(f"Error querying {q}: {e}")

# Deduplicate by URL
unique_papers = {p['URL']: p for p in papers}.values()

out_path = "$CORTEX_ROOT/30_BABYLON-60/scripts/scratch/arxiv_results.json"
with open(out_path, "w") as f:
    json.dump(list(unique_papers), f, indent=2)

print(f"C5-REAL_AUTODIDACT_SUCCESS: {len(unique_papers)} papers extraídos en {out_path}")
