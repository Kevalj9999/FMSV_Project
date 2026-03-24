from collections import defaultdict

def build_global_graph(local_graph, modules):
    global_graph = defaultdict(set)

    # -------- Step 1: Normalize input graph --------
    for signal, deps in local_graph.items():
        for d in deps:
            global_graph[signal].add(d)

    # -------- Step 2: Cross-module connections --------
    for mod_name, mod_data in modules.items():
        for inst in mod_data.get("instances", []):
            connections = inst.get("connections", {})

            # Connect all signals in same instance
            signals = list(connections.values())

            for i in range(len(signals)):
                for j in range(len(signals)):
                    if i != j:
                        src = signals[i]
                        tgt = signals[j]

                        if src and tgt:
                            global_graph[src].add(tgt)

    return dict(global_graph)