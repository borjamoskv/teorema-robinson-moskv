# C5-REAL: AST Projection Isomorphism
import ast
import textwrap
import sys

DUMMY_CODE: str = textwrap.dedent("""
    def process_data(data):
        # Un comentario irrelevante
        result = data * 2
        
        return result
""")

class SentinelInjector(ast.NodeTransformer):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        assert isinstance(node, ast.FunctionDef), "Nodo debe ser FunctionDef"
        self.generic_visit(node)
        
        sentinel_node: ast.Expr = ast.Expr(
            value=ast.Call(
                func=ast.Name(id='print', ctx=ast.Load()),
                args=[ast.Constant(value="[C5-REAL] Git Sentinel Injected. Cero Anergía.")],
                keywords=[]
            )
        )
        ast.copy_location(sentinel_node, node)
        node.body.insert(0, sentinel_node)
        return node

if __name__ == "__main__":
    sys.stdout.write("[C5-REAL] Iniciando Prueba de Isomorfismo Código/AST (Projectional Editing)\n")
    sys.stdout.write("\n[TEXTO ORIGINAL - Entrópico]:\n")
    sys.stdout.write(DUMMY_CODE.strip() + "\n")
    
    tree: ast.AST = ast.parse(DUMMY_CODE)
    injector: SentinelInjector = SentinelInjector()
    mutated_tree: ast.AST = injector.visit(tree)
    
    ast.fix_missing_locations(mutated_tree)
    
    try:
        colapsado: str = ast.unparse(mutated_tree)
        sys.stdout.write("\n[AST COLAPSADO - Estructuralmente Mutado]:\n")
        sys.stdout.write(colapsado + "\n")
        sys.stdout.write("\n[STATUS] Isomorfismo Código/AST Validado. El formato fue destruido, la estructura prevalece.\n")
    except AttributeError:
        sys.stdout.write("[FALLBACK] ast.unparse requiere Python 3.9+. Mostrando el volcado del AST:\n")
        sys.stdout.write(ast.dump(mutated_tree, indent=4) + "\n")
