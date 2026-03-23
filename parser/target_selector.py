from pyverilog.vparser.ast import *


class TargetVisitor:
    def __init__(self):
        self.targets = set()
        self.current_module = None

    # ------------------ VISIT ------------------
    def visit(self, node):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for c in node.children():
            self.visit(c)

    # ------------------ MODULE ------------------
    def visit_ModuleDef(self, node):
        self.current_module = node.name
        self.generic_visit(node)

    # ------------------ REGISTER TARGETS ------------------
    def visit_NonblockingSubstitution(self, node):
        target = self.get_lhs_name(node.left)

        if target and self.current_module:
            full_name = f"{self.current_module}.{target}"

            # 🔥 Filter out useless signals
            if not self.is_noise_signal(target):
                self.targets.add(full_name)

        self.generic_visit(node)

    # ------------------ HELPERS ------------------
    def get_lhs_name(self, node):
        if isinstance(node, Lvalue):
            node = node.var

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, Pointer):
            return node.var.name

        if isinstance(node, Partselect):
            return node.var.name

        return None

    def is_noise_signal(self, name):
        name = name.lower()

        # ❌ Remove clock/reset and trivial signals
        if name in ["clk", "clock", "rst", "reset"]:
            return True

        return False


# ================== ENTRY FUNCTION ==================

def extract_targets(ast):
    visitor = TargetVisitor()
    visitor.visit(ast)

    return sorted(visitor.targets)