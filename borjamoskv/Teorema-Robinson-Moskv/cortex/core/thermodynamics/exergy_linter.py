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
