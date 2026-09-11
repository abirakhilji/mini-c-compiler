#!/usr/bin/env python3
"""
mini_c.py - Mini C Compiler/Interpreter ka entry point

Usage:
    python3 mini_c.py <source_file.c>
    python3 mini_c.py --tokens <source_file.c>   # sirf tokens dikhaye
    python3 mini_c.py --ast <source_file.c>      # sirf AST structure dikhaye
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from interpreter import Interpreter, CRuntimeError
from ast_nodes import *


def print_ast(node, indent=0):
    prefix = '  ' * indent
    if isinstance(node, Program):
        print(f"{prefix}Program")
        for d in node.declarations:
            print_ast(d, indent + 1)
    elif isinstance(node, FunctionDecl):
        print(f"{prefix}FunctionDecl: {node.return_type} {node.name}({node.params})")
        print_ast(node.body, indent + 1)
    elif isinstance(node, Block):
        print(f"{prefix}Block")
        for s in node.statements:
            print_ast(s, indent + 1)
    elif isinstance(node, VarDecl):
        print(f"{prefix}VarDecl: {node.var_type} {node.name}")
    elif isinstance(node, If):
        print(f"{prefix}If")
        print_ast(node.then_branch, indent + 1)
        if node.else_branch:
            print(f"{prefix}Else")
            print_ast(node.else_branch, indent + 1)
    elif isinstance(node, While):
        print(f"{prefix}While")
        print_ast(node.body, indent + 1)
    elif isinstance(node, For):
        print(f"{prefix}For")
        print_ast(node.body, indent + 1)
    elif isinstance(node, Return):
        print(f"{prefix}Return")
    else:
        print(f"{prefix}{type(node).__name__}")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 mini_c.py [--tokens|--ast] <source_file.c>")
        sys.exit(1)

    mode = 'run'
    if args[0] in ('--tokens', '--ast'):
        mode = args[0][2:]
        args = args[1:]

    if not args:
        print("Error: source file specify karo")
        sys.exit(1)

    filepath = args[0]
    with open(filepath, 'r') as f:
        source = f.read()

    try:
        tokens = Lexer(source).tokenize()
        if mode == 'tokens':
            for t in tokens:
                print(t)
            return

        program = Parser(tokens).parse_program()
        if mode == 'ast':
            print_ast(program)
            return

        interpreter = Interpreter(program)
        exit_code = interpreter.run('main')
        sys.exit(exit_code if isinstance(exit_code, int) else 0)

    except LexerError as e:
        print(f"Lexical Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ParserError as e:
        print(f"Syntax Error: {e}", file=sys.stderr)
        sys.exit(1)
    except CRuntimeError as e:
        print(f"Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
