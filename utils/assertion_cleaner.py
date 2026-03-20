def is_valid_assertion(line):
    if "|->" not in line and "|=>" not in line:
        return False

    if not line.strip().startswith("assert property"):
        return False

    return True


def clean_assertions(assertions):
    cleaned = []
    seen = set()

    for line in assertions.split("\n"):
        l = line.strip()

        if not l:
            continue

        # ❌ skip invalid format
        if not is_valid_assertion(l):
            continue

        # ❌ skip meaningless negation-only assertions
        if l.endswith("));") and ("|->" not in l and "|=>" not in l):
            continue

        # ❌ skip inequality hallucinations
        if "!=" in l:
            continue

        # ❌ deduplicate
        if l in seen:
            continue

        seen.add(l)
        cleaned.append(l)

    return "\n".join(cleaned)