import re


# ---------------- MODULE SPLITTING ----------------

def split_modules(rtl_code):
    modules = {}

    pattern = r'module\s+(\w+).*?endmodule'
    matches = re.findall(pattern, rtl_code, re.DOTALL)

    for match in matches:
        name = match[0]
        body = match[1]
        modules[name] = body

    return modules


# ---------------- EXTRACTORS ----------------

def extract_always_blocks(code):
    return re.findall(r'always\s*@.*?end', code, re.DOTALL)


def extract_assigns(code):
    return re.findall(r'assign\s+.*?;', code)

def is_noise_block(block):
    noise_keywords = [
        "uart", "dbg_", "scan_", "wdt", "clock", "bcsctl"
    ]
    return any(k in block.lower() for k in noise_keywords)

# ---------------- MATCH ----------------
def match_signal(sig, text):
    sig = sig.split(".")[-1]

    # break into tokens
    tokens = sig.split("_")

    words = re.findall(r'\b\w+\b', text)

    for word in words:
        word_tokens = word.split("_")

        # ✅ STRONG match: LAST token must match EXACTLY
        if tokens[-1] == word_tokens[-1]:
            return True

        # ✅ MEDIUM match: full token match (not substring)
        if any(t == wt for t in tokens for wt in word_tokens):
            return True

    return False


def is_relevant(block, signals):
    return any(match_signal(s, block) for s in signals)


# ---------------- MAIN ----------------

def build_context(rtl_code, cone, target, paths):

    modules = split_modules(rtl_code)

    target_base = target.split(".")[-1]

    # 🔥 STEP 1: find correct module
    selected_module = None
    best_score = 0

    signals = set(cone)
    signals.add(target_base)

    for mod_name, body in modules.items():
        score = 0

        for sig in signals:
            if match_signal(sig, body):
                score += 2   # stronger weight

        # 🔥 BOOST if target appears
        if match_signal(target_base, body):
            score += 5

        if score > best_score:
            best_score = score
            selected_module = body

    # fallback
    if not selected_module or best_score < 3:
        selected_module = rtl_code

    always_blocks = extract_always_blocks(selected_module)
    assigns = extract_assigns(selected_module)

    signals = set(cone)
    signals.add(target_base)

    context_blocks = []

    # -------- 1. TARGET BLOCK --------
    for block in always_blocks:
        if match_signal(target_base, block):
            context_blocks.append(block.strip())

    # -------- 2. CONE BLOCKS --------
    for block in always_blocks:
        if is_relevant(block, signals):
            context_blocks.append(block.strip())

    # -------- 3. ASSIGNS --------
    for stmt in assigns:
        if is_relevant(stmt, signals):
            context_blocks.append(stmt.strip())

    # -------- REMOVE DUPLICATES --------
    unique = []
    seen = set()
    for b in context_blocks:
        if b not in seen:
            unique.append(b)
            seen.add(b)

    # -------- SCORING --------
    def score(b):
        s = 0
        if match_signal(target_base, b):
            s += 5
        for sig in signals:
            if match_signal(sig, b):
                s += 1
        return s

    unique = sorted(unique, key=score, reverse=True)

    # -------- LIMIT --------
    context_blocks = unique[:6]

    # -------- FALLBACK --------
    if not context_blocks:
        context_blocks = always_blocks[:2]

    # -------- PATHS --------
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