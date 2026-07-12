import json
DAG = {'📢': ['📦', '🛡️', '💀'], '📦': ['🧠', '🛡️', '💀'], '🧠': ['⚡', '💀', '🩸', '⏳'], '⚡': ['📤', '✅', '🔒'], '💀': ['🩸', '🔄', '❌'], '🩸': ['🧠'], '🛡️': ['✅', '💀'], '✅': ['🔒', '📤'], '🔒': ['📤'], '🔄': ['👑'], '👑': ['📢'], '⏳': ['🧠', '💀'], '❌': ['🔄', '💀'], '📤': []}

def get_reachable(graph, start, exclude_direct=None):
    visited = set()
    queue = []
    for child in graph.get(start, []):
        if exclude_direct and child == exclude_direct:
            continue
        queue.append(child)
        visited.add(child)
    while queue:
        node = queue.pop(0)
        for child in graph.get(node, []):
            if child not in visited:
                visited.add(child)
                queue.append(child)
    return visited
reduced_dag = {}
for node, children in DAG.items():
    reduced_children = []
    for child in children:
        reachable = get_reachable(DAG, node, exclude_direct=child)
        if child not in reachable:
            reduced_children.append(child)
    reduced_dag[node] = reduced_children
print('Reduced DAG:')
for k, v in reduced_dag.items():
    print(f'    "{k}": {json.dumps(v, ensure_ascii=False)},')
