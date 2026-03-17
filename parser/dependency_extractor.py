from pyverilog.vparser.ast import *


class DependencyVisitor:
    def __init__(self):
        self.graph = {}

    def visit(self, node):
        """Generic visit function"""
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for c in node.children():
            self.visit(c)

    def add_dep(self, target, sources):
        if target is None:
            return

        if target not in self.graph:
            self.graph[target] = set()

        self.graph[target].update(sources)

    # Handle assign a = b;
    def visit_Assign(self, node):
        target = self.get_lhs_name(node.left)
        sources = self.get_rhs_signals(node.right)
        self.add_dep(target, sources)
        self.generic_visit(node)

    # Handle <=
    def visit_NonblockingSubstitution(self, node):
        target = self.get_lhs_name(node.left)
        sources = self.get_rhs_signals(node.right)
        self.add_dep(target, sources)
        self.generic_visit(node)

    # Handle =
    def visit_BlockingSubstitution(self, node):
        target = self.get_lhs_name(node.left)
        sources = self.get_rhs_signals(node.right)
        self.add_dep(target, sources)
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

    def get_rhs_signals(self, node):
        signals = set()

        if isinstance(node, Identifier):
            signals.add(node.name)

        elif isinstance(node, Pointer):
            signals.add(node.var.name)

        elif isinstance(node, Partselect):
            signals.add(node.var.name)

        for child in node.children():
            signals.update(self.get_rhs_signals(child))

        return signals

    def visit_IfStatement(self, node):
    # Extract signals from condition
        cond_signals = self.get_rhs_signals(node.cond)

        # Visit true branch
        self.handle_branch(node.true_statement, cond_signals)

        # Visit false branch
        if node.false_statement:
            self.handle_branch(node.false_statement, cond_signals)

        self.generic_visit(node)


    def handle_branch(self, node, cond_signals):
        if node is None:
            return

        if isinstance(node, Block):
            for stmt in node.statements:
                self.handle_branch(stmt, cond_signals)

        elif isinstance(node, NonblockingSubstitution) or isinstance(node, BlockingSubstitution):
            target = self.get_lhs_name(node.left)
            if target:
                self.add_dep(target, cond_signals)

        else:
            for c in node.children():
                self.handle_branch(c, cond_signals)

    def get_assigned_targets(self, node):
        targets = set()

        if hasattr(node, "statement") and node.statement:
            targets.update(self.collect_targets(node.statement))

        if hasattr(node, "else_statement") and node.else_statement:
            targets.update(self.collect_targets(node.else_statement))

        return targets


    def collect_targets(self, node):
        targets = set()

        if isinstance(node, NonblockingSubstitution) or isinstance(node, BlockingSubstitution):
            name = self.get_lhs_name(node.left)
            if name:
                targets.add(name)

        for c in node.children():
            targets.update(self.collect_targets(c))

        return targets


def build_dependency_graph(ast):
    visitor = DependencyVisitor()
    visitor.visit(ast)
    return visitor.graph