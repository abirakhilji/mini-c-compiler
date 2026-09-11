"""
Tree-walking Interpreter for mini-C.
AST -> Execution

Ye ek simple memory model use karta hai:
- Har scope ek dict hai (variable name -> value)
- Arrays Python list se represent hote hain
- Pointers ek simple "Reference" object se represent hote hain jo
  kisi scope-dict aur uski key ko point karta hai (address ki jagah)
"""

from ast_nodes import *


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class CRuntimeError(Exception):
    pass


class Reference:
    """Pointer ko represent karta hai: kis scope aur kis variable/index ko point kar raha hai."""
    def __init__(self, container, key):
        self.container = container  # dict (scope) ya list (array)
        self.key = key               # variable name (str) ya array index (int)

    def get(self):
        return self.container[self.key]

    def set(self, value):
        self.container[self.key] = value

    def __repr__(self):
        return f"<Reference -> {self.key}>"


class Scope:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def declare(self, name, value):
        self.vars[name] = value

    def get_scope_holding(self, name):
        """Us scope ko dhundo jisme variable defined hai (dict return karta hai)."""
        scope = self
        while scope is not None:
            if name in scope.vars:
                return scope.vars
            scope = scope.parent
        raise CRuntimeError(f"Undefined variable '{name}'")

    def get(self, name):
        return self.get_scope_holding(name)[name]

    def set(self, name, value):
        self.get_scope_holding(name)[name] = value


class Interpreter:
    def __init__(self, program: Program):
        self.program = program
        self.functions = {}
        self.globals = Scope()
        self.output = []  # printf jaisa output collect karne ke liye

        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl
            elif isinstance(decl, GlobalVarDecl):
                init_val = self.eval_expr(decl.init, self.globals) if decl.init else self.default_value(decl.var_type)
                if decl.array_size is not None:
                    self.globals.declare(decl.name, [self.default_value(decl.var_type)] * decl.array_size)
                else:
                    self.globals.declare(decl.name, init_val)

    def default_value(self, var_type):
        if var_type in ('int', 'char') or var_type.endswith('*'):
            return 0
        if var_type == 'float':
            return 0.0
        return None

    # ---------- Built-in functions ----------
    def call_builtin(self, name, args):
        if name == 'printf':
            if not args:
                return 0
            fmt = args[0]
            rest = args[1:]
            result = self.format_printf(fmt, rest)
            print(result, end='')
            self.output.append(result)
            return len(result)
        raise CRuntimeError(f"Unknown function '{name}'")

    def format_printf(self, fmt, args):
        result = ''
        i = 0
        arg_i = 0
        while i < len(fmt):
            ch = fmt[i]
            if ch == '%' and i + 1 < len(fmt):
                spec = fmt[i + 1]
                if spec == 'd':
                    result += str(int(args[arg_i])); arg_i += 1; i += 2; continue
                elif spec == 'f':
                    result += f"{float(args[arg_i]):.6f}"; arg_i += 1; i += 2; continue
                elif spec == 'c':
                    v = args[arg_i]
                    result += chr(v) if isinstance(v, int) else str(v)
                    arg_i += 1; i += 2; continue
                elif spec == 's':
                    result += str(args[arg_i]); arg_i += 1; i += 2; continue
                elif spec == '%':
                    result += '%'; i += 2; continue
            if ch == '\\' and i + 1 < len(fmt) and fmt[i+1] == 'n':
                result += '\n'; i += 2; continue
            result += ch
            i += 1
        return result

    # ---------- Entry point ----------
    def run(self, entry='main', argv=None):
        if entry not in self.functions:
            raise CRuntimeError(f"No '{entry}' function found")
        return self.call_function(entry, argv or [])

    def call_function(self, name, args):
        if name not in self.functions:
            return self.call_builtin(name, args)

        func = self.functions[name]
        scope = Scope(parent=self.globals)
        for (ptype, pname), arg_val in zip(func.params, args):
            scope.declare(pname, arg_val)

        try:
            self.exec_block(func.body, scope)
        except ReturnException as r:
            return r.value
        return 0  # implicit return

    # ---------- Statement execution ----------
    def exec_block(self, block: Block, scope: Scope):
        inner = Scope(parent=scope)
        for stmt in block.statements:
            self.exec_stmt(stmt, inner)

    def exec_stmt(self, stmt, scope: Scope):
        if isinstance(stmt, VarDecl):
            if stmt.array_size is not None:
                arr = [self.default_value(stmt.var_type)] * stmt.array_size
                scope.declare(stmt.name, arr)
            else:
                value = self.eval_expr(stmt.init, scope) if stmt.init else self.default_value(stmt.var_type)
                scope.declare(stmt.name, value)

        elif isinstance(stmt, ExprStatement):
            self.eval_expr(stmt.expr, scope)

        elif isinstance(stmt, Block):
            self.exec_block(stmt, scope)

        elif isinstance(stmt, If):
            if self.truthy(self.eval_expr(stmt.cond, scope)):
                self.exec_stmt(stmt.then_branch, scope)
            elif stmt.else_branch is not None:
                self.exec_stmt(stmt.else_branch, scope)

        elif isinstance(stmt, While):
            while self.truthy(self.eval_expr(stmt.cond, scope)):
                try:
                    self.exec_stmt(stmt.body, scope)
                except BreakException:
                    break
                except ContinueException:
                    continue

        elif isinstance(stmt, For):
            for_scope = Scope(parent=scope)
            if stmt.init is not None:
                self.exec_stmt(stmt.init, for_scope)
            while stmt.cond is None or self.truthy(self.eval_expr(stmt.cond, for_scope)):
                try:
                    self.exec_stmt(stmt.body, for_scope)
                except BreakException:
                    break
                except ContinueException:
                    pass
                if stmt.update is not None:
                    self.eval_expr(stmt.update, for_scope)

        elif isinstance(stmt, Return):
            value = self.eval_expr(stmt.value, scope) if stmt.value is not None else None
            raise ReturnException(value)

        elif isinstance(stmt, Break):
            raise BreakException()

        elif isinstance(stmt, Continue):
            raise ContinueException()

        else:
            raise CRuntimeError(f"Unknown statement type: {type(stmt).__name__}")

    # ---------- Expression evaluation ----------
    def truthy(self, value):
        return value not in (0, 0.0, None, False)

    def eval_expr(self, expr, scope: Scope):
        if isinstance(expr, Literal):
            return expr.value

        if isinstance(expr, Identifier):
            return scope.get(expr.name)

        if isinstance(expr, ArrayAccess):
            arr = self.eval_expr(expr.array, scope)
            idx = self.eval_expr(expr.index, scope)
            return arr[idx]

        if isinstance(expr, Assign):
            value = self.eval_expr(expr.value, scope)
            self.assign_to(expr.target, value, scope)
            return value

        if isinstance(expr, BinOp):
            return self.eval_binop(expr, scope)

        if isinstance(expr, UnaryOp):
            return self.eval_unaryop(expr, scope)

        if isinstance(expr, FunctionCall):
            args = [self.eval_expr(a, scope) for a in expr.args]
            return self.call_function(expr.name, args)

        raise CRuntimeError(f"Unknown expression type: {type(expr).__name__}")

    def assign_to(self, target, value, scope: Scope):
        if isinstance(target, Identifier):
            scope.set(target.name, value)
        elif isinstance(target, ArrayAccess):
            arr = self.eval_expr(target.array, scope)
            idx = self.eval_expr(target.index, scope)
            arr[idx] = value
        elif isinstance(target, UnaryOp) and target.op == '*':
            # dereference assignment: *ptr = value
            ref = self.eval_expr(target.operand, scope)
            if not isinstance(ref, Reference):
                raise CRuntimeError("Cannot dereference a non-pointer")
            ref.set(value)
        else:
            raise CRuntimeError("Invalid assignment target")

    def eval_binop(self, expr: BinOp, scope: Scope):
        op = expr.op
        if op == '&&':
            return 1 if (self.truthy(self.eval_expr(expr.left, scope)) and
                         self.truthy(self.eval_expr(expr.right, scope))) else 0
        if op == '||':
            return 1 if (self.truthy(self.eval_expr(expr.left, scope)) or
                         self.truthy(self.eval_expr(expr.right, scope))) else 0

        left = self.eval_expr(expr.left, scope)
        right = self.eval_expr(expr.right, scope)

        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/':
            if isinstance(left, int) and isinstance(right, int):
                return int(left / right) if right != 0 else self._div_zero()
            return left / right
        if op == '%': return left % right
        if op == '==': return 1 if left == right else 0
        if op == '!=': return 1 if left != right else 0
        if op == '<': return 1 if left < right else 0
        if op == '>': return 1 if left > right else 0
        if op == '<=': return 1 if left <= right else 0
        if op == '>=': return 1 if left >= right else 0

        raise CRuntimeError(f"Unknown binary operator: {op}")

    def _div_zero(self):
        raise CRuntimeError("Division by zero")

    def eval_unaryop(self, expr: UnaryOp, scope: Scope):
        op = expr.op

        if op == '&':
            # address-of: sirf Identifier ya ArrayAccess pe possible
            if isinstance(expr.operand, Identifier):
                container = scope.get_scope_holding(expr.operand.name)
                return Reference(container, expr.operand.name)
            elif isinstance(expr.operand, ArrayAccess):
                arr = self.eval_expr(expr.operand.array, scope)
                idx = self.eval_expr(expr.operand.index, scope)
                return Reference(arr, idx)
            raise CRuntimeError("Cannot take address of this expression")

        if op == '*':
            ref = self.eval_expr(expr.operand, scope)
            if not isinstance(ref, Reference):
                raise CRuntimeError("Cannot dereference a non-pointer")
            return ref.get()

        if op == '-':
            return -self.eval_expr(expr.operand, scope)

        if op == '!':
            return 0 if self.truthy(self.eval_expr(expr.operand, scope)) else 1

        if op in ('++', '--'):
            old_val = self.eval_expr(expr.operand, scope)
            new_val = old_val + 1 if op == '++' else old_val - 1
            self.assign_to(expr.operand, new_val, scope)
            return old_val if expr.postfix else new_val

        raise CRuntimeError(f"Unknown unary operator: {op}")
