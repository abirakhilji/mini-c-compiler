"""
Recursive-descent Parser for mini-C compiler.
Tokens -> AST

Grammar (simplified):
    program        -> (function_decl | global_var_decl)*
    function_decl  -> type IDENT '(' params? ')' block
    global_var_decl-> type IDENT ('[' INT ']')? ('=' expr)? ';'
    block          -> '{' statement* '}'
    statement      -> var_decl | if_stmt | while_stmt | for_stmt
                     | return_stmt | break_stmt | continue_stmt
                     | block | expr_stmt
    expr           -> assignment
    assignment     -> logic_or ('=' assignment)?
    logic_or       -> logic_and ('||' logic_and)*
    logic_and      -> equality ('&&' equality)*
    equality       -> relational (('==' | '!=') relational)*
    relational     -> additive (('<' | '>' | '<=' | '>=') additive)*
    additive       -> term (('+' | '-') term)*
    term           -> unary (('*' | '/' | '%') unary)*
    unary          -> ('!' | '-' | '&' | '*' | '++' | '--') unary | postfix
    postfix        -> primary ( '[' expr ']' | '++' | '--' )*
    primary        -> INT | FLOAT | CHAR | STRING | IDENT | IDENT '(' args? ')'
                     | '(' expr ')'
"""

from lexer import TokenType
from ast_nodes import *

TYPE_KEYWORDS = {'int', 'float', 'char', 'void'}


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---------- helpers ----------
    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def advance(self):
        tok = self.peek()
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def check(self, type_, value=None):
        tok = self.peek()
        if tok.type != type_:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def match(self, type_, value=None):
        if self.check(type_, value):
            return self.advance()
        return None

    def expect(self, type_, value=None):
        if self.check(type_, value):
            return self.advance()
        tok = self.peek()
        expected = value if value else type_
        self.error(f"Expected {expected} but got {tok.type} ({tok.value!r})")

    def error(self, msg):
        tok = self.peek()
        raise ParserError(f"Parser error at line {tok.line}, col {tok.col}: {msg}")

    def is_type_keyword(self):
        tok = self.peek()
        return tok.type == TokenType.KEYWORD and tok.value in TYPE_KEYWORDS

    # ---------- top level ----------
    def parse_program(self):
        decls = []
        while not self.check(TokenType.EOF):
            decls.append(self.parse_top_level_decl())
        return Program(decls)

    def parse_top_level_decl(self):
        # type IDENT ...
        type_tok = self.expect(TokenType.KEYWORD)
        var_type = type_tok.value
        # handle pointer type: int *ptr
        while self.match(TokenType.STAR):
            var_type += '*'
        name_tok = self.expect(TokenType.IDENTIFIER)
        name = name_tok.value

        if self.check(TokenType.LPAREN):
            # function declaration
            self.advance()  # consume (
            params = self.parse_params()
            self.expect(TokenType.RPAREN)
            body = self.parse_block()
            return FunctionDecl(var_type, name, params, body)
        else:
            # global variable
            array_size = None
            if self.match(TokenType.LBRACKET):
                size_tok = self.expect(TokenType.INT_LITERAL)
                array_size = size_tok.value
                self.expect(TokenType.RBRACKET)
            init = None
            if self.match(TokenType.ASSIGN):
                init = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return GlobalVarDecl(var_type, name, init, array_size)

    def parse_params(self):
        params = []
        if self.check(TokenType.RPAREN):
            return params
        while True:
            type_tok = self.expect(TokenType.KEYWORD)
            ptype = type_tok.value
            while self.match(TokenType.STAR):
                ptype += '*'
            name_tok = self.expect(TokenType.IDENTIFIER)
            params.append((ptype, name_tok.value))
            if not self.match(TokenType.COMMA):
                break
        return params

    # ---------- statements ----------
    def parse_block(self):
        self.expect(TokenType.LBRACE)
        statements = []
        while not self.check(TokenType.RBRACE):
            statements.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return Block(statements)

    def parse_statement(self):
        if self.check(TokenType.LBRACE):
            return self.parse_block()

        if self.is_type_keyword():
            return self.parse_var_decl()

        if self.check(TokenType.KEYWORD, 'if'):
            return self.parse_if()

        if self.check(TokenType.KEYWORD, 'while'):
            return self.parse_while()

        if self.check(TokenType.KEYWORD, 'for'):
            return self.parse_for()

        if self.check(TokenType.KEYWORD, 'return'):
            self.advance()
            value = None
            if not self.check(TokenType.SEMICOLON):
                value = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return Return(value)

        if self.check(TokenType.KEYWORD, 'break'):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return Break()

        if self.check(TokenType.KEYWORD, 'continue'):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return Continue()

        # expression statement
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ExprStatement(expr)

    def parse_var_decl(self):
        type_tok = self.expect(TokenType.KEYWORD)
        var_type = type_tok.value
        while self.match(TokenType.STAR):
            var_type += '*'
        name_tok = self.expect(TokenType.IDENTIFIER)
        name = name_tok.value
        array_size = None
        if self.match(TokenType.LBRACKET):
            size_tok = self.expect(TokenType.INT_LITERAL)
            array_size = size_tok.value
            self.expect(TokenType.RBRACKET)
        init = None
        if self.match(TokenType.ASSIGN):
            init = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return VarDecl(var_type, name, init, array_size)

    def parse_if(self):
        self.advance()  # 'if'
        self.expect(TokenType.LPAREN)
        cond = self.parse_expr()
        self.expect(TokenType.RPAREN)
        then_branch = self.parse_statement()
        else_branch = None
        if self.match(TokenType.KEYWORD, 'else'):
            else_branch = self.parse_statement()
        return If(cond, then_branch, else_branch)

    def parse_while(self):
        self.advance()  # 'while'
        self.expect(TokenType.LPAREN)
        cond = self.parse_expr()
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        return While(cond, body)

    def parse_for(self):
        self.advance()  # 'for'
        self.expect(TokenType.LPAREN)
        init = None
        if not self.check(TokenType.SEMICOLON):
            if self.is_type_keyword():
                init = self.parse_var_decl_no_semi()
            else:
                init = ExprStatement(self.parse_expr())
        self.expect(TokenType.SEMICOLON)
        cond = None
        if not self.check(TokenType.SEMICOLON):
            cond = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        update = None
        if not self.check(TokenType.RPAREN):
            update = self.parse_expr()
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        return For(init, cond, update, body)

    def parse_var_decl_no_semi(self):
        type_tok = self.expect(TokenType.KEYWORD)
        var_type = type_tok.value
        while self.match(TokenType.STAR):
            var_type += '*'
        name_tok = self.expect(TokenType.IDENTIFIER)
        name = name_tok.value
        init = None
        if self.match(TokenType.ASSIGN):
            init = self.parse_expr()
        return VarDecl(var_type, name, init)

    # ---------- expressions (precedence climbing) ----------
    def parse_expr(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logic_or()
        if self.match(TokenType.ASSIGN):
            value = self.parse_assignment()
            return Assign(left, value)
        return left

    def parse_logic_or(self):
        left = self.parse_logic_and()
        while self.check(TokenType.OR):
            op = self.advance().value
            right = self.parse_logic_and()
            left = BinOp(op, left, right)
        return left

    def parse_logic_and(self):
        left = self.parse_equality()
        while self.check(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinOp(op, left, right)
        return left

    def parse_equality(self):
        left = self.parse_relational()
        while self.check(TokenType.EQ) or self.check(TokenType.NEQ):
            op = self.advance().value
            right = self.parse_relational()
            left = BinOp(op, left, right)
        return left

    def parse_relational(self):
        left = self.parse_additive()
        while (self.check(TokenType.LT) or self.check(TokenType.GT)
               or self.check(TokenType.LE) or self.check(TokenType.GE)):
            op = self.advance().value
            right = self.parse_additive()
            left = BinOp(op, left, right)
        return left

    def parse_additive(self):
        left = self.parse_term()
        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            op = self.advance().value
            right = self.parse_term()
            left = BinOp(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_unary()
        while (self.check(TokenType.STAR) or self.check(TokenType.SLASH)
               or self.check(TokenType.PERCENT)):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self):
        if self.check(TokenType.NOT) or self.check(TokenType.MINUS) or \
           self.check(TokenType.AMP) or self.check(TokenType.STAR) or \
           self.check(TokenType.PLUSPLUS) or self.check(TokenType.MINUSMINUS):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.match(TokenType.LBRACKET):
                index = self.parse_expr()
                self.expect(TokenType.RBRACKET)
                expr = ArrayAccess(expr, index)
            elif self.check(TokenType.PLUSPLUS) or self.check(TokenType.MINUSMINUS):
                op = self.advance().value
                expr = UnaryOp(op, expr, postfix=True)
            else:
                break
        return expr

    def parse_primary(self):
        tok = self.peek()

        if tok.type == TokenType.INT_LITERAL:
            self.advance()
            return Literal(tok.value, 'int')

        if tok.type == TokenType.FLOAT_LITERAL:
            self.advance()
            return Literal(tok.value, 'float')

        if tok.type == TokenType.CHAR_LITERAL:
            self.advance()
            return Literal(tok.value, 'char')

        if tok.type == TokenType.STRING_LITERAL:
            self.advance()
            return Literal(tok.value, 'string')

        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            if self.check(TokenType.LPAREN):
                self.advance()
                args = []
                if not self.check(TokenType.RPAREN):
                    args.append(self.parse_expr())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_expr())
                self.expect(TokenType.RPAREN)
                return FunctionCall(tok.value, args)
            return Identifier(tok.value)

        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr

        self.error(f"Unexpected token {tok.type} ({tok.value!r})")


if __name__ == '__main__':
    from lexer import Lexer
    sample = '''
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        int x = 5;
        int y = 10;
        int result = add(x, y);
        if (result > 10) {
            result = result - 1;
        }
        return result;
    }
    '''
    tokens = Lexer(sample).tokenize()
    program = Parser(tokens).parse_program()
    print(f"Parsed {len(program.declarations)} top-level declarations")
    for decl in program.declarations:
        print(f" - {type(decl).__name__}: {decl.name}")
