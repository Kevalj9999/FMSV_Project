import re

def extract_modules(rtl_code):
    modules = {}

    pattern = r'module\s+(\w+)(.*?)endmodule'
    matches = re.findall(pattern, rtl_code, re.S)

    for name, body in matches:
        modules[name] = {
            "body": body,
            "instances": [],
        }

        # -------- Extract instances --------
        inst_pattern = r'(\w+)\s+(\w+)\s*\((.*?)\);'
        inst_matches = re.findall(inst_pattern, body, re.S)

        for mod, inst, ports in inst_matches:
            port_map = {}

            connections = re.findall(r'\.(\w+)\((.*?)\)', ports)
            for p, sig in connections:
                port_map[p] = sig.strip()

            modules[name]["instances"].append({
                "module": mod,
                "instance": inst,
                "connections": port_map
            })

    return modules