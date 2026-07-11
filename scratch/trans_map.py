TRANSITIONS = {
    "📢": ["🛡️", "📦"],
    "🛡️": ["✅", "⏳"],
    "✅": ["📤", "🧠"],
    "❌": ["🔄", "💀"],
    "📦": ["🧠", "🔒"],
    "🧠": ["⚡", "💀", "🩸", "⏳"],
    "⚡": ["📤", "✅", "📢"],
    "🩸": ["📦", "🔄"],
    "💀": ["🔄", "❌"],
    "🔒": ["🔓"],
    "🔓": ["🧠"],
    "⏳": ["🧠", "💀"],
    "🔄": ["👑", "⏳"],
    "👑": ["📢", "📦"],
    "📤": []
}
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

for node, children in TRANSITIONS.items():
    for child in children:
        reachable = get_reachable(TRANSITIONS, node, exclude_direct=child)
        if child in reachable:
            print(f"{node} -> {child}")
