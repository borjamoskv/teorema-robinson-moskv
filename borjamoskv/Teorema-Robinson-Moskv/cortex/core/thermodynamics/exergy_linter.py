# exergy_linter.py | Reality Level: C5-REAL
import ast, os, sys, json

class ExergyVisitor(ast.NodeVisitor):
    def __init__(self): self.guards_count = 0
    def visit_Assert(self, node): self.guards_count += 1; self.generic_visit(node)
    def visit_AnnAssign(self, node): self.guards_count += 1; self.generic_visit(node)
    def visit_FunctionDef(self, node):
        if node.returns: self.guards_count += 1
        for arg in node.args.args:
            if arg.annotation: self.guards_count += 1
        self.generic_visit(node)

def analyze_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f: source = f.read()
    except Exception: return None

    lines = source.splitlines()
    total_lines = len(lines)
    if total_lines == 0: return None

    comments = sum(1 for line in lines if line.strip().startswith('#'))
    anergy_terms = ['TODO', 'FIXME', 'pass', 'placeholder', 'print(', 'sleep(']
    anergy_penalty = sum(1 for line in lines for term in anergy_terms if term in line)

    try:
        visitor = ExergyVisitor()
        visitor.visit(ast.parse(source))
        guards = visitor.guards_count
    except SyntaxError:
        guards = 0; anergy_penalty += 10 # Penalización masiva por código no compilable

    comment_ratio = comments / total_lines
    exergy_score = 1.0 - comment_ratio - (anergy_penalty / total_lines) + (guards / total_lines)
    
    return {
        "filename": os.path.basename(filepath),
        "exergy_score": round(max(0.0, min(1.0, exergy_score)), 4)
    }

if __name__ == '__main__':
    target_files = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.isdir(arg):
                for root, _, files in os.walk(arg):
                    for file in files:
                        if file.endswith('.py'):
                            target_files.append(os.path.join(root, file))
            elif os.path.isfile(arg) and arg.endswith('.py'):
                target_files.append(arg)
    else:
        # Por defecto, auditar el directorio actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(current_dir):
            if file.endswith('.py'):
                target_files.append(os.path.join(current_dir, file))

    results = []
    for filepath in target_files:
        res = analyze_file(filepath)
        if res:
            results.append(res)

    # Imprimir resultados en Markdown y JSON
    print(json.dumps(results, indent=2))

