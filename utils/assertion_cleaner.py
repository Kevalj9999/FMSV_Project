import re

def clean_assertions(text):
    valid_blocks = []

    # ✅ 1. Capture property + assert blocks
    pattern1 = r'(property[\s\S]*?endproperty\s*assert property\s*\(.*?\);)'
    matches1 = re.findall(pattern1, text, re.MULTILINE)

    # ✅ 2. Capture inline assertions
    pattern2 = r'(assert property\s*\(.*?\);)'
    matches2 = re.findall(pattern2, text, re.MULTILINE)

    all_blocks = matches1 + matches2

    for b in all_blocks:
        b = b.strip()

        # Must have temporal operator
        if "|->" not in b and "|=>" not in b:
            continue

        # ❌ Remove useless always-true logic
        if "<" in b and "+ 1" in b:
            continue

        # ❌ Remove weak dependency guesses
        if "dependency" in b or "throughout" in b:
            continue

        valid_blocks.append(b)

    return "\n\n".join(valid_blocks)