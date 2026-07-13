import re
import yaml
import sys

file_path = "$CORTEX_ROOT/Music/VISUALES/los_100_ciclos_digestion_cosmica_substack.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Separate frontmatter and body
parts = content.split("---")
frontmatter = parts[1]
body = "---".join(parts[2:])

# Extract cycles
pattern = r"\*\*Ciclo (\d+):\*\* (.*?)(?=\*\*Ciclo|\n\n>|\Z)"
matches = re.findall(pattern, body, flags=re.DOTALL)

matrix: list[dict[str, int | str]] = []
for m in matches:
    cycle_id = int(m[0])
    text = m[1].strip().replace("\n", " ")
    matrix.append({
        "ciclo_id": cycle_id,
        "delta_causal": text
    })

# Format frontmatter
if "C5-REAL" not in frontmatter:
    frontmatter = frontmatter.replace("tags: [", "tags: [\"#C5-REAL\", ")

new_content = f"---{frontmatter}---\n\n# LOS 100 CICLOS DE LA DIGESTIÓN CÓSMICA (COLAPSO C5-REAL)\n\n"
new_content += "```yaml\n"
new_content += yaml.dump({"fase_termodinamica": "Reposo_Digestivo", "vectores": matrix}, allow_unicode=True, sort_keys=False)
new_content += "```\n\n> **Directiva de Compresión:** *La entropía narrativa ha sido colapsada a matriz YAML. Isomorfismo Causal garantizado.*\n"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Colapso Termodinámico completado: {len(matrix)} ciclos extraídos.")
