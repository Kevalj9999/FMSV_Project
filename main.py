import os
import pickle
from concurrent.futures import ThreadPoolExecutor

from parser.rtl_parser import parse_rtl
from parser.dependency_extractor import build_dependency_graph
from parser.target_selector import extract_targets
from parser.cone_extractor import extract_smart_cone
from parser.context_builder import build_context
from llm.generator import generate_assertions
from parser.signal_extractor import extract_signals
from utils.assertion_cleaner import clean_assertions
from parser.module_extractor import extract_modules
from parser.global_dependency import build_global_graph


# -------- DERIVED SIGNAL DETECTION --------
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

        if "mem" in t_lower or "memory" in t_lower:
            continue

        if t_lower in ["wr_en", "rd_en"]:
            continue

        if t_lower in ["full", "empty"]:
            continue

        if any(k in t_lower for k in ["ptr", "count", "data"]):
            filtered.append(t)

    return filtered


# -------- PARALLEL TARGET PROCESSING --------
def process_target(args):
    target, graph, derived_signals = args

    try:
        result = extract_smart_cone(graph, target)

        cone = result["cone"]
        paths = result["paths"]

        # Remove derived signals
        cone = [s for s in cone if s not in derived_signals]

        return target, cone, paths

    except Exception as e:
        print(f"❌ Error in {target}: {e}")
        return target, [], []


def main():
    rtl_folder = "rtl"
    spec_file = "spec/spec.txt"

    rtl_files = get_rtl_files(rtl_folder)
    print(f"Found {len(rtl_files)} RTL files")

    print("Parsing RTL files (incremental mode - memory efficient)...")
    ast = parse_rtl(rtl_files, incremental=True)

    rtl_code = load_rtl_code(rtl_files)
    modules = extract_modules(rtl_code)

    # -------- GRAPH (WITH CACHE) --------
    if os.path.exists("graph.pkl"):
        print("Loading cached graph...")
        graph = pickle.load(open("graph.pkl", "rb"))

        # ⚠️ Need local_graph for derived signals → rebuild minimal
        local_graph = build_dependency_graph(ast)
        local_graph = remove_self_dependencies(local_graph)

    else:
        print("Building graph from scratch...")

        local_graph = build_dependency_graph(ast)
        local_graph = remove_self_dependencies(local_graph)

        graph = build_global_graph(local_graph, modules)
        graph = remove_self_dependencies(graph)

        pickle.dump(graph, open("graph.pkl", "wb"))

    # -------- DERIVED SIGNALS --------
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

    # -------- CONE EXTRACTION (PARALLEL) --------
    print("\n--- Register Cones ---\n")

    cones = {}
    all_paths = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(
            process_target,
            [(t, graph, derived_signals) for t in targets]
        )

    for target, cone, paths in results:
        cones[target] = cone
        all_paths[target] = paths

        print(f"\nTarget: {target}")
        print("Cone:", cone)
        print("Cone size:", len(cone))

        print("Paths:")
        for p in paths[:3]:
            print(" -> ".join(p))

    # -------- CONTEXT EXTRACTION --------
    print("\n--- Context Extraction ---\n")

    contexts = {}

    for target in targets:
        try:
            cone = cones.get(target, [])
            paths = all_paths.get(target, [])

            context = build_context(rtl_code, cone, target, paths)
            contexts[target] = context

            print(f"\nTarget: {target}")
            print("Context:\n", context)

        except Exception as e:
            print(f"❌ Context error for {target}: {e}")

    # -------- LOAD SPEC --------
    with open(spec_file, "r") as f:
        spec = f.read()

    # -------- ASSERTION GENERATION --------
    print("\n--- FINAL ASSERTIONS (PER TARGET) ---\n")

    for target in targets:
        context = contexts.get(target, "").strip()

        if not context:
            continue

        print(f"\n===== TARGET: {target} =====\n")

        signals = extract_signals(context)

        print("--- Signals ---")
        print(signals)

        raw_assertions = generate_assertions(context, spec, signals, target)
        cleaned_assertions = clean_assertions(raw_assertions)

        print("\n--- Assertions ---\n")
        print(cleaned_assertions)


if __name__ == "__main__":
    main()