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
        if any(keyword in t.lower() for keyword in ["mem", "memory"]):
            continue
        filtered.append(t)
    return filtered


def main():
    rtl_folder = "rtl"
    spec_file = "spec/spec.txt"

    rtl_files = get_rtl_files(rtl_folder)

    print("Parsing RTL files...")
    ast = parse_rtl(rtl_files)

    print("Building dependency graph...")
    graph = build_dependency_graph(ast)

    print("\n--- Dependency Graph (Sample) ---\n")
    for i, (target, deps) in enumerate(graph.items()):
        print(f"{target} ← {list(deps)}")
        if i >= 20:
            break

    # Extract targets
    raw_targets = extract_targets(ast)
    targets = filter_targets(raw_targets)

    print("\n--- Targets ---\n")
    for t in targets:
        print(t)

    # Load RTL code
    rtl_code = load_rtl_code(rtl_files)

    print("\n--- Register Cones ---\n")
    cones = {}

    for target in targets:
        cone = extract_cone(graph, target)
        cones[target] = cone

        print(f"\nTarget: {target}")
        print("Cone:", list(cone))

    print("\n--- Context Extraction ---\n")
    contexts = {}

    for target in targets:
        context = build_context(rtl_code, cones[target])
        contexts[target] = context

        print(f"\nTarget: {target}")
        print("Context:\n", context)

    # Load specification
    with open(spec_file, "r") as f:
        spec = f.read()

    print("\n--- Combined Context Assertion Generation ---\n")

    # ✅ Use ALL targets (works for any RTL, not just FIFO)
    combined_context = ""

    for t in targets:
        combined_context += contexts.get(t, "") + "\n"

    # ✅ Safety check
    if not combined_context.strip():
        print("No valid context found ❌")
        return

    # ✅ Debug
    print("\n--- COMBINED CONTEXT ---\n")
    print(combined_context)

    # ✅ Extract signals from combined context (CORRECT)
    signals = extract_signals(combined_context)

    print("\n--- EXTRACTED SIGNALS ---\n")
    print(signals)

    # ✅ Generate assertions
    assertions = generate_assertions(combined_context, spec, signals)

    print("\n--- FINAL ASSERTIONS ---\n")
    print(assertions)


if __name__ == "__main__":
    main()