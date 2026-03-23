def extract_cone(graph, target, max_depth=2):
    visited = set()
    stack = [(target, 0)]

    while stack:
        node, depth = stack.pop()

        if depth >= max_depth:
            continue

        for dep in graph.get(node, []):
            # ❌ Skip derived-like signals early
            if dep in ("full", "empty"):
                continue

            if dep not in visited:
                visited.add(dep)
                stack.append((dep, depth + 1))

    return visited