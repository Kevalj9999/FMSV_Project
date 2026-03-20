def build_context(rtl_code, cone, target):
    lines = rtl_code.split("\n")

    header = """
input clk;
input reset;
"""

    # -------- STEP 1: Extract always blocks --------
    blocks = []
    current_block = []
    inside = False
    depth = 0

    for line in lines:
        stripped = line.strip()

        if "always" in stripped:
            inside = True
            depth = 0
            current_block = [line]
            continue

        if inside:
            current_block.append(line)

            if "begin" in stripped:
                depth += 1
            if "end" in stripped:
                depth -= 1

            if depth <= 0 and "end" in stripped:
                blocks.append("\n".join(current_block))
                inside = False

    # -------- STEP 2: relevance check --------
    def contains_cone_signal(line):
        return any(sig in line for sig in cone)

    def is_structure(line):
        keywords = ["if", "else", "case", "endcase", "begin", "end"]
        return any(k in line for k in keywords)

    def is_assignment(line):
        return "<=" in line or "=" in line

    # -------- STEP 3: smart slicing --------
    sliced_blocks = []

    for block in blocks:
        keep_block = False
        new_block = []

        for line in block.split("\n"):
            stripped = line.strip()

            # Keep structure always (important for correctness)
            if is_structure(stripped):
                new_block.append(line)
                continue

            # Keep lines involving ANY cone signal
            if contains_cone_signal(stripped):
                new_block.append(line)
                keep_block = True
                continue

        if keep_block:
            sliced_blocks.append("\n".join(new_block))

    # -------- STEP 4: deduplicate --------
    unique_blocks = []
    seen = set()

    for block in sliced_blocks:
        key = "\n".join([l.strip() for l in block.split("\n")])
        if key not in seen:
            seen.add(key)
            unique_blocks.append(block)

    # -------- STEP 5: FINAL FILTER (important) --------
    # Only keep blocks where TARGET is actually assigned
    final_blocks = []

    for block in unique_blocks:
        if target in block:
            final_blocks.append(block)

    return header + "\n\n".join(final_blocks)