import re

def extract_signals_fallback(rtl_code):
    signals = set()

    # match wire/reg/input/output
    pattern = r'\b(input|output|wire|reg)\b\s+(?:\[[^\]]+\]\s*)?([\w, ]+);'

    matches = re.findall(pattern, rtl_code)

    for _, group in matches:
        for sig in group.split(","):
            sig = sig.strip()
            if sig:
                signals.add(sig.lower())

    return signals