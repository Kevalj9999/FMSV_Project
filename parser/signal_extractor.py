import re

def extract_signals(context):
    signals = set()

    # -------- INPUTS --------
    signals.update(re.findall(
        r'input\s+(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # -------- OUTPUTS --------
    signals.update(re.findall(
        r'output\s+(?:reg\s+)?(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # -------- REGS --------
    signals.update(re.findall(
        r'reg\s+(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # -------- PARAMETERS (FSM states etc.) --------
    signals.update(re.findall(
        r'parameter\s+(\w+)', context))

    # -------- LHS ASSIGNMENTS --------
    signals.update(re.findall(
        r'\b(\w+)\s*<=', context))

    # -------- RHS SIGNALS (IMPORTANT ADDITION) --------
    signals.update(re.findall(
        r'<=\s*(\w+)', context))

    # -------- CONDITIONS --------
    signals.update(re.findall(
        r'\bif\s*\((.*?)\)', context))

    # Flatten condition signals
    condition_signals = set()
    for cond in list(signals):
        if " " in cond or "&&" in cond or "||" in cond:
            tokens = re.findall(r'\b\w+\b', cond)
            condition_signals.update(tokens)
            signals.discard(cond)

    signals.update(condition_signals)

    # -------- CLEANUP --------
    # Remove numbers and keywords
    blacklist = {
        "if", "else", "case", "begin", "end",
        "posedge", "negedge"
    }

    signals = {
        s for s in signals
        if not s.isdigit() and s not in blacklist
    }

    return sorted(signals)