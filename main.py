import os
from sys import modules
from parser.rtl_parser import parse_rtl
from parser.dependency_extractor import build_dependency_graph
from parser.target_selector import extract_targets
from parser.cone_extractor import extract_cone
from parser.context_builder import build_context
from llm.generator import generate_assertions
from llm.generator import clean_assertions
from parser.signal_extractor import extract_signals
from utils.assertion_cleaner import clean_assertions
from parser.module_extractor import extract_modules
from parser.global_dependency import build_global_graph


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
        # Skip memory-related signals
        if any(keyword in t.lower() for keyword in ["mem", "memory"]):
            continue
        filtered.append(t)
    return filtered


def is_control_target(t):
    """
    Optional: keep only meaningful verification targets
    Helps scaling for large RTL like OpenMSP
    """
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
    # Load RTL code
    rtl_code = load_rtl_code(rtl_files)

    # Extract modules
    modules = extract_modules(rtl_code)

    # Build local graph
    local_graph = build_dependency_graph(ast)

    # Build global graph (NEW)
    graph = build_global_graph(local_graph, modules)

    print("\n--- Dependency Graph (Sample) ---\n")
    for i, (target, deps) in enumerate(graph.items()):
        print(f"{target} ← {list(deps)}")
        if i >= 20:
            break

    # -------- TARGET EXTRACTION --------
    raw_targets = extract_targets(ast)
    targets = filter_targets(raw_targets)

    # OPTIONAL: Enable this for large RTL (OpenMSP)
    # targets = [t for t in targets if is_control_target(t)]

    # OPTIONAL: limit targets for LLM cost/control
    # targets = targets[:5]

    print("\n--- Targets ---\n")
    for t in targets:
        print(t)

    # -------- LOAD RTL --------
    rtl_code = load_rtl_code(rtl_files)

    # -------- CONE EXTRACTION --------
    print("\n--- Register Cones ---\n")
    cones = {}

    for target in targets:
        cone = extract_cone(graph, target)
        cones[target] = cone

        print(f"\nTarget: {target}")
        print("Cone:", list(cone))

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

    # -------- PER-TARGET ASSERTION GENERATION --------
    print("\n--- FINAL ASSERTIONS (PER TARGET) ---\n")

    for target in targets:
        context = contexts.get(target, "").strip()

        if not context:
            continue

        print(f"\n===== TARGET: {target} =====\n")

        # Extract signals ONLY for this context
        signals = extract_signals(context)

        print("--- Signals ---")
        print(signals)

        # Generate assertions for this target
        raw_assertions = generate_assertions(context, spec, signals,target)
        cleaned_assertions = clean_assertions(raw_assertions)

        print("\n--- Assertions ---\n")
        print(cleaned_assertions)


if __name__ == "__main__":
    main()