def map_graph_to_rtl(graph, rtl_targets):
    def qualify_signal(target, signal):
        # target = fifo.count → module = fifo
        if "." in target:
            module = target.split(".")[0]
            return f"{module}.{signal}"
        return signal
    
    mapped_graph = {}

    # Extract module prefix (assume same module for now)
    module = rtl_targets[0].split(".")[0] if rtl_targets else ""

    # Build mapping
    name_map = {}
    for t in rtl_targets:
        short = t.split(".")[-1]
        name_map[short] = t

    def map_signal(sig):
        if sig in name_map:
            return name_map[sig]
        # fallback: attach module prefix
        if module:
            return f"{module}.{sig}"
        return sig

    for target, deps in graph.items():
        mapped_target = map_signal(target)

        mapped_deps = []
        for d in deps:
            mapped_deps.append(qualify_signal(target, d))

        mapped_graph[mapped_target] = mapped_deps

    return mapped_graph