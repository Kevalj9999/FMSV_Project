def build_context(rtl_code, cone, target):
    lines = rtl_code.split("\n")

    header = """
input clk;
input reset;
"""

    # -------- STEP 1: Extract COMPLETE always blocks (FIXED) --------
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

                # Track begin-end properly
                if "begin" in stripped:
                    depth += 1
                if "end" in stripped:
                    depth -= 1

                # Close block only when fully balanced
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

    def is_target_assignment(line, target):
        return f"{target} <=" in line or f"{target} =" in line

    def contains_target(line):
        return target in line

    # -------- STEP 3: TARGET-FOCUSED slicing --------
    sliced_blocks = []

    for block in blocks:
        new_block = []
        keep_block = False

        for line in block.split("\n"):
            stripped = line.strip()

            # Always keep structure (prevents broken RTL)
            if is_structure(stripped):
                new_block.append(line)
                continue

            # Keep ONLY assignments of target
            if is_assignment(stripped) and is_target_assignment(stripped, target):
                new_block.append(line)
                keep_block = True
                continue

            # Keep conditions involving target
            # Keep assignments even if not directly target, if inside useful block
            if is_assignment(stripped):
                new_block.append(line)
                continue

            # Keep conditions related to cone (NOT just target)
            if any(sig in stripped for sig in cone):
                new_block.append(line)

        # Only keep meaningful blocks
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
    # Ensure target is actually assigned (STRICT)
    final_blocks = []

    for block in unique_blocks:
        if any(is_target_assignment(line, target) for line in block.split("\n")):
            final_blocks.append(block)

    # -------- STEP 6: RETURN --------
    return header + "\n\n".join(final_blocks)