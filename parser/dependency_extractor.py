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
        if node is None:
            return
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for c in node.children():
            self.visit(c)

    # ------------------ SAFE ADD ------------------
    def safe_add(self, target, sources):
        if self.current_module is None or target is None:
            return

        if target not in self.graph:
            self.graph[target] = set()

        for src in sources:
            if src and src != target:  # avoid self loops
                self.graph[target].add(src)

    # ------------------ ADD DEP ------------------
    def add_dep(self, target, sources):
        if target is None or self.current_module is None:
            return

        target = f"{self.current_module}.{target}"

        sources = {
            f"{self.current_module}.{s}"
            for s in sources
            if s is not None
        }

        self.safe_add(target, sources)

    # ------------------ MODULE ------------------
    def visit_ModuleDef(self, node):
        self.current_module = node.name
        self.port_directions = {}

        if node.portlist:
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

    # ------------------ BLOCKING (=) ------------------
    def visit_BlockingSubstitution(self, node):
        target = self.get_lhs_name(node.left)
        rhs = self.get_rhs_signals(node.right)
        conds = self.get_current_conditions()

        self.add_dep(target, rhs.union(conds))
        self.generic_visit(node)

    # ------------------ INSTANCE ------------------
    def visit_InstanceList(self, node):
        module_type = node.module

        for instance in node.instances:
            for port in instance.portlist:
                signal_name = self.get_lhs_name(port.argname)
                port_name = port.portname

                if not signal_name:
                    continue

                parent = f"{self.current_module}.{signal_name}"
                child = f"{module_type}.{port_name}"

                direction = self.port_directions.get(port_name, "unknown")

                if direction == "input":
                    self.safe_add(child, {parent})

                elif direction == "output":
                    if parent not in self.graph:
                        self.graph[parent] = set()

                    # Keep first driver only
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
        from pyverilog.vparser.ast import Identifier, Pointer, Partselect

        if node is None:
            return None

        if isinstance(node, Identifier):
            return node.name

        elif isinstance(node, Pointer):   # mem[i]
            return self.get_lhs_name(node.var)

        elif isinstance(node, Partselect):  # data[7:0]
            return self.get_lhs_name(node.var)

        return None

    def get_rhs_signals(self, node):
        from pyverilog.vparser.ast import Identifier, Pointer, Partselect, IntConst

        signals = set()

        def visit(n):
            if n is None:
                return

            if isinstance(n, Identifier):
                signals.add(n.name)

            elif isinstance(n, Pointer):
                visit(n.var)
                visit(n.ptr)

            elif isinstance(n, Partselect):
                visit(n.var)

            elif isinstance(n, IntConst):
                return

            else:
                for c in n.children():
                    visit(c)

        visit(node)
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
    
def merge_with_instances(graph, instances):
    for inst_name, data in instances.items():
        for port, signal in data["connections"].items():

            child = f"{inst_name}.{port}"

            if signal not in graph:
                graph[signal] = []

            graph[signal].append(child)

    return graph