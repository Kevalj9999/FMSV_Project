import os
from parser.rtl_parser import parse_rtl
from parser.dependency_extractor import build_dependency_graph
from parser.target_selector import extract_targets
from parser.cone_extractor import extract_cone
from parser.context_builder import build_context
from llm.generator import generate_assertions
from parser.signal_extractor import extract_signals
from utils.assertion_cleaner import clean_assertions
from parser.module_extractor import extract_modules
from parser.global_dependency import build_global_graph


# -------- FIX 3: Derived signal detection --------
def find_derived_signals(graph):
    derived = set()

    for target, deps in graph.items():
        filtered = [d for d in deps if d not in ("reset", "clk")]

        if len(filtered) == 1:
            parent = filtered[0]

            # ❗ Check if target is used back in parent
            if target not in graph.get(parent, []):
                derived.add(target)

    return derived


def remove_self_dependencies(graph):
    for node in graph:
        graph[node] = set(d for d in graph[node] if d != node)
    return graph


def get_rtl_files(folder):
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".v")
    ]


def load_rtl_code(rtl_files):
    code = ""
    for file in rtl_files:
        with open(file, "r") as f:
            code += f.read() + "\n"
    return code


def filter_targets(targets):
    filtered = []

    for t in targets:
        t_lower = t.lower()

        # ❌ Skip memory/internal signals
        if "mem" in t_lower or "memory" in t_lower:
            continue

        # ❌ Skip pure control signals
        if t_lower in ["wr_en", "rd_en"]:
            continue

        # ❌ Skip derived flags
        if t_lower in ["full", "empty"]:
            continue

        # ✅ Keep important verification signals
        if any(k in t_lower for k in ["ptr", "count", "data"]):
            filtered.append(t)

    return filtered


def is_control_target(t):
    keywords = ["ptr", "count", "state", "ctrl", "flag", "valid", "ready"]
    return any(k in t.lower() for k in keywords)


def main():
    rtl_folder = "rtl"
    spec_file = "spec/spec.txt"

    rtl_files = get_rtl_files(rtl_folder)
    print(f"Found {len(rtl_files)} RTL files")

    print("Parsing RTL files (incremental mode - memory efficient)...")
    ast = parse_rtl(rtl_files, incremental=True)

    print("Building dependency graph...")

    rtl_code = load_rtl_code(rtl_files)
    modules = extract_modules(rtl_code)

    # -------- LOCAL GRAPH --------
    local_graph = build_dependency_graph(ast)

    # -------- FIX 1 --------
    local_graph = remove_self_dependencies(local_graph)

    # -------- GLOBAL GRAPH --------
    graph = build_global_graph(local_graph, modules)

    # -------- CLEAN GLOBAL GRAPH --------
    graph = remove_self_dependencies(graph)

    # -------- FIX 3: DERIVED SIGNALS --------
    derived_signals = find_derived_signals(local_graph)

    print("\n--- Derived Signals ---\n")
    print(sorted(derived_signals))

    print("\n--- Dependency Graph (Sample) ---\n")
    for i, (target, deps) in enumerate(graph.items()):
        print(f"{target} ← {list(deps)}")
        if i >= 20:
            break

    # -------- TARGET EXTRACTION --------
    raw_targets = extract_targets(ast)
    targets = filter_targets(raw_targets)

    print("\n--- Targets ---\n")
    for t in targets:
        print(t)

    # -------- CONE EXTRACTION --------
    print("\n--- Register Cones ---\n")
    cones = {}

    for target in targets:
        cone = extract_cone(graph, target, max_depth=2)

        # -------- FIX 3 APPLY --------
        cone = [s for s in cone if s not in derived_signals]

        cones[target] = cone

        print(f"\nTarget: {target}")
        print("Cone:", list(cone))
        print("Cone size:", len(cone))

    # -------- CONTEXT EXTRACTION --------
    print("\n--- Context Extraction ---\n")
    contexts = {}

    for target in targets:
        context = build_context(rtl_code, cones[target], target)
        contexts[target] = context

        print(f"\nTarget: {target}")
        print("Context:\n", context)

    # -------- LOAD SPEC --------
    with open(spec_file, "r") as f:
        spec = f.read()

    # (assertion generation still commented)
    # print("\n--- FINAL ASSERTIONS (PER TARGET) ---\n")

    # for target in targets:
    #     context = contexts.get(target, "").strip()

    #     if not context:
    #         continue

    #     print(f"\n===== TARGET: {target} =====\n")

    #     # Extract signals ONLY for this context
    #     signals = extract_signals(context)

    #     print("--- Signals ---")
    #     print(signals)

    #     # Generate assertions for this target
    #     raw_assertions = generate_assertions(context, spec, signals,target)
    #     cleaned_assertions = clean_assertions(raw_assertions)

    #     print("\n--- Assertions ---\n")
    #     print(cleaned_assertions)

if __name__ == "__main__":
    main()