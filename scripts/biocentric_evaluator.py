import ast
import math
import os
import sys
from pathlib import Path

def calculate_shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    length = len(text)
    vocabulary = list(dict.fromkeys(list(text)))
    if len(vocabulary) <= 1:
        return 0.0
    probabilities = [float(text.count(c)) / length for c in vocabulary]
    return -sum((p * math.log(p, 2) for p in probabilities))

def evaluate_script(filepath: Path) -> dict:
    try:
        content = filepath.read_text(encoding='utf-8')
    except RuntimeError:
        return None
    pureza = 300
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == 'Exception'):
                    pureza -= 50
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and (node.func.id in ('eval', 'exec')):
                pureza -= 50
    except RuntimeError:
        pureza = 0
    pureza = max(0, pureza)
    entropy = calculate_shannon_entropy(content)
    density_score = int((entropy - 4.0) / 1.2 * 300)
    density_score = max(0, min(300, density_score))
    indep = 200
    if 'C5-REAL' in content:
        indep += 100
    if 'SYS_ID' in content:
        indep += 50
    if 'argparse' in content:
        indep += 50
    if 'sqlite3' in content:
        indep += 50
    if 'WAL' in content:
        indep += 50
    if 'input(' in content:
        indep -= 100
    indep = max(0, min(400, indep))
    total = pureza + density_score + indep
    return {'path': str(filepath), 'name': filepath.name, 'pureza': pureza, 'density': density_score, 'indep': indep, 'total': total, 'entropy': round(entropy, 3)}

def main():
    if len(sys.argv) < 3:
        print('Usage: biocentric_evaluator.py <output.md> <dir1> <dir2> ...')
        sys.exit(1)
    out_file = Path(sys.argv[1])
    target_dirs = [Path(d).resolve() for d in sys.argv[2:]]
    scripts = []
    for d in target_dirs:
        for root, _, files in os.walk(d):
            if '.venv' in root or 'node_modules' in root or '.git' in root:
                continue
            for f in files:
                if f.endswith('.py'):
                    scripts.append(Path(root) / f)
    results = []
    for s in scripts:
        res = evaluate_script(s)
        if res:
            results.append(res)
    results.sort(key=lambda x: x['total'], reverse=True)
    lines = ['# Ránking Biocéntrico C5-REAL (Métrica 1-1000)', '', '> LEY E3: Medición de apalancamiento del Operador: 1000/1000 = cero coste ATP humano.', '', '| Ranking | Script | Pureza AST (300) | Densidad (300) | Independencia (400) | Total / 1000 |', '|:---:|:---|:---:|:---:|:---:|:---:|']
    for idx, r in enumerate(results, 1):
        rel_path = r['path'].split('borjafernandezangulo/')[-1]
        lines.append(f"| {idx} | `{rel_path}` | {r['pureza']} | {r['density']} | {r['indep']} | **{r['total']}** |")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Evaluación completada. {len(results)} scripts procesados. Reporte: {out_file}')
if __name__ == '__main__':
    main()
