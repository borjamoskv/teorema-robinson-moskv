#!/usr/bin/env python3
# C5-REAL: Macrófago Ontológico Ouroboros (v2.0)
# Erradicación Autónoma de Context Rot mediante Jaccard N-Grams y Generación de AST Patch.
# Zero dependencies (Pura Exergía).

import os
import re
import sys

def tokenize_ngrams(text, n=2):
    text = text.lower()
    text = re.sub(r'[^a-z0-9áéíóúñü]', ' ', text)
    tokens = text.split()
    stopwords = {'el','la','los','las','un','una','unos','unas','y','e','o','u','de','del','a','en','que','para','por','con','sin','sobre','como','es','son','o','no','si','se','su','sus','al','lo'}
    tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
    if len(tokens) < n:
        return set(tokens)
    return set(["_".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)])

def get_jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def parse_markdown_tables(filepath):
    entities = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_table = False
    headers = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('|') and not stripped.startswith('|-'):
            parts = [p.strip() for p in stripped.split('|')[1:-1]]
            if not in_table:
                if len(parts) > 0 and 'ID' in parts[0].upper():
                    headers = parts
                    in_table = True
            else:
                if len(parts) == len(headers):
                    entity = dict(zip(headers, parts))
                    if 'ID' in entity and entity['ID'].startswith(('ANTI-', 'INV-', 'PRIM-', 'VEC-', 'RED-')):
                        entities.append({
                            'id': entity['ID'],
                            'file': os.path.basename(filepath),
                            'content': " ".join(parts[1:])
                        })
        elif stripped.startswith('|-'):
            continue
        else:
            in_table = False
            
    return entities

def main(directory):
    print("[*] Iniciando Macrófago Ontológico Ouroboros v2.0...")
    all_entities = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.md'):
                filepath = os.path.join(root, f)
                entities = parse_markdown_tables(filepath)
                all_entities.extend(entities)
                
    print(f"[*] Ingestadas {len(all_entities)} entidades ontológicas.")
    
    ngrams_map = {}
    for ent in all_entities:
        bg = tokenize_ngrams(ent['content'], 2)
        tg = tokenize_ngrams(ent['content'], 3)
        ngrams_map[ent['id']] = bg.union(tg)
        
    redundancies = []
    threshold = 0.08 # Jaccard en 2-grams y 3-grams es bajo empíricamente
    
    for i in range(len(all_entities)):
        for j in range(i+1, len(all_entities)):
            ent1 = all_entities[i]
            ent2 = all_entities[j]
            
            sim = get_jaccard_similarity(ngrams_map[ent1['id']], ngrams_map[ent2['id']])
            
            if sim >= threshold:
                cat1 = ent1['id'].split('-')[0]
                cat2 = ent2['id'].split('-')[0]
                is_symbiotic = cat1 != cat2
                
                redundancies.append({
                    'score': round(sim, 3),
                    'node_A': ent1['id'],
                    'node_B': ent2['id'],
                    'file_A': ent1['file'],
                    'file_B': ent2['file'],
                    'symbiotic': is_symbiotic
                })
                
    redundancies.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\\n[!] Detectadas {len(redundancies)} fracturas N-Gram (Similitud >= {threshold}).\\n")
    
    patch_lines = ["#!/bin/bash", "# C5-REAL Auto-generated Apoptosis Patch"]
    
    for r in redundancies:
        sym_flag = "[SIMBIÓTICO]" if r['symbiotic'] else "[REDUNDANTE]"
        print(f"[{r['score']}] {sym_flag} {r['node_A']} ({r['file_A']}) <---> {r['node_B']} ({r['file_B']})")
        if not r['symbiotic']:
            filepath = os.path.join(directory, r['file_B'])
            patch_lines.append(f"sed -i '' '/| {r['node_B']} |/d' {filepath}")
            
    if not redundancies:
        print("[+] Red neuronal limpia. Cero Context Rot.")
        
    yaml_out = os.path.join(directory, "apoptosis_target.yaml")
    with open(yaml_out, 'w', encoding='utf-8') as f:
        f.write("Claim: Redundancias Estructurales Detectadas\\n")
        f.write("Proof: { Base: N-Gram Jaccard Index, Confidence: C5-REAL }\\n")
        f.write("Fractures:\\n")
        for r in redundancies:
            f.write(f"  - nodes: [{r['node_A']}, {r['node_B']}]\\n")
            f.write(f"    score: {r['score']}\\n")
            f.write(f"    files: [{r['file_A']}, {r['file_B']}]\\n")
            f.write(f"    symbiotic: {r['symbiotic']}\\n")
            
    patch_out = os.path.join(directory, "apoptosis_patch.sh")
    with open(patch_out, 'w', encoding='utf-8') as f:
        f.write("\\n".join(patch_lines) + "\\n")
        
    os.chmod(patch_out, 0o755)
            
    print(f"\\n[*] Reporte cristalizado en {yaml_out}.")
    print(f"[*] Mutador Bash generado en {patch_out}. Ejecutar para purgar AST automáticamente.")

if __name__ == '__main__':
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    main(target_dir)
