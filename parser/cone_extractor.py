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

        # 🔥 IMPORTANT: ranked + limited branching
        for dep in rank_deps(graph.get(node, []))[:6]:
            if dep not in path:  # avoid cycles per path
                dfs(dep, path + [dep], depth + 1)

    # Start DFS
    dfs(target, [target], 0)

    # -------- Build cone --------
    cone = set()
    for p in paths:
        cone.update(p)

    # -------- Remove noise --------
    cone = {
        s for s in cone
        if '.' in s and not s.endswith(("clk", "reset"))
    }

    # -------- Sort cone (important for consistency) --------
    cone = sorted(cone, key=lambda x: -score_signal(x))

    return {
        "target": target,
        "paths": paths[:max_paths],
        "cone": cone
    }