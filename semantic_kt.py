from ast_kt import (
    Program, FunDecl, Param, VarDecl, Assignment,
    IfStmt, WhileStmt, ReturnStmt, PrintStmt,
    BinaryOp, UnaryOp, Literal, Identifier, FunCall
)


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, info):
        if name in self.scopes[-1]:
            return False
        self.scopes[-1][name] = info
        return True

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = SymbolTable()

    def analyze(self, node):
        self.visit(node)

    def visit(self, node):
        method = getattr(self, f'visit_{type(node).__name__}', None)
        if method:
            method(node)
        else:
            for child in self._children(node):
                self.visit(child)

    def _children(self, node):
        if isinstance(node, Program):
            return node.statements
        elif isinstance(node, FunDecl):
            return node.params + node.body
        elif isinstance(node, Param):
            return []
        elif isinstance(node, VarDecl):
            return [node.value]
        elif isinstance(node, Assignment):
            return [node.value]
        elif isinstance(node, IfStmt):
            children = [node.condition]
            children.extend(node.then_body)
            if node.else_body:
                children.extend(node.else_body)
            return children
        elif isinstance(node, WhileStmt):
            return [node.condition] + node.body
        elif isinstance(node, ReturnStmt):
            return [node.value] if node.value else []
        elif isinstance(node, PrintStmt):
            return [node.value]
        elif isinstance(node, BinaryOp):
            return [node.left, node.right]
        elif isinstance(node, UnaryOp):
            return [node.operand]
        else:
            return []

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_FunDecl(self, node):
        if not self.symbols.declare(node.name, {'kind': 'function', 'params': node.params}):
            print(f"[ERRO SEMÂNTICO] Função '{node.name}' já declarada neste escopo")
        self.symbols.enter_scope()
        for p in node.params:
            self.symbols.declare(p.name, {'kind': 'param', 'type': p.type_name})
        for stmt in node.body:
            self.visit(stmt)
        self.symbols.exit_scope()

    def visit_VarDecl(self, node):
        self.visit(node.value)
        inferred_type = self._infer_type(node.value)
        if not self.symbols.declare(node.name, {'kind': 'variable', 'type': inferred_type, 'mut': node.kind == 'var'}):
            print(f"[ERRO SEMÂNTICO] Variável '{node.name}' já declarada neste escopo")

    def visit_Assignment(self, node):
        info = self.symbols.lookup(node.name)
        if info is None:
            print(f"[ERRO SEMÂNTICO] Variável '{node.name}' não declarada antes do uso")
        elif info['kind'] == 'variable' and not info.get('mut', False):
            print(f"[ERRO SEMÂNTICO] Variável '{node.name}' é imutável (val)")
        self.visit(node.value)

    def visit_Identifier(self, node):
        info = self.symbols.lookup(node.name)
        if info is None:
            print(f"[ERRO SEMÂNTICO] Variável '{node.name}' não declarada antes do uso")

    def visit_FunCall(self, node):
        info = self.symbols.lookup(node.name)
        if info is None:
            print(f"[ERRO SEMÂNTICO] Função '{node.name}' não declarada")
        for arg in node.args:
            self.visit(arg)

    def visit_IfStmt(self, node):
        self.visit(node.condition)
        self.symbols.enter_scope()
        for stmt in node.then_body:
            self.visit(stmt)
        self.symbols.exit_scope()
        if node.else_body:
            self.symbols.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.symbols.exit_scope()

    def visit_WhileStmt(self, node):
        self.visit(node.condition)
        self.symbols.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbols.exit_scope()

    def _infer_type(self, node):
        if isinstance(node, Literal):
            return node.type_name
        if isinstance(node, Identifier):
            info = self.symbols.lookup(node.name)
            if info:
                return info.get('type', '?')
            return '?'
        if isinstance(node, BinaryOp):
            left_type = self._infer_type(node.left)
            right_type = self._infer_type(node.right)
            if left_type == 'Double' or right_type == 'Double':
                return 'Double'
            if left_type == 'Int' and right_type == 'Int':
                return 'Int'
            if node.op in ('>', '<', '==', '!='):
                return 'Boolean'
            return left_type if left_type != '?' else right_type
        if isinstance(node, UnaryOp):
            return self._infer_type(node.operand)
        if isinstance(node, FunCall):
            return '?'
        if isinstance(node, PrintStmt):
            return 'Unit'
        return '?'
