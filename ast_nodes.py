"""
AST Node definitions for mini-C compiler.
Har node ek grammar construct represent karta hai.
"""

class Node:
    pass


# ---------- Top level ----------
class Program(Node):
    def __init__(self, declarations):
        self.declarations = declarations  # list of FunctionDecl / GlobalVarDecl


class FunctionDecl(Node):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type
        self.name = name
        self.params = params  # list of (type, name)
        self.body = body      # Block


class GlobalVarDecl(Node):
    def __init__(self, var_type, name, init=None, array_size=None):
        self.var_type = var_type
        self.name = name
        self.init = init
        self.array_size = array_size


# ---------- Statements ----------
class Block(Node):
    def __init__(self, statements):
        self.statements = statements


class VarDecl(Node):
    def __init__(self, var_type, name, init=None, array_size=None):
        self.var_type = var_type
        self.name = name
        self.init = init
        self.array_size = array_size


class Assign(Node):
    def __init__(self, target, value):
        self.target = target  # Identifier or ArrayAccess or UnaryOp('*', ...)
        self.value = value


class If(Node):
    def __init__(self, cond, then_branch, else_branch=None):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch


class While(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body


class For(Node):
    def __init__(self, init, cond, update, body):
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body


class Return(Node):
    def __init__(self, value=None):
        self.value = value


class Break(Node):
    pass


class Continue(Node):
    pass


class ExprStatement(Node):
    def __init__(self, expr):
        self.expr = expr


# ---------- Expressions ----------
class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryOp(Node):
    def __init__(self, op, operand, postfix=False):
        self.op = op
        self.operand = operand
        self.postfix = postfix


class Literal(Node):
    def __init__(self, value, lit_type):
        self.value = value
        self.lit_type = lit_type  # 'int', 'float', 'char', 'string'


class Identifier(Node):
    def __init__(self, name):
        self.name = name


class ArrayAccess(Node):
    def __init__(self, array, index):
        self.array = array
        self.index = index


class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args
