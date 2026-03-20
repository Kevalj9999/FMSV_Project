import re

def extract_signals(context):
    signals = set()

    # -------- INPUTS --------
    signals.update(re.findall(
        r'\binput\s+(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # -------- OUTPUTS --------
    signals.update(re.findall(
        r'\boutput\s+(?:reg\s+)?(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # -------- REGS --------
    signals.update(re.findall(
        r'\breg\s+(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # -------- PARAMETERS --------
    signals.update(re.findall(
        r'\bparameter\s+(\w+)', context))

    # -------- LHS ASSIGNMENTS --------
    signals.update(re.findall(
        r'\b(\w+)\s*<=', context))

    # -------- RHS EXPRESSIONS (ROBUST) --------
    rhs_expressions = re.findall(r'<=\s*(.*?);', context)
    for expr in rhs_expressions:
        tokens = re.findall(r'\b[a-zA-Z_]\w*\b', expr)
        signals.update(tokens)

    # -------- CONDITIONS (if, case, ternary) --------
    condition_exprs = re.findall(r'\bif\s*\((.*?)\)', context)
    condition_exprs += re.findall(r'\bcase\s*\((.*?)\)', context)

    for expr in condition_exprs:
        tokens = re.findall(r'\b[a-zA-Z_]\w*\b', expr)
        signals.update(tokens)

    # -------- MEMORY INDEXING (mem[rd_ptr]) --------
    mem_indices = re.findall(r'\b(\w+)\[(\w+)\]', context)
    for mem, idx in mem_indices:
        signals.add(mem)
        signals.add(idx)

    # -------- CLEANUP --------
    blacklist = {
        "if", "else", "case", "begin", "end",
        "posedge", "negedge",
        "default"
    }

    # Remove numbers and keywords
    signals = {
        s for s in signals
        if not s.isdigit() and s not in blacklist
    }

    return sorted(signals)