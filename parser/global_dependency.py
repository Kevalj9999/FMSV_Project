def build_global_graph(local_graph, modules):
    global_graph = dict(local_graph)

    # -------- Cross-module dependencies --------
    for mod_name, mod_data in modules.items():
        for inst in mod_data["instances"]:
            child_module = inst["module"]
            connections = inst["connections"]

            for port, signal in connections.items():
                # Assume connection means dependency
                if signal not in global_graph:
                    global_graph[signal] = set()

                # Connect across modules
                global_graph[signal].add(port)

    return global_graph