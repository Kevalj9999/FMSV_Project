import re

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