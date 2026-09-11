"""
Lexer (Tokenizer) for our mini-C compiler.
Ye module C source code ko tokens ki list mein todta hai.
"""

class TokenType:
    # Literals
    INT_LITERAL = 'INT_LITERAL'
    FLOAT_LITERAL = 'FLOAT_LITERAL'
    CHAR_LITERAL = 'CHAR_LITERAL'
    STRING_LITERAL = 'STRING_LITERAL'
    IDENTIFIER = 'IDENTIFIER'

    # Keywords
    KEYWORD = 'KEYWORD'

    # Operators
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    STAR = 'STAR'
    SLASH = 'SLASH'
    PERCENT = 'PERCENT'
    ASSIGN = 'ASSIGN'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    GT = 'GT'
    LE = 'LE'
    GE = 'GE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    AMP = 'AMP'          # &  (address-of / bitwise and)
    PLUSPLUS = 'PLUSPLUS'
    MINUSMINUS = 'MINUSMINUS'

    # Punctuation
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    SEMICOLON = 'SEMICOLON'
    COMMA = 'COMMA'

    EOF = 'EOF'


KEYWORDS = {
    'int', 'float', 'char', 'void', 'if', 'else', 'while', 'for',
    'return', 'break', 'continue'
}


class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f'Token({self.type}, {self.value!r}, line={self.line}, col={self.col})'


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(source)

    def error(self, msg):
        raise LexerError(f"Lexer error at line {self.line}, col {self.col}: {msg}")

    def peek(self, offset=0):
        p = self.pos + offset
        if p < self.length:
            return self.source[p]
        return None

    def advance(self):
        ch = self.peek()
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        return ch

    def skip_whitespace_and_comments(self):
        while True:
            ch = self.peek()
            if ch is None:
                return
            if ch in ' \t\r\n':
                self.advance()
                continue
            # single line comment
            if ch == '/' and self.peek(1) == '/':
                while self.peek() is not None and self.peek() != '\n':
                    self.advance()
                continue
            # multi line comment
            if ch == '/' and self.peek(1) == '*':
                self.advance(); self.advance()
                while True:
                    if self.peek() is None:
                        self.error("Unterminated block comment")
                    if self.peek() == '*' and self.peek(1) == '/':
                        self.advance(); self.advance()
                        break
                    self.advance()
                continue
            return

    def make_number(self):
        start_line, start_col = self.line, self.col
        num_str = ''
        is_float = False
        while self.peek() is not None and self.peek().isdigit():
            num_str += self.advance()
        if self.peek() == '.':
            is_float = True
            num_str += self.advance()
            while self.peek() is not None and self.peek().isdigit():
                num_str += self.advance()
        if is_float:
            return Token(TokenType.FLOAT_LITERAL, float(num_str), start_line, start_col)
        else:
            return Token(TokenType.INT_LITERAL, int(num_str), start_line, start_col)

    def make_identifier(self):
        start_line, start_col = self.line, self.col
        id_str = ''
        while self.peek() is not None and (self.peek().isalnum() or self.peek() == '_'):
            id_str += self.advance()
        if id_str in KEYWORDS:
            return Token(TokenType.KEYWORD, id_str, start_line, start_col)
        return Token(TokenType.IDENTIFIER, id_str, start_line, start_col)

    def make_char_literal(self):
        start_line, start_col = self.line, self.col
        self.advance()  # consume opening '
        if self.peek() == '\\':
            self.advance()
            esc = self.advance()
            escapes = {'n': '\n', 't': '\t', '0': '\0', '\\': '\\', "'": "'", '"': '"'}
            ch = escapes.get(esc, esc)
        else:
            ch = self.advance()
        if self.peek() != "'":
            self.error("Unterminated char literal")
        self.advance()  # consume closing '
        return Token(TokenType.CHAR_LITERAL, ch, start_line, start_col)

    def make_string_literal(self):
        start_line, start_col = self.line, self.col
        self.advance()  # consume opening "
        s = ''
        while self.peek() is not None and self.peek() != '"':
            ch = self.advance()
            if ch == '\\':
                esc = self.advance()
                escapes = {'n': '\n', 't': '\t', '0': '\0', '\\': '\\', "'": "'", '"': '"'}
                s += escapes.get(esc, esc)
            else:
                s += ch
        if self.peek() != '"':
            self.error("Unterminated string literal")
        self.advance()  # consume closing "
        return Token(TokenType.STRING_LITERAL, s, start_line, start_col)

    def tokenize(self):
        tokens = []
        while True:
            self.skip_whitespace_and_comments()
            ch = self.peek()
            if ch is None:
                tokens.append(Token(TokenType.EOF, None, self.line, self.col))
                break

            line, col = self.line, self.col

            if ch.isdigit():
                tokens.append(self.make_number())
                continue

            if ch.isalpha() or ch == '_':
                tokens.append(self.make_identifier())
                continue

            if ch == "'":
                tokens.append(self.make_char_literal())
                continue

            if ch == '"':
                tokens.append(self.make_string_literal())
                continue

            # two-character operators
            two = ch + (self.peek(1) or '')
            two_char_map = {
                '==': TokenType.EQ, '!=': TokenType.NEQ,
                '<=': TokenType.LE, '>=': TokenType.GE,
                '&&': TokenType.AND, '||': TokenType.OR,
                '++': TokenType.PLUSPLUS, '--': TokenType.MINUSMINUS,
            }
            if two in two_char_map:
                self.advance(); self.advance()
                tokens.append(Token(two_char_map[two], two, line, col))
                continue

            single_char_map = {
                '+': TokenType.PLUS, '-': TokenType.MINUS,
                '*': TokenType.STAR, '/': TokenType.SLASH,
                '%': TokenType.PERCENT, '=': TokenType.ASSIGN,
                '<': TokenType.LT, '>': TokenType.GT,
                '!': TokenType.NOT, '&': TokenType.AMP,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN,
                '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON, ',': TokenType.COMMA,
            }
            if ch in single_char_map:
                self.advance()
                tokens.append(Token(single_char_map[ch], ch, line, col))
                continue

            self.error(f"Unexpected character {ch!r}")

        return tokens


if __name__ == '__main__':
    sample = '''
    int main() {
        int x = 5;
        int y = 10;
        if (x < y) {
            return x + y;
        }
        return 0;
    }
    '''
    lexer = Lexer(sample)
    for tok in lexer.tokenize():
        print(tok)
