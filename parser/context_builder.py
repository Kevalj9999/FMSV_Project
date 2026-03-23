def build_context(rtl_code, cone, target, paths=None):
    lines = rtl_code.split("\n")

    header = """
input clk;
input reset;
"""

    # -------- STEP 1: Extract COMPLETE always blocks --------
    def extract_blocks(lines):
        blocks = []
        current = []
        inside = False
        depth = 0

        for line in lines:
            stripped = line.strip()

            if "always" in stripped:
                inside = True
                depth = 0
                current = [line]
                continue

            if inside:
                current.append(line)

                if "begin" in stripped:
                    depth += 1
                if "end" in stripped:
                    depth -= 1

                if depth <= 0 and stripped == "end":
                    blocks.append("\n".join(current))
                    inside = False

        return blocks

    blocks = extract_blocks(lines)

    # -------- STEP 2: helpers --------
    def is_structure(line):
        keywords = ["if", "else", "case", "endcase", "begin", "end", "always"]
        return any(k in line for k in keywords)

    def is_assignment(line):
        return "<=" in line or "=" in line

    def is_target_assignment(line):
        return f"{target} <=" in line or f"{target} =" in line

    def contains_cone_signal(line):
        return any(sig.split(".")[-1] in line for sig in cone)

    # -------- STEP 3: TARGET + CONE slicing --------
    sliced_blocks = []

    for block in blocks:
        new_block = []
        keep_block = False

        for line in block.split("\n"):
            stripped = line.strip()

            # Always keep structure
            if is_structure(stripped):
                new_block.append(line)
                continue

            # Keep target assignment (CRITICAL)
            if is_assignment(stripped) and is_target_assignment(stripped):
                new_block.append(line)
                keep_block = True
                continue

            # Keep assignments related to cone (filtered)
            if is_assignment(stripped) and contains_cone_signal(stripped):
                new_block.append(line)
                continue

            # Keep conditions involving cone
            if contains_cone_signal(stripped):
                new_block.append(line)

        if keep_block:
            sliced_blocks.append("\n".join(new_block))

    # -------- STEP 4: Deduplicate --------
    unique_blocks = []
    seen = set()

    for block in sliced_blocks:
        key = "\n".join([l.strip() for l in block.split("\n")])
        if key not in seen:
            seen.add(key)
            unique_blocks.append(block)

    # -------- STEP 5: FINAL FILTER --------
    final_blocks = []

    for block in unique_blocks:
        if any(is_target_assignment(line) for line in block.split("\n")):
            final_blocks.append(block)

    # -------- STEP 6: PATH CONTEXT (🔥 NEW FEATURE) --------
    path_text = ""

    if paths:
        path_text += "\n// ===== Dependency Paths =====\n"
        for i, path in enumerate(paths[:5]):  # limit paths
            short_path = [p.split(".")[-1] for p in path]
            path_text += f"// Path {i+1}: " + " -> ".join(short_path) + "\n"

    # -------- STEP 7: RETURN --------
    return header + path_text + "\n\n".join(final_blocks)