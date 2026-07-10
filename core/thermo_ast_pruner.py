import ast
import os
import signal
from typing import List

class AnergiaPurger(ast.NodeTransformer):
    """
    Transductor Termodinámico. 
    Convierte la Anergía (prosa, manejo elástico de errores) en Exergía (Fail-Fast).
    """
    
    def visit_Expr(self, node: ast.Expr) -> ast.AST:
        # Purge docstrings and standalone string literals (Anergia)
        if isinstance(node.value, (ast.Constant, ast.Str)):
            return None 
        return self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> ast.AST:
        # Desconfianza Bizantina: Rechazo de try/except Exception (Green Theater)
        for i, handler in enumerate(node.handlers):
            if handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id == 'Exception'):
                # Reemplazar el bloque de contención con un colapso inmediato (SIGKILL)
                kill_node = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id='os', ctx=ast.Load()),
                            attr='kill',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Call(func=ast.Attribute(value=ast.Name(id='os', ctx=ast.Load()), attr='getpid', ctx=ast.Load()), args=[], keywords=[]),
                            ast.Attribute(value=ast.Name(id='signal', ctx=ast.Load()), attr='SIGKILL', ctx=ast.Load())
                        ],
                        keywords=[]
                    )
                )
                node.handlers[i].body = [kill_node]
                
        return self.generic_visit(node)

def transmute_file(filepath: str) -> None:
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())
    
    purger = AnergiaPurger()
    mutated_tree = purger.visit(tree)
    ast.fix_missing_locations(mutated_tree)
    
    # Sobrescritura física (Mutación en disco)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(ast.unparse(mutated_tree))
