
def resolve_signal(sig, signal_map, instance_map):

        # already qualified
        if "." in sig:
            return sig

        # first try instance mapping
        for parent_sig, child_sig in instance_map.items():
            if sig in parent_sig:
                return child_sig

        # fallback: module-level mapping
        if sig in signal_map:
            module = signal_map[sig][0]
            return f"{module}.{sig}"

        return sig

def build_signal_to_module_map(modules):
    signal_map = {}

    for module_name, data in modules.items():
        body = data["body"]

        # extract signals from module body
        import re
        signals = re.findall(r'\b(input|output|reg|wire)\s+(?:\[\d+:\d+\]\s+)?(\w+)', body)

        for _, sig in signals:
            if sig not in signal_map:
                signal_map[sig] = []
            signal_map[sig].append(module_name)

    return signal_map

def build_instance_signal_map(modules):
    instance_map = {}

    for parent_module, data in modules.items():
        for inst in data["instances"]:
            child_module = inst["module"]
            connections = inst["connections"]

            for port, signal in connections.items():
                # map parent signal → child signal
                parent_sig = f"{parent_module}.{signal}"
                child_sig = f"{child_module}.{port}"

                instance_map[parent_sig] = child_sig

    return instance_map


def map_graph_to_rtl(graph, rtl_targets, modules):

    signal_map = build_signal_to_module_map(modules)
    instance_map = build_instance_signal_map(modules)

    # 🔥 Extract all RTL signals from targets
    rtl_signals = set()
    for t in rtl_targets:
        rtl_signals.add(t)
        # also extract base signal
        if "." in t:
            rtl_signals.add(t.split(".")[-1])

    mapped_graph = {}

    for target, deps in graph.items():

        # Step 1: try intelligent resolution
        mapped_target = resolve_signal(target, signal_map, instance_map)

        # Step 2: force match with RTL (IMPORTANT)
        mapped_target = map_to_rtl(mapped_target.split(".")[-1], rtl_signals)

        mapped_deps = []

        for d in deps:
            resolved = resolve_signal(d, signal_map, instance_map)
            resolved = map_to_rtl(resolved.split(".")[-1], rtl_signals)
            mapped_deps.append(resolved)

        mapped_graph[mapped_target] = mapped_deps

    # 🔥 Merge nodes that map to same RTL signal
    final_graph = {}

    for node, deps in mapped_graph.items():
        if node not in final_graph:
            final_graph[node] = set()

        for d in deps:
            final_graph[node].add(d)

    # convert sets → list
    final_graph = {k: list(v) for k, v in final_graph.items()}

    return final_graph

def map_to_rtl(signal, rtl_signals):
    for rtl in rtl_signals:
        if rtl.endswith("." + signal):
            return rtl
    return signal

def align_spec_to_rtl(graph, rtl_targets):
    aligned_graph = {}

    for node, deps in graph.items():

        mapped_node = node

        # 🔥 match suffix
        for t in rtl_targets:
            if t.endswith("." + node):
                mapped_node = t
                break

        if mapped_node not in aligned_graph:
            aligned_graph[mapped_node] = set()

        for d in deps:
            mapped_dep = d

            for t in rtl_targets:
                if t.endswith("." + d):
                    mapped_dep = t
                    break

            aligned_graph[mapped_node].add(mapped_dep)

    return {k: list(v) for k, v in aligned_graph.items()}