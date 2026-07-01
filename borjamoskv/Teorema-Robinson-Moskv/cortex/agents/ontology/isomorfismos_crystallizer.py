import os
import json
import yaml

ONTOLOGY_DIR = "$CORTEX_ROOT/borjamoskv/Teorema-Robinson-Moskv/cortex/agents/ontology"

def parse_isomorfismos():
    md_file = os.path.join(ONTOLOGY_DIR, "07_ISOMORFISMOS_BIO_SILICIO.md")
    if not os.path.exists(md_file):
        return

    data = {}
    current_category = None

    with open(md_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("## ") or (line[0].isdigit() and ". " in line and not line.startswith("1. Cognición")):
                # Handle both "## 6. Termodinámica..." and "2. Sistema nervioso..."
                current_category = line.replace("## ", "").strip()
                data[current_category] = []
            elif line.startswith("|") and not line.startswith("|-"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) == 2:
                    if all(all(c in "- " for c in part) for part in parts):
                        continue
                    dom_a = parts[0].lower()
                    if dom_a not in ["humano", "biológico/social (humano)", "físico / mecánico (relevo 4x4)", "biológico/social humano"]:
                        if current_category:
                            data[current_category].append({
                                "domain_a": parts[0],
                                "domain_b": parts[1]
                            })

    json_file = os.path.join(ONTOLOGY_DIR, "07_ISOMORFISMOS_BIO_SILICIO.json")
    with open(json_file, "w", encoding="utf-8") as jf:
        json.dump(data, jf, indent=2, ensure_ascii=False)

    yaml_file = os.path.join(ONTOLOGY_DIR, "07_ISOMORFISMOS_BIO_SILICIO.yaml")
    with open(yaml_file, "w", encoding="utf-8") as yf:
        yaml.dump(data, yf, allow_unicode=True, sort_keys=False)

    total_mappings = sum(len(mappings) for mappings in data.values())
    print(f"[*] Cristalizado 07_ISOMORFISMOS_BIO_SILICIO.md -> JSON/YAML ({total_mappings} mappings extraídos)")

if __name__ == '__main__':
    print("[*] Iniciando cristalización de Isomorfismos a JSON/YAML...")
    parse_isomorfismos()
    print("[+] Colapso a JSON completado.")
