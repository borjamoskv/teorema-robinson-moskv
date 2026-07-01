import os
import glob
import yaml
import re

ONTOLOGY_DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/agents/ontology"
ARTIFACT_PATH = "$CORTEX_ROOT/.gemini/antigravity/brain/5e16ae97-2190-4550-90e2-3dd8495c4339/redundancias_convergencias.md"

def extract_entities():
    entities = []
    
    prim1000_path = os.path.join(ONTOLOGY_DIR, "06_MATRIZ_1000.yaml")
    with open(prim1000_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        for t_key, t_val in data.items():
            if not isinstance(t_val, dict): continue
            for d_key, d_list in t_val.get("dimensions", {}).items():
                for prim in d_list:
                    entities.append({"id": f"{t_key}:{prim}", "text": f"{t_key} {d_key} {prim}", "source": "MATRIZ_1000"})
    
    for yf in glob.glob(os.path.join(ONTOLOGY_DIR, "*.yaml")):
        basename = os.path.basename(yf)
        if basename == "CATALOGO_ENTIDADES_CORTEX.yaml":
            with open(yf, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                for cat, items in data.items():
                    for item in items:
                        entities.append({"id": item.get("id",""), "text": item.get("name",""), "source": basename})
        elif basename.startswith("0") and basename.endswith(".yaml"):
            with open(yf, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                for item in data.get("entities", []):
                    text = " ".join(str(v) for v in item.values())
                    item_id = item.get("id", text[:10])
                    entities.append({"id": item_id, "text": text, "source": basename})
    
    return entities

def tokenize(text):
    words = re.findall(r'\b\w+\b', str(text).lower())
    stop_words = {'para', 'como', 'este', 'esta', 'pero', 'todo', 'nada', 'algo'}
    return set([w for w in words if len(w) > 3 and w not in stop_words])

def jaccard(set1, set2):
    if not set1 or not set2: return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def main():
    entities = extract_entities()
    print(f"[*] Extracting tokens from {len(entities)} entities...")
    
    for e in entities:
        e["tokens"] = tokenize(e["text"])
        
    convergences = []
    seen_pairs = set()
    
    for i in range(len(entities)):
        for j in range(i+1, len(entities)):
            e1 = entities[i]
            e2 = entities[j]
            if e1["id"] == e2["id"]: continue
            
            score = jaccard(e1["tokens"], e2["tokens"])
            if score >= 0.40:
                pair = tuple(sorted([e1["id"], e2["id"]]))
                if pair not in seen_pairs:
                    convergences.append((score, e1, e2))
                    seen_pairs.add(pair)
                
    convergences.sort(key=lambda x: x[0], reverse=True)
    
    os.makedirs(os.path.dirname(ARTIFACT_PATH), exist_ok=True)
    with open(ARTIFACT_PATH, "w", encoding='utf-8') as f:
        f.write("# 🌀 Convergencias y Redundancias Ontológicas\n\n")
        f.write("> [!CAUTION]\n")
        f.write("> **Directiva C5-REAL (Ω6)**: La redundancia de estado es pudrición de contexto. Se exponen los nodos con colisión topológica superior al 40%.\n\n")
        f.write("Estas entidades exhiben isomorfismo parcial y deben purgarse o fusionarse (Nexus Bridging).\n\n")
        f.write("| Score | Entidad A | Origen A | Entidad B | Origen B |\n")
        f.write("|---|---|---|---|---|\n")
        
        count = 0
        for score, e1, e2 in convergences:
            if count > 150: break
            f.write(f"| {score:.2f} | {e1['id']} | {e1['source']} | {e2['id']} | {e2['source']} |\n")
            count += 1
            
    print(f"[+] Análisis completo. Se encontraron {len(convergences)} convergencias. Artefacto generado en: {ARTIFACT_PATH}")

if __name__ == '__main__':
    main()
