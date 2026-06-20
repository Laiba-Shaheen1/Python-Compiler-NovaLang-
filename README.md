# NovaLang ⬡

A compiled programming language with its own lexer, parser, AST, and LLVM IR backend — written entirely in Python.

NovaLang compiles `.nova` source files down to **LLVM IR**, the same intermediate representation used by Clang/C++, Rust, and Swift. Programs can be run instantly via JIT or compiled to a native executable.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Language Reference](#language-reference)
- [The IDE](#the-ide)
- [How It Works](#how-it-works)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [License](#license)

---

## Features

- **Data types** — integer, float, boolean, string
- **Arithmetic** — `+ - * / %` and unary minus
- **Comparison** — `== != > < >= <=`
- **Logical operators** — `&& || !`
- **Control flow** — `if`, `if / else`, `while` loops
- **I/O** — `print()` for all supported types
- **Comments** — `// single-line` and `/* multi-line */`
- **Variable re-assignment**
- **JIT execution** — run programs instantly, no separate LLVM install required
- **GUI IDE** — dark/light themed editor with syntax highlighting, error line markers, and an examples gallery

---

## Project Structure

| File | Role | Description |
|---|---|---|
| `lexer.py` | Tokenizer | Converts source text into a token stream using `rply` |
| `nova_parser.py` | Grammar + AST | Defines grammar rules and builds AST node objects |
| `nova_ast.py` | IR Emitter | Each AST node class emits LLVM IR via `.eval()` |
| `codegen.py` | LLVM Module | Sets up the LLVM module, declares `printf`, verifies and saves `output.ll` |
| `main.py` | CLI Compiler | Drives lexer → parser → eval, handles `--run` flag and errors |
| `Ide.py` | GUI IDE | Full tkinter IDE — editor, console, syntax highlighting, themes |
| `input.nova` | Sample program | Default source file compiled by `main.py` |

---

## Requirements

### Python packages

```bash
pip install rply llvmlite
```

### Optional (for native `.exe` compilation only)

| Tool | Purpose |
|---|---|
| LLVM (`clang`, `llc`) | Compile IR to native assembly/executables |
| Visual Studio Build Tools (Windows) | Provides `libcmt.lib` / `kernel32.lib` needed by the linker |

> You do **not** need Flex, Bison, or any C/C++ toolchain to run NovaLang — `rply` handles lexing and parsing entirely in Python, and the `--run` flag JIT-executes programs directly.

---

## Installation

```bash
git clone <your-repo-url>
cd NovaLang
pip install rply llvmlite
```

---

## Usage

### Compile and run with JIT (recommended)

```bash
python main.py input.nova --run
```

### Compile only (writes LLVM IR to a file)

```bash
python main.py input.nova -o output.ll
```

### Use a custom source file

```bash
python main.py myprogram.nova --run
```

### Launch the GUI IDE

```bash
python Ide.py
```

### CLI options

| Flag | Description |
|---|---|
| `source` | Path to `.nova` file (default: `input.nova`) |
| `-o, --output` | Output `.ll` file path (default: `output.ll`) |
| `--run` | JIT-execute the program immediately after compiling |
| `-q, --quiet` | Suppress banner and info messages |

---

## Language Reference

### Types

```nova
42          // integer
3.14        // float
true        // boolean
false       // boolean
"hello"     // string
```

### Variables

```nova
x = 10;
x = x + 1;   // re-assignment supported
```

### Operators

| Category | Operators |
|---|---|
| Arithmetic | `+` `-` `*` `/` `%` |
| Unary | `-x` |
| Comparison | `==` `!=` `>` `<` `>=` `<=` |
| Logical | `&&` `\|\|` `!` |

### Print

```nova
print(42);
print(3.14);
print("Hello, NovaLang!");
print(true);
```

### If / Else

```nova
if (x > 10) {
    print(1);
} else {
    print(0);
}

// if without else is also valid
if (x == 5) {
    print(x);
}
```

### While Loop

```nova
i = 1;
while (i < 5) {
    print(i);
    i = i + 1;
}
```

### Comments

```nova
// single-line comment
/* multi-line
   comment */
```

### Example — FizzBuzz

```nova
n = 1;
while (n <= 15) {
    if (n % 15 == 0) {
        print("FizzBuzz");
    } else {
        if (n % 3 == 0) {
            print("Fizz");
        } else {
            if (n % 5 == 0) {
                print("Buzz");
            } else {
                print(n);
            }
        }
    }
    n = n + 1;
}
```

---

## The IDE

Run with:

```bash
python Ide.py
```

| Feature | Description |
|---|---|
| Syntax highlighting | Keywords, strings, numbers, operators, comments |
| Dark / light theme | Toggle with `Ctrl+T`, preference saved between sessions |
| Error highlighting | Failing lines marked in red with line-specific messages |
| Examples gallery | 6 built-in programs (`Ctrl+E`) |
| Console / LLVM IR tabs | View program output or the generated IR side by side |
| File management | New, Open, Save, Recent Files |
| Find | `Ctrl+F` |
| Font zoom | `Ctrl+` / `Ctrl-` |

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` | Run |
| `Ctrl+S` | Save |
| `Ctrl+O` | Open |
| `Ctrl+N` | New |
| `Ctrl+F` | Find |
| `Ctrl+E` | Examples gallery |
| `Ctrl+T` | Toggle theme |

---

## How It Works

```
source.nova
    │
    ▼
 Lexer (rply)         — tokenizes the source text
    │
    ▼
 Parser (rply)         — builds AST nodes per grammar rules
    │
    ▼
 AST nodes (.eval())   — each node emits LLVM IR via llvmlite
    │
    ▼
 CodeGen               — wraps IR in an LLVM module, verifies it
    │
    ▼
 output.ll             — LLVM IR, ready for JIT or llc/clang
```

### Why deferred evaluation matters

AST nodes store their children as unevaluated objects rather than calling `.eval()` immediately. This means a `while` loop can position the LLVM builder inside the correct basic block (`while_header`, `while_body`, `while_exit`) *before* evaluating the condition or body — which is what makes loops behave correctly instead of running forever or emitting IR in the wrong place.

### What is LLVM?

LLVM is a compiler backend toolkit. Instead of writing a custom machine-code generator, NovaLang compiles to LLVM's intermediate representation (IR) — the same IR used by Clang/C++, Rust, and Swift — and lets LLVM (or `llvmlite`'s JIT) handle the rest.

---

## Known Limitations

- No user-defined functions yet
- No arrays
- Single-file programs only (no imports/modules)
- One statement per top-level chunk in `main.py`'s parser loop

---

## Roadmap

| Feature | Difficulty |
|---|---|
| `for` loop | Easy |
| `return` statement | Easy |
| User-defined functions | Medium |
| Arrays | Medium |
| Type inference | Hard |
| Standard library | Hard |

---

## License

See `LICENSE`.
