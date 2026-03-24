import os
from concurrent.futures import ThreadPoolExecutor
import re

from parser.rtl_parser import parse_rtl
from parser.cone_extractor import extract_smart_cone
from parser.context_builder import build_context
from parser.signal_extractor import extract_signals
from parser.module_extractor import extract_modules
from parser.instance_extractor import extract_instances
from parser.signal_mapper import map_graph_to_rtl
from parser.global_dependency import build_global_graph
from parser.dependency_extractor import merge_with_instances
from parser.signal_filter import clean_kg, filter_by_rtl
from llm.generator import generate_assertions
from utils.assertion_cleaner import clean_assertions


# -------- HELPERS --------

def get_rtl_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".v")]


def load_rtl_code(rtl_files):
    code = ""
    for file in rtl_files:
        with open(file, "r") as f:
            code += f.read() + "\n"
    return code


def normalize_signal(name):
    return name.lower().strip().replace(" ", "_")


# -------- MAIN --------

def main():
    rtl_folder = "rtl"
    spec_txt_path = "spec/spec.txt"

    # -------- STEP 1: LOAD SPEC --------
    print("\nLoading spec...\n")

    with open(spec_txt_path, "r", encoding="utf-8") as f:
        spec_text = f.read()

    spec_text = re.sub(r'\n+', '\n', spec_text)
    spec_text = re.sub(r'\s+', ' ', spec_text)

    # -------- STEP 2: RTL --------
    rtl_files = get_rtl_files(rtl_folder)
    print(f"Found {len(rtl_files)} RTL files")

    ast = parse_rtl(rtl_files, incremental=True)
    rtl_code = load_rtl_code(rtl_files)

    # -------- STEP 3: RTL SIGNALS --------
    try:
        rtl_signals = set(normalize_signal(s) for s in extract_signals(ast))
    except:
        from parser.fallback_extractor import extract_signals_fallback
        rtl_signals = extract_signals_fallback(rtl_code)

    print(f"Total RTL signals: {len(rtl_signals)}")

    # -------- STEP 4: SPEC KG --------
    from parser.spec_kg_builder import build_spec_kg, kg_to_graph, clean_graph

    kg = build_spec_kg(spec_text)
    kg = clean_kg(kg)
    kg = filter_by_rtl(kg, rtl_signals)

    graph = clean_graph(kg_to_graph(kg))

    # -------- STEP 5: TARGETS --------
    def extract_targets(kg):
        return [
            n for n in kg["nodes"]
            if any(k in n for k in ["en", "addr", "data", "count", "ptr"])
            and any(n in r for r in rtl_signals)
        ]

    targets = extract_targets(kg)

    def score(t):
        return (
            5 * ("count" in t) +
            4 * ("ptr" in t) +
            3 * ("data" in t) +
            2 * ("addr" in t) +
            1 * ("en" in t)
        )

    targets = sorted(targets, key=score, reverse=True)[:15]

    print(f"\nSelected {len(targets)} targets\n")

    # -------- STEP 6: MAPPING --------
    modules = extract_modules(rtl_code)
    instances = extract_instances(ast)

    base_graph = map_graph_to_rtl(graph, targets, modules)

    # 🔥 strip hierarchy (CRITICAL FIX)
    def strip(signal):
        return signal.split(".")[-1]

    graph = {}
    for k, deps in base_graph.items():
        graph[strip(k)] = set(strip(d) for d in deps)

    graph = build_global_graph(graph, modules)

    # -------- STEP 7: CONES --------
    cones = {}
    paths = {}

    for t in targets:
        base = strip(t)
        result = extract_smart_cone(graph, base)
        cones[t] = result["cone"]
        paths[t] = result["paths"]

    # -------- STEP 8: CONTEXT --------
    contexts = {}

    for t in targets:
        context = build_context(
            rtl_code,
            cones.get(t, []),
            t,
            paths.get(t, [])
        )
        contexts[t] = context

    print("\n--- CONTEXT DEBUG ---")

    for t in targets[:3]:  # print only first 3 targets to avoid spam
        print(f"\nTarget: {t}\n")
        print(contexts[t][:500])

    # -------- STEP 9: ASSERTIONS → FILE --------
    os.makedirs("output", exist_ok=True)
    output_file = "output/assertions.sv"

    with open(output_file, "w") as f:

        for t in targets:
            context = contexts.get(t, "").strip()
            if not context:
                continue

            raw = generate_assertions(
                context,
                graph,
                paths.get(t, []),
                t
            )

            cleaned = clean_assertions(raw)

            f.write(f"\n// ===== TARGET: {t} =====\n\n")
            f.write(cleaned + "\n")

    print(f"\n✅ Assertions saved to: {output_file}\n")


if __name__ == "__main__":
    main()