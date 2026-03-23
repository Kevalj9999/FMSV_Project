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


def extract_smart_cone(graph, target, max_depth=5, max_paths=25):
    paths = []

    def dfs(node, path, depth):
        if depth > max_depth or len(paths) >= max_paths:
            return

        path.append(node)

        if node not in graph or len(graph[node]) == 0:
            paths.append(path.copy())
        else:
            # Sort dependencies by importance
            deps = sorted(
                graph[node],
                key=lambda x: -score_signal(x)
            )

            # Limit branching (VERY IMPORTANT)
            for dep in deps[:5]:
                if dep not in path:  # avoid cycles
                    dfs(dep, path, depth + 1)

        path.pop()

    dfs(target, [], 0)

    # Build cone from paths
    cone = set()
    for p in paths:
        cone.update(p)

    # Remove noise
    cone = {
        s for s in cone
        if '.' in s and not s.endswith(("clk", "reset"))
    }

    return {
        "target": target,
        "paths": paths,
        "cone": list(cone)
    }