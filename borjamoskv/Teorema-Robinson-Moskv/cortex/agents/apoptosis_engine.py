#!/usr/bin/env python3
# C5-REAL: Motor de Apoptosis AST (v1.0)
# Poda determinista de código muerto (Dead Code Pruner)
import ast
import os
import sys

class ApoptosisVisitor(ast.NodeVisitor):
    def __init__(self):
        self.defined = set()
        self.used = set()




        


def prune_file(filepath, dead_nodes):
    if not dead_nodes:
        return False
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
            
        tree = ast.parse(code)
    except:
        return False
        
    to_remove = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if node.name in dead_nodes:
                to_remove.append((node.lineno, node.end_lineno))
                
    if not to_remove:
        return False
        
    # Sort and remove from bottom to top
    to_remove.sort(key=lambda x: x[0], reverse=True)
    for start, end in to_remove:
        del lines[start-1:end]
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    return True

def run_apoptosis(target_dir):
    print(f"[*] Detonando Apoptosis Ontológica (AST-Pruner) en {target_dir}")
    total_files = 0
    pruned_files = 0
    
    # Gather global usage across all files first to prevent cross-file false positives
    global_used = set()
    global_defined = set()
    file_map = {}
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_files += 1
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    visitor = ApoptosisVisitor()
                    visitor.visit(tree)
                    global_used.update(visitor.used)
                    global_defined.update(visitor.defined)
                    file_map[filepath] = (visitor.defined, tree)
                except:
                    continue
                    
    # Only prune nodes that are NEVER used anywhere in the codebase
    dead_global = global_defined - global_used
    dead_global = {d for d in dead_global if not d.startswith('__') and d != 'main'}
    
    print(f"[*] Escaneo completado: {total_files} archivos. Nodos muertos globales identificados: {len(dead_global)}")
    
    if not dead_global:
        print("[+] Red neuronal limpia. Cero anergía.")
        return
        
    for filepath, (defined, tree) in file_map.items():
        local_dead = defined.intersection(dead_global)
        if prune_file(filepath, local_dead):
            print(f"[-] Purgado: {os.path.basename(filepath)} ({len(local_dead)} nodos eliminados)")
            pruned_files += 1
            
    print(f"[*] Apoptosis finalizada. Archivos mutados: {pruned_files}")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    run_apoptosis(target)
