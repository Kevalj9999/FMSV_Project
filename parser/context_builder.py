def build_context(rtl_code, cone):
    lines = rtl_code.split("\n")
    selected = []

    for line in lines:
        for signal in cone:
            if signal in line:
                selected.append(line)
                break

    context = "\n".join(selected)

    # 🔥 IMPORTANT: prepend module header manually
    header = """
input clk;
input reset;
input sensor;
"""

    return header + "\n" + context