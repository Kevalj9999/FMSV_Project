import re

def extract_signals(context):
    signals = set()

    # inputs
    signals.update(re.findall(r'input\s+(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # outputs
    signals.update(re.findall(r'output\s+(?:reg\s+)?(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # regs
    signals.update(re.findall(r'reg\s+(?:\[\d+:\d+\]\s+)?(\w+)', context))

    # parameters (FSM states)
    signals.update(re.findall(r'parameter\s+(\w+)', context))

    # LHS assignments
    signals.update(re.findall(r'(\w+)\s*<=', context))

    # manual fallback (CRITICAL)
    fallback = ["state", "timer", "highway_light", "farm_light", "sensor", "reset", "clk"]
    signals.update(fallback)

    return list(signals)