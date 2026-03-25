import re


# ---------------- NORMALIZATION ----------------
def normalize_signal(name):
    return (
        str(name)
        .lower()
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


# ---------------- NOISE DEFINITIONS ----------------
NOISE_KEYWORDS = [
    "clk", "clock", "mclk", "aclk", "smclk",
    "reset", "rst",
]

BLACKLIST = [
    "input", "output", "module", "interface",
    "configuration", "state", "machine",
    "system", "logic",
    "behavior", "operation", "parameter",
    "design", "block", "function"
]


# ---------------- VALIDATION ----------------
def is_valid_signal(name):
    if not name:
        return False

    name = name.strip()

    # must match RTL-like identifier
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        return False

    # reject long phrases
    if len(name.split()) > 1:
        return False

    # reject blacklisted words
    if any(b in name for b in BLACKLIST):
        return False

    # must contain at least one letter
    if not any(c.isalpha() for c in name):
        return False

    return True


def is_clean_signal(name):
    if not name:
        return False

    name = str(name)

    # remove parser garbage
    if "pyverilog" in name:
        return False

    # remove expressions
    if any(x in name for x in ["(", ")", "|", "&", "~", "^", "="]):
        return False

    # remove constants
    if "'" in name:
        return False

    # too long = probably garbage
    if len(name) > 40:
        return False

    return True


def is_noise_signal(name):
    return any(n in name for n in NOISE_KEYWORDS)


# ---------------- CLEAN KG ----------------
def clean_kg(kg):
    nodes = set()
    edges = set()

    for edge in kg["edges"]:
        src = normalize_signal(edge["source"])
        tgt = normalize_signal(edge["target"])

        if src == tgt:
            continue

        if not src or not tgt:
            continue

        if not (is_clean_signal(src) and is_clean_signal(tgt)):
            continue

        if not (is_valid_signal(src) and is_valid_signal(tgt)):
            continue

        if "pmem" in src and "dmem" in tgt:
            continue

        # ❌ remove noise-only edges (like clk → everything)
        if is_noise_signal(src) and is_noise_signal(tgt):
            continue

        nodes.add(src)
        nodes.add(tgt)

        edges.add((src, tgt, edge.get("relation", "")))

    return {
        "nodes": list(nodes),
        "edges": [
            {"source": s, "target": t, "relation": r}
            for (s, t, r) in edges
        ]
    }


# ---------------- FILTER BY RTL ----------------
def filter_by_rtl(kg, rtl_signals):
    nodes = set()
    edges = set()

    rtl_signals = set(rtl_signals)

    def match(sig):
        # strict + suffix match
        return any(
            sig == r or
            r.endswith("." + sig) or
            sig.endswith("." + r)
            for r in rtl_signals
        )

    for edge in kg["edges"]:
        src = edge["source"]
        tgt = edge["target"]

        if match(src) and match(tgt):

            # ❌ remove clock-driven edges
            if is_noise_signal(src):
                continue

            nodes.add(src)
            nodes.add(tgt)

            edges.add((src, tgt, edge.get("relation", "")))

    return {
        "nodes": list(nodes),
        "edges": [
            {"source": s, "target": t, "relation": r}
            for (s, t, r) in edges
        ]
    }


# ---------------- GRAPH BUILD ----------------
def build_graph_from_kg(kg):
    graph = {}

    for edge in kg["edges"]:
        src = edge["source"]
        tgt = edge["target"]

        if tgt not in graph:
            graph[tgt] = set()

        graph[tgt].add(src)

    return {k: list(v) for k, v in graph.items()}


# ---------------- GRAPH CLEANING ----------------
def clean_graph_noise(graph):
    """
    Removes noisy dependencies like clocks
    """
    clean_graph = {}

    for node, deps in graph.items():
        filtered = [
            d for d in deps
            if not is_noise_signal(d)
        ]

        if filtered:
            clean_graph[node] = filtered

    return clean_graph


# ---------------- SIMPLE RTL MATCHING ----------------
def map_to_rtl(signal, rtl_signals):
    for rtl in rtl_signals:
        if rtl.endswith("." + signal):
            return rtl
    return signal


# ---------------- FINAL MAPPING ----------------
def map_graph_to_rtl(graph, rtl_targets, modules):
    rtl_signals = set()

    for t in rtl_targets:
        rtl_signals.add(t)

        if "." in t:
            rtl_signals.add(t.split(".")[-1])

    mapped_graph = {}

    for node, deps in graph.items():

        mapped_node = map_to_rtl(node, rtl_signals)

        if mapped_node not in mapped_graph:
            mapped_graph[mapped_node] = set()

        for d in deps:
            mapped_dep = map_to_rtl(d, rtl_signals)

            if mapped_dep:
                mapped_graph[mapped_node].add(mapped_dep)

    return {
        k: list(v)
        for k, v in mapped_graph.items()
    }