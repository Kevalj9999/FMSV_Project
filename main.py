import os
from parser.rtl_parser import parse_rtl
from parser.dependency_extractor import build_dependency_graph
from parser.target_selector import extract_targets
from parser.cone_extractor import extract_cone
from parser.context_builder import build_context
from llm.generator import generate_assertions
from parser.signal_extractor import extract_signals


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
        # Skip memory-related signals (not useful for assertions)
        if any(keyword in t.lower() for keyword in ["mem", "memory"]):
            continue
        filtered.append(t)
    return filtered


def main():
    rtl_folder = "rtl"
    spec_file = "spec/spec.txt"

    rtl_files = get_rtl_files(rtl_folder)
    print(f"Found {len(rtl_files)} RTL files")

    print("Parsing RTL files (incremental mode - memory efficient)...")
    ast = parse_rtl(rtl_files, incremental=True)

    print("Building dependency graph...")
    graph = build_dependency_graph(ast)

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

    print("\n--- Combined Context Assertion Generation ---\n")

    # -------- DEDUPLICATE CONTEXT --------
    unique_contexts = set()

    for t in targets:
        ctx = contexts.get(t, "").strip()
        if ctx:
            unique_contexts.add(ctx)

    combined_context = "\n\n".join(unique_contexts)

    # -------- SAFETY CHECK --------
    if not combined_context.strip():
        print("No valid context found ❌")
        return

    # -------- DEBUG --------
    print("\n--- COMBINED CONTEXT ---\n")
    print(combined_context)

    # -------- SIGNAL EXTRACTION --------
    signals = extract_signals(combined_context)

    print("\n--- EXTRACTED SIGNALS ---\n")
    print(signals)

    # -------- ASSERTION GENERATION --------
    assertions = generate_assertions(combined_context, spec, signals)

    print("\n--- FINAL ASSERTIONS ---\n")
    print(assertions)


if __name__ == "__main__":
    main()