from pyverilog.vparser.ast import *


class TargetVisitor:
    def __init__(self):
        self.targets = set()

    def visit(self, node):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for c in node.children():
            self.visit(c)

    # Capture registers updated in always blocks
    def visit_NonblockingSubstitution(self, node):
        target = self.get_lhs_name(node.left)
        if target:
            self.targets.add(target)
        self.generic_visit(node)

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


def extract_targets(ast):
    visitor = TargetVisitor()
    visitor.visit(ast)
    return visitor.targets