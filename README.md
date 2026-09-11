# Mini-C Compiler (Interpreter)

A small C compiler/interpreter written in Python. It follows this pipeline:

```
Source Code (.c) --> Lexer --> Tokens --> Parser --> AST --> Interpreter --> Output
```

## Files

| File | Purpose |
|---|---|
| `lexer.py` | Breaks source code into tokens |
| `ast_nodes.py` | AST node classes (Program, FunctionDecl, BinOp, etc.) |
| `parser.py` | Builds an AST from tokens (recursive descent parser) |
| `interpreter.py` | Executes the AST (tree-walking interpreter) |
| `mini_c.py` | Main entry point that ties everything together |

## How to use

```bash
# Run a C program
python3 mini_c.py tests/test1_basic.c

# View only the tokens
python3 mini_c.py --tokens tests/test1_basic.c

# View only the AST structure
python3 mini_c.py --ast tests/test1_basic.c
```

## Supported Features

- **Types:** `int`, `float`, `char`, `void`, pointers (`int*`)
- **Variables:** declaration, initialization, assignment
- **Operators:** `+ - * / %`, `== != < > <= >=`, `&& || !`, `& *` (address-of / dereference), `++ --`
- **Control flow:** `if/else`, `while`, `for`, `break`, `continue`
- **Functions:** declaration, calls, recursion, return values
- **Arrays:** declaration (`int arr[5]`), indexing, assignment
- **Pointers:** address-of (`&x`), dereference (`*ptr`), modifying a value through a pointer
- **Built-in:** `printf` (with `%d`, `%f`, `%c`, `%s`, `\n` support)
- **Comments:** `//` and `/* */`

## Not yet supported (future scope)

- `struct`, `union`, `enum`
- Preprocessor directives (`#include`, `#define`)
- Multi-dimensional arrays
- String library functions (`strlen`, `strcpy`, etc.), rest of the standard library
- Real machine code / assembly generation (this is currently an interpreter, not a compiler)
- Static type checking (type errors are currently caught only at runtime)

## Understanding the Architecture

1. **Lexer** — reads the source character by character and produces meaningful tokens
   (keywords, identifiers, numbers, operators, punctuation).

2. **Parser** — takes the list of tokens and, following C's grammar rules, builds a
   tree (AST). Operator precedence (e.g., `*` binding tighter than `+`) is handled here.

3. **Interpreter** — walks the AST from top to bottom and executes it directly.
   Variables are stored in scopes (dictionaries), and functions behave like a call
   stack (`return`/`break`/`continue` are implemented using Python exceptions).

## Ideas for extending this project

- Add `struct` support
- Generate real x86/ARM assembly (to make it an actual "compiler")
- Add a type checker (to catch semantic errors)
- Add standard library functions (`malloc`, `strlen`, etc.)
- Better error messages with source line highlighting
