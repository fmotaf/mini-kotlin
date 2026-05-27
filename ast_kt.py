class Program:
    def __init__(self, statements):
        self.statements = statements

class FunDecl:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Param:
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name

class VarDecl:
    def __init__(self, kind, name, value):
        self.kind = kind
        self.name = name
        self.value = value

class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class IfStmt:
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class WhileStmt:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ReturnStmt:
    def __init__(self, value=None):
        self.value = value

class PrintStmt:
    def __init__(self, value):
        self.value = value

class BinaryOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Literal:
    def __init__(self, value, type_name):
        self.value = value
        self.type_name = type_name

class FunCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Identifier:
    def __init__(self, name):
        self.name = name


def print_ast(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, Program):
        print(f"{prefix}Program")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    elif isinstance(node, FunDecl):
        print(f"{prefix}FunDecl: {node.name}")
        for p in node.params:
            print(f"{prefix}  Param: {p.name}: {p.type_name}")
        for s in node.body:
            print_ast(s, indent + 1)
    elif isinstance(node, VarDecl):
        print(f"{prefix}VarDecl({node.kind}): {node.name}")
        print_ast(node.value, indent + 1)
    elif isinstance(node, Assignment):
        print(f"{prefix}Assignment: {node.name}")
        print_ast(node.value, indent + 1)
    elif isinstance(node, IfStmt):
        print(f"{prefix}IfStmt")
        print(f"{prefix}  Condition:")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}  Then:")
        for s in node.then_body:
            print_ast(s, indent + 2)
        if node.else_body:
            print(f"{prefix}  Else:")
            for s in node.else_body:
                print_ast(s, indent + 2)
    elif isinstance(node, WhileStmt):
        print(f"{prefix}WhileStmt")
        print(f"{prefix}  Condition:")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}  Body:")
        for s in node.body:
            print_ast(s, indent + 2)
    elif isinstance(node, ReturnStmt):
        print(f"{prefix}ReturnStmt")
        if node.value:
            print_ast(node.value, indent + 1)
    elif isinstance(node, PrintStmt):
        print(f"{prefix}PrintStmt")
        print_ast(node.value, indent + 1)
    elif isinstance(node, BinaryOp):
        print(f"{prefix}BinaryOp: {node.op}")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnaryOp: {node.op}")
        print_ast(node.operand, indent + 1)
    elif isinstance(node, Literal):
        print(f"{prefix}Literal: {node.value} ({node.type_name})")
    elif isinstance(node, FunCall):
        print(f"{prefix}FunCall: {node.name}")
        for arg in node.args:
            print_ast(arg, indent + 1)
    elif isinstance(node, Identifier):
        print(f"{prefix}Identifier: {node.name}")
