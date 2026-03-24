def build_port_map(instances):
    """
    Build cross-module signal mapping
    """
    port_map = {}

    for inst_name, data in instances.items():
        for port, signal in data["connections"].items():
            full_port = f"{inst_name}.{port}"

            if signal not in port_map:
                port_map[signal] = []

            port_map[signal].append(full_port)

    return port_map