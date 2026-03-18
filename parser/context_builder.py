def build_context(rtl_code, cone, target=None):
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

    # -------- STEP 2: Behavioral slicing --------

    def is_structure(line):
        keywords = ["if", "else", "case", "endcase", "begin", "end", "always"]
        return any(k in line for k in keywords)

    def is_assignment(line):
        return "<=" in line or "=" in line

    def is_behaviorally_relevant(line, target):
        if target is None:
            return True

        # Direct assignment to target
        if target in line and is_assignment(line):
            return True

        # Conditions controlling logic
        if "if" in line or "case" in line:
            return True

        # Control signals (generic)
        control_keywords = [
            "wr_en", "rd_en", "enable", "valid", "ready",
            "start", "done"
        ]
        if any(k in line for k in control_keywords):
            return True

        return False

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

            # Keep only behaviorally relevant lines
            if is_behaviorally_relevant(stripped, target):
                new_block.append(line)

                # Only mark useful if target actually appears
                if target and target in stripped:
                    keep_block = True

        # Keep block only if target appears inside
        if keep_block:
            sliced_blocks.append("\n".join(new_block))

    # -------- STEP 3: Deduplicate --------
    unique_blocks = []
    seen = set()

    for block in sliced_blocks:
        key = "\n".join([l.strip() for l in block.split("\n")])
        if key not in seen:
            seen.add(key)
            unique_blocks.append(block)

    return header + "\n\n".join(unique_blocks)