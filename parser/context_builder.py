import re

def extract_always_blocks(rtl_code):
    return re.findall(r'always\s*@.*?end', rtl_code, re.DOTALL)


def extract_assigns(rtl_code):
    return re.findall(r'assign\s+.*?;', rtl_code)


def match_signal(sig, text):
    sig = sig.split(".")[-1]
    return (
        sig in text or
        any(sig in word for word in text.split())
    )


def build_context(rtl_code, cone, target, paths):
    context_blocks = []

    always_blocks = extract_always_blocks(rtl_code)
    assigns = extract_assigns(rtl_code)

    target_base = target.split(".")[-1]

    # -------- 1. TARGET MATCH --------
    for block in always_blocks:
        if target_base in block:
            context_blocks.append(block.strip())

    # -------- 2. CONE MATCH --------
    for block in always_blocks:
        if any(match_signal(sig, block) for sig in cone):
            context_blocks.append(block.strip())

    # -------- 3. ASSIGN MATCH --------
    for stmt in assigns:
        if target_base in stmt or any(match_signal(sig, stmt) for sig in cone):
            context_blocks.append(stmt.strip())

    # -------- 4. FALLBACK --------
    if not context_blocks:
        context_blocks = always_blocks[:3]

    # -------- CLEAN --------
    context_blocks = list(set(context_blocks))[:5]

    path_text = "\n".join([
        "// Path: " + " -> ".join(p)
        for p in paths[:5]
    ])

    return f"""
// ===== RTL LOGIC =====
{chr(10).join(context_blocks)}

// ===== DEPENDENCY PATHS =====
{path_text}
"""