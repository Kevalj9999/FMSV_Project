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
from parser.signal_mapper import map_graph_to_rtl
from parser.global_dependency import build_global_graph
from parser.instance_extractor import extract_instances
from parser.port_mapper import build_port_map
from parser.dependency_extractor import merge_with_instances


# -------- DERIVED SIGNAL DETECTION --------
def find_derived_signals(graph):
    derived = set()

    for target, deps in graph.items():
        filtered = [d for d in deps if d not in ("reset", "clk")]

        if target in ["wr_en", "rd_en"]:
            continue

        if any(k in target.lower() for k in ["ptr", "data"]):
            continue

        if len(filtered) == 1:
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

    # -------- LOAD RTL FILES --------
    rtl_files = get_rtl_files(rtl_folder)
    print(f"Found {len(rtl_files)} RTL files")

    print("Parsing RTL files...")
    ast = parse_rtl(rtl_files, incremental=True)

    rtl_code = load_rtl_code(rtl_files)

    # -------- BUILD GRAPH FROM SPEC --------
    from parser.spec_kg_builder import build_spec_kg, kg_to_graph, clean_graph

    print("\nBuilding Knowledge Graph from Spec...\n")

    with open(spec_file, "r") as f:
        spec_text = f.read()

    kg = build_spec_kg(spec_text)

    print("\n--- KG ---\n")
    print(kg)

    graph = kg_to_graph(kg)
    graph = clean_graph(graph)

    print("\n--- Graph (Spec-based) ---\n")
    for k, v in graph.items():
        print(f"{k} ← {v}")

    # -------- TARGETS FROM RTL --------
    print("\n--- Targets (from RTL) ---\n")

    raw_targets = extract_targets(ast)
    targets = filter_targets(raw_targets)

    for t in targets:
        print(t)

    # -------- MAP GRAPH TO RTL --------
    graph = map_graph_to_rtl(graph, targets)
    instances = extract_instances(ast)
    graph = merge_with_instances(graph, instances)

    print("\n--- Graph (Mapped to RTL) ---\n")
    for k, v in graph.items():
        print(f"{k} ← {v}")

    # -------- DERIVED SIGNALS (EMPTY FOR NOW) --------
    derived_signals = set()

    # -------- CONE EXTRACTION --------
    print("\n--- Register Cones ---\n")

    cones = {}
    all_paths = {}

    for target in targets:
        try:
            result = extract_smart_cone(graph, target)

            cone = result["cone"]
            paths = result["paths"]

            cones[target] = cone
            all_paths[target] = paths

            print(f"\nTarget: {target}")
            print("Cone:", cone)
            print("Paths:")
            for p in paths[:3]:
                print(" -> ".join(p))

        except Exception as e:
            print(f"❌ Cone error for {target}: {e}")

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

    # -------- ASSERTION GENERATION --------
    print("\n--- FINAL ASSERTIONS ---\n")

    for target in targets:
        context = contexts.get(target, "").strip()

        if not context:
            continue

        print(f"\n===== TARGET: {target} =====\n")

        signals = extract_signals(context)

        raw_assertions = generate_assertions(
            context,
            graph,
            all_paths.get(target, []),
            target
        )

        print("\n--- RawAssertions ---\n")
        print(raw_assertions)

        # cleaned_assertions = clean_assertions(raw_assertions)

        # print("\n--- Cleaned Assertions ---\n")
        # print(cleaned_assertions)

if __name__ == "__main__":
    main()