import os
import re

from parser.rtl_parser import parse_rtl
from parser.cone_extractor import extract_smart_cone
from parser.context_builder import build_context
from parser.signal_extractor import extract_signals
from parser.module_extractor import extract_modules
from parser.instance_extractor import extract_instances
from parser.signal_mapper import map_graph_to_rtl
from parser.global_dependency import build_global_graph
from parser.signal_filter import clean_kg, filter_by_rtl
from llm.generator import generate_assertions
from utils.assertion_cleaner import clean_assertions,remove_invalid_assertions,remove_weak_assertions


# -------- HELPERS --------

import ast

def load_kg(path):
    with open(path, "r") as f:
        return ast.literal_eval(f.read())


def load_graph(path):
    graph = {}

    with open(path, "r") as f:
        for line in f:
            if "←" not in line:
                continue

            left, right = line.split("←")
            node = left.strip()

            deps = right.strip()
            deps = deps.strip("[]")

            if deps:
                deps = [d.strip().strip("'") for d in deps.split(",")]
            else:
                deps = []

            graph[node] = deps

    return graph

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

def strip(signal):
    return signal.split(".")[-1]

# -------- MAIN --------

def main():
    rtl_folder = "rtl"
    spec_txt_path = "spec/spec.txt"

    os.makedirs("output", exist_ok=True)

    # -------- STEP 1: LOAD SPEC --------
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

    with open("output/signals.txt", "w") as f:
        for s in sorted(rtl_signals):
            f.write(s + "\n")

    # -------- STEP 4: SPEC KG --------
    # from parser.spec_kg_builder import build_spec_kg, kg_to_graph, clean_graph

    # kg = build_spec_kg(spec_text)
    # kg = clean_kg(kg)
    # kg = filter_by_rtl(kg, rtl_signals)

    # with open("output/kg.txt", "w") as f:
    #     f.write(str(kg))

    # graph = clean_graph(kg_to_graph(kg))

    # with open("output/graph.txt", "w") as f:
    #     for k, v in graph.items():
    #         f.write(f"{k} ← {v}\n")

    # -------- STEP 4: LOAD PREBUILT KG + GRAPH --------

    print("\nLoading KG and Graph from files...\n")

    kg = load_kg("output/kg.txt")
    graph = load_graph("output/graph.txt")

    print(f"KG nodes: {len(kg['nodes'])}")
    print(f"Graph nodes: {len(graph)}")

    # -------- STEP 5: TARGETS --------

    def extract_targets(graph, rtl_signals):
        candidates = []

        for node, deps in graph.items():

            if node not in rtl_signals:
                continue

            if not deps:
                continue

            if any(k in node for k in [
                "data", "addr", "count", "ptr",
                "en", "ready", "valid"
            ]):
                candidates.append((node, len(deps)))

        return candidates


    candidates = extract_targets(graph, rtl_signals)


    # -------- SMART SCORING --------
    def score(item):
        node, dep_count = item

        return (
            5 * ("count" in node) +
            4 * ("ptr" in node) +
            3 * ("data" in node) +
            2 * ("addr" in node) +
            2 * ("ready" in node) +
            2 * ("valid" in node) +
            1 * ("en" in node) +
            2 * dep_count          # 🔥 THIS IS KEY
        )


    targets = [t[0] for t in sorted(candidates, key=score, reverse=True)[:15]]

    CLOCK_KEYWORDS = ["clk", "aclk", "smclk", "dco", "lfxt"]

    targets = [
        t for t in targets
        if not any(k in t for k in CLOCK_KEYWORDS)
    ]


    # -------- SAVE --------
    with open("output/targets.txt", "w") as f:
        for t in targets:
            f.write(t + "\n")

    print(f"Selected {len(targets)} targets")

    # -------- STEP 7: CONES --------
    cones = {}
    paths = {}

    with open("output/cones.txt", "w") as f:
        for t in targets:
            base = strip(t)
            result = extract_smart_cone(graph, base)

            cones[t] = result["cone"]
            paths[t] = result["paths"]

            f.write(f"\n===== TARGET: {t} =====\n")
            f.write(f"Cone: {cones[t]}\n")
            f.write("Paths:\n")
            for p in paths[t]:
                f.write(" -> ".join(p) + "\n")

    # -------- STEP 8: CONTEXT --------
    contexts = {}

    with open("output/contexts.txt", "w") as f:
        for t in targets:
            context = build_context(
                rtl_code,
                cones.get(t, []),
                t,
                paths.get(t, [])
            )

            contexts[t] = context

            f.write(f"\n===== TARGET: {t} =====\n")
            f.write(context + "\n")

    # -------- STEP 9: ASSERTIONS --------
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

            # 🔥 Safety check
            if not raw or len(raw.strip()) < 10:
                continue

            cleaned = clean_assertions(raw)
            cleaned = remove_invalid_assertions(cleaned)
            cleaned = remove_weak_assertions(cleaned)

            # 🔥 Skip empty after cleaning
            if not cleaned or len(cleaned.strip()) < 10:
                continue

            # -------- WRITE --------
            f.write("\n" + "="*60 + "\n")
            f.write(f"// TARGET: {t}\n")
            f.write("="*60 + "\n\n")

            f.write(cleaned.strip() + "\n\n")

    print(f"\n✅ All outputs saved in /output folder")
    print(f"✅ Assertions: {output_file}")

if __name__ == "__main__":
    main()