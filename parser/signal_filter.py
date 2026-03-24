import re


# ---------------- NORMALIZATION ----------------
def normalize_signal(name):
    return (
        name.lower()
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


# ---------------- VALIDATION ----------------
def is_valid_signal(name):
    if not name:
        return False

    name = name.strip()

    if "'" in name:
        return False

    if "(" in name or ")" in name:
        return False

    if "*" in name:
        return False

    # Reject long phrases
    if len(name.split()) > 1:
        return False

    # Reject generic words
    blacklist = [
        "input", "output", "module", "interface",
        "configuration", "state", "machine",
        "system", "clock", "reset", "data",
        "address", "control", "logic"
    ]

    if any(b in name for b in blacklist):
        return False

    # Must look like RTL signal
    if "_" not in name and len(name) > 5:
        return False

    # Must contain letters
    if not any(c.isalpha() for c in name):
        return False

    return True


def is_clean_signal(name):
    if not name:
        return False

    name = str(name)

    # ❌ remove pyverilog garbage
    if "pyverilog" in name:
        return False

    # ❌ remove logic expressions
    if any(x in name for x in ["(", ")", "|", "&", "~", "^"]):
        return False

    # ❌ remove constants
    if "'" in name:
        return False

    # ❌ remove very long tokens
    if len(name) > 40:
        return False

    return True


# ---------------- CLEAN KG ----------------
def clean_kg(kg):
    nodes = set()
    edges = []

    for edge in kg["edges"]:
        src = normalize_signal(edge["source"])
        tgt = normalize_signal(edge["target"])

        if not src or not tgt:
            continue

        if is_clean_signal(src) and is_clean_signal(tgt) and is_valid_signal(src) and is_valid_signal(tgt):
            nodes.add(src)
            nodes.add(tgt)

            edges.append({
                "source": src,
                "target": tgt,
                "relation": edge.get("relation", "")
            })

    return {
        "nodes": list(nodes),
        "edges": edges
    }


# ---------------- FILTER BY RTL ----------------
def filter_by_rtl(kg, rtl_signals):
    nodes = set()
    edges = []

    for edge in kg["edges"]:
        src = edge["source"]
        tgt = edge["target"]

        # ✅ relaxed match
        src_match = any(src in r or r in src for r in rtl_signals)
        tgt_match = any(tgt in r or r in tgt for r in rtl_signals)

        if src_match and tgt_match:
            nodes.add(src)
            nodes.add(tgt)

            edges.append({
                "source": src,
                "target": tgt,
                "relation": edge.get("relation", "")
            })

    return {
        "nodes": list(nodes),
        "edges": edges
    }

# ---------------- BASIC GRAPH BUILD ----------------
def build_graph_from_kg(kg):
    graph = {}

    for edge in kg["edges"]:
        src = edge["source"]
        tgt = edge["target"]

        if tgt not in graph:
            graph[tgt] = []

        graph[tgt].append(src)

    return graph


# ---------------- SIMPLE RTL MATCHING ----------------
def map_to_rtl(signal, rtl_signals):
    for rtl in rtl_signals:
        if rtl.endswith("." + signal):
            return rtl
    return signal


# ---------------- MAIN MAPPING FUNCTION ----------------
def map_graph_to_rtl(graph, rtl_targets, modules):
    """
    Maps spec graph → RTL graph using:
    - direct matching
    - suffix matching
    - merging nodes
    """

    # Collect all RTL signals
    rtl_signals = set()

    for t in rtl_targets:
        rtl_signals.add(t)

        if "." in t:
            rtl_signals.add(t.split(".")[-1])

    mapped_graph = {}

    for node, deps in graph.items():

        # Map node
        mapped_node = map_to_rtl(node, rtl_signals)

        if mapped_node not in mapped_graph:
            mapped_graph[mapped_node] = set()

        # Map dependencies
        for d in deps:
            mapped_dep = map_to_rtl(d, rtl_signals)

            if mapped_dep:
                mapped_graph[mapped_node].add(mapped_dep)

    # Convert sets → list
    final_graph = {
        k: list(v)
        for k, v in mapped_graph.items()
    }

    return final_graph