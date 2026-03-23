from pyverilog.vparser.ast import *


class DependencyVisitor:
    def __init__(self):
        self.graph = {}
        self.condition_stack = []
        self.current_module = None

    # ------------------ CONDITION STACK ------------------
    def get_current_conditions(self):
        all_conds = set()
        for cond in self.condition_stack:
            all_conds.update(cond)
        return all_conds

    # ------------------ VISIT ------------------
    def visit(self, node):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for c in node.children():
            self.visit(c)

    # ------------------ SAFE ADD ------------------
    def safe_add(self, target, sources):
        if self.current_module is None:
            return
        if target not in self.graph:
            self.graph[target] = set()

        for src in sources:
            if src != target:  # ❌ remove self-loops
                self.graph[target].add(src)

    # ------------------ ADD DEP ------------------
    def add_dep(self, target, sources):
        if self.current_module is None:
            return
        if target is None or self.current_module is None:
            return

        target = f"{self.current_module}.{target}"
        sources = {f"{self.current_module}.{s}" for s in sources}

        self.safe_add(target, sources)

    # ------------------ MODULE ------------------
    def visit_ModuleDef(self, node):
        self.current_module = node.name
        self.port_directions = {}

        for item in node.portlist.ports:
            if isinstance(item, Ioport):
                name = item.first.name
                if isinstance(item.first, Input):
                    self.port_directions[name] = "input"
                elif isinstance(item.first, Output):
                    self.port_directions[name] = "output"

        self.generic_visit(node)

    # ------------------ ASSIGN (=) ------------------
    def visit_Assign(self, node):
        target = self.get_lhs_name(node.left)
        rhs = self.get_rhs_signals(node.right)
        conds = self.get_current_conditions()

        self.add_dep(target, rhs.union(conds))
        self.generic_visit(node)

    # ------------------ NONBLOCKING (<=) ------------------
    def visit_NonblockingSubstitution(self, node):
        target = self.get_lhs_name(node.left)
        rhs = self.get_rhs_signals(node.right)
        conds = self.get_current_conditions()

        self.add_dep(target, rhs.union(conds))
        self.generic_visit(node)

    # ------------------ BLOCKING ------------------
    def visit_BlockingSubstitution(self, node):
        target = self.get_lhs_name(node.left)
        rhs = self.get_rhs_signals(node.right)
        conds = self.get_current_conditions()

        self.add_dep(target, rhs.union(conds))
        self.generic_visit(node)

    # ------------------ INSTANCE (FIXED 🔥) ------------------
    def visit_InstanceList(self, node):
        module_type = node.module  # child module

        for instance in node.instances:
            for port in instance.portlist:
                port_name = port.portname
                signal_name = self.get_lhs_name(port.argname)

                if signal_name:
                    parent = f"{self.current_module}.{signal_name}"
                    child = f"{module_type}.{port_name}"

                    direction = self.port_directions.get(port_name, "unknown")

                    if direction == "input":
                        # child depends on parent
                        self.safe_add(child, {parent})

                    elif direction == "output":
                        # parent depends on child
                        if parent not in self.graph:
                            self.graph[parent] = set()

                        # Only keep first driver (simple fix)
                        if len(self.graph[parent]) == 0:
                            self.graph[parent].add(child)


    # ------------------ IF ------------------
    def visit_IfStatement(self, node):
        cond_signals = self.get_rhs_signals(node.cond)

        self.condition_stack.append(cond_signals)

        if node.true_statement:
            self.visit(node.true_statement)

        if node.false_statement:
            self.visit(node.false_statement)

        self.condition_stack.pop()

    # ------------------ CASE ------------------
    def visit_CaseStatement(self, node):
        case_expr_signals = self.get_rhs_signals(node.comp)

        for case_item in node.caselist:
            item_conds = set(case_expr_signals)

            if case_item.cond:
                for cond in case_item.cond:
                    item_conds.update(self.get_rhs_signals(cond))

            self.condition_stack.append(item_conds)

            if case_item.statement:
                self.visit(case_item.statement)

            self.condition_stack.pop()

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

    def get_rhs_signals(self, node):
        signals = set()

        if isinstance(node, Identifier):
            signals.add(node.name)

        elif isinstance(node, Pointer):
            signals.add(node.var.name)

        elif isinstance(node, Partselect):
            signals.add(node.var.name)

        elif isinstance(node, IntConst):
            return set()  # ✅ ignore constants properly

        for child in node.children():
            signals.update(self.get_rhs_signals(child))

        return signals


# ================== GRAPH BUILDER ==================

class DependencyGraphBuilder:
    def merge_graphs(self, graph1, graph2):
        merged = dict(graph1)

        for target, sources in graph2.items():
            if target not in merged:
                merged[target] = set()
            merged[target].update(sources)

        return merged

    def build_graph_from_files(self, ast_list):
        graphs = []

        for ast in ast_list:
            if ast is None:
                continue

            visitor = DependencyVisitor()
            visitor.visit(ast)
            graphs.append(visitor.graph)

        if not graphs:
            return {}

        result = graphs[0]
        for graph in graphs[1:]:
            result = self.merge_graphs(result, graph)

        return result


# ================== ENTRY FUNCTION ==================

def build_dependency_graph(ast):
    if isinstance(ast, list):
        builder = DependencyGraphBuilder()
        return builder.build_graph_from_files(ast)
    else:
        visitor = DependencyVisitor()
        visitor.visit(ast)
        return visitor.graph