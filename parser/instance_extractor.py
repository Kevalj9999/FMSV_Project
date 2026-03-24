from pyverilog.vparser.ast import InstanceList, Instance

def extract_instances(ast):
    """
    Extract module instances and port connections
    Returns:
        instances = {
            "top.u_fifo": {
                "module": "fifo",
                "connections": {
                    "wr_en": "top.wr_en",
                    "rd_en": "top.rd_en"
                }
            }
        }
    """
    instances = {}

    def visit(node, current_module=None):
        from pyverilog.vparser.ast import ModuleDef

        if isinstance(node, ModuleDef):
            current_module = node.name

        if isinstance(node, InstanceList):
            for inst in node.instances:
                if isinstance(inst, Instance):
                    inst_name = f"{current_module}.{inst.name}"
                    module_type = node.module

                    connections = {}
                    for port in inst.portlist:
                        if port.portname and port.argname:
                            connections[port.portname] = str(port.argname)

                    instances[inst_name] = {
                        "module": module_type,
                        "connections": connections
                    }

        for c in node.children():
            visit(c, current_module)

    visit(ast)
    return instances