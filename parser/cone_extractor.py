def score_signal(signal):
    score = 0

    # High importance signals
    if any(x in signal for x in ["full", "empty", "valid", "ready"]):
        score += 3

    if any(x in signal for x in ["count", "ptr", "state"]):
        score += 2

    # Penalize noise
    if "clk" in signal:
        score -= 2
    if "reset" in signal:
        score -= 1   # less penalty

    return score


def rank_deps(deps):
    def score(s):
        score = 0
        if "count" in s: score += 3
        if "ptr" in s: score += 2
        if "data" in s: score += 2
        if "en" in s: score += 1
        return score

    return sorted(deps, key=score, reverse=True)


def extract_smart_cone(graph, target, max_depth=5, max_paths=50):
    paths = []

    def dfs(node, path, depth):
        # Stop conditions
        if depth > max_depth:
            return

        if len(paths) >= max_paths:
            return

        # # 🔍 DEBUG START
        # if node not in graph:
        #     print(f"[WARNING] Node not in graph: {node}")

        deps = graph.get(node, [])

        # print(f"\n[DEBUG] Visiting: {node}")
        # print(f"[DEBUG] Dependencies: {deps}")
        # print(f"[DEBUG] Path: {path}")
        # 🔍 DEBUG END

        paths.append(path.copy())

        # 🔥 Ranked + limited branching
        ranked = rank_deps(deps)

        for dep in ranked[:4]:
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

    # -------- Sort cone --------
    cone = sorted(cone, key=lambda x: -score_signal(x))

    return {
        "target": target,
        "paths": paths[:max_paths],
        "cone": cone
    }