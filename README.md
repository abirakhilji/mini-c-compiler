# Mini-C Compiler (Interpreter)

Ye ek chhota C compiler/interpreter hai jo Python mein likha gaya hai. Ye pipeline follow karta hai:

```
Source Code (.c) --> Lexer --> Tokens --> Parser --> AST --> Interpreter --> Output
```

## Files

| File | Kaam |
|---|---|
| `lexer.py` | Source code ko tokens mein todta hai |
| `ast_nodes.py` | AST node classes (Program, FunctionDecl, BinOp, etc.) |
| `parser.py` | Tokens se AST banata hai (recursive descent parser) |
| `interpreter.py` | AST ko execute karta hai (tree-walking interpreter) |
| `mini_c.py` | Sabko jodne wala main entry point |

## Kaise use karein

```bash
# Ek C program run karo
python3 mini_c.py tests/test1_basic.c

# Sirf tokens dekhna hai
python3 mini_c.py --tokens tests/test1_basic.c

# Sirf AST structure dekhna hai
python3 mini_c.py --ast tests/test1_basic.c
```

## Supported Features

- **Types:** `int`, `float`, `char`, `void`, pointers (`int*`)
- **Variables:** declaration, initialization, assignment
- **Operators:** `+ - * / %`, `== != < > <= >=`, `&& || !`, `& *` (address-of / dereference), `++ --`
- **Control flow:** `if/else`, `while`, `for`, `break`, `continue`
- **Functions:** declaration, calls, recursion, return values
- **Arrays:** declaration (`int arr[5]`), indexing, assignment
- **Pointers:** address-of (`&x`), dereference (`*ptr`), pointer se value modify karna
- **Built-in:** `printf` (with `%d`, `%f`, `%c`, `%s`, `\n` support)
- **Comments:** `//` aur `/* */`

## Abhi NAHI supported (future scope)

- `struct`, `union`, `enum`
- Preprocessor directives (`#include`, `#define`)
- Multi-dimensional arrays
- String library (`strlen`, `strcpy` etc.), standard library ke baaki functions
- Real machine code / assembly generation (abhi ye ek interpreter hai, compiler nahi)
- Static type checking (abhi runtime pe hi type errors pakde jaate hain)

## Architecture samjhein

1. **Lexer** — character by character source padhta hai aur meaningful tokens banata hai
   (keywords, identifiers, numbers, operators, punctuation).

2. **Parser** — tokens ki list lekar, C ki grammar rules follow karte hue, ek tree
   (AST) banata hai. Operator precedence (jaise `*` pehle `+` se) yahin handle hota hai.

3. **Interpreter** — AST ko top se bottom traverse karta hai aur directly execute
   karta hai. Variables scopes (dict) mein store hote hain, functions call stack
   jaisa behave karte hain (Python exceptions use karke `return`/`break`/`continue`
   implement kiya gaya hai).

## Aage kya extend kar sakte ho

- `struct` support add karna
- Real x86/ARM assembly generation (asli "compiler" banane ke liye)
- Type checker add karna (semantic errors pakadne ke liye)
- Standard library functions (`malloc`, `strlen`, etc.)
- Better error messages with source line highlighting
