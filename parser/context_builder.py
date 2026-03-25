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

    path_text = "\n".join([
        "// Path: " + " -> ".join(p)
        for p in paths[:5]
    ])

    return f"""
// ===== TARGET =====
{target}

// ===== DEPENDENCY PATHS =====
{path_text}
"""