def extract_cone(graph, target):
    visited = set()
    stack = [target]

    while stack:
        node = stack.pop()

        if node not in visited:
            visited.add(node)

            for dep in graph.get(node, []):
                if dep not in visited:
                    stack.append(dep)

    return visited