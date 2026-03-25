import re

def is_valid_assertion(block):
    block = block.strip()

    # ❌ reject garbage patterns
    bad_patterns = [
        "some_", "enable_condition", "expected_",
        "-> ->", "|-> |->"
    ]

    for p in bad_patterns:
        if p in block:
            return False

    # ❌ multiple implications
    if block.count("|->") > 1:
        return False

    # ❌ empty property
    if "property" in block and "endproperty" in block:
        lines = block.split("\n")
        if len(lines) <= 3:
            return False

    return True


def clean_assertions(text):
    blocks = re.split(r'\n\s*\n', text)

    cleaned = []

    for b in blocks:
        if "property" in b and is_valid_assertion(b):
            cleaned.append(b.strip())

    return "\n\n".join(cleaned)

def remove_invalid_assertions(text):
    lines = text.split("\n")
    filtered = []

    for l in lines:
        if "!= " in l:
            parts = l.split("!=")
            if parts[0].strip() == parts[1].strip():
                continue

        if "== " in l:
            parts = l.split("==")
            if parts[0].strip() == parts[1].strip():
                continue

        filtered.append(l)

    return "\n".join(filtered)


def remove_weak_assertions(text):
    lines = text.split("\n")
    filtered = []

    for l in lines:
        if "!= 0" in l and "$past" not in l:
            continue
        filtered.append(l)

    return "\n".join(filtered)