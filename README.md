<div align="center">

# ⬡ NovaLang

**A compiled programming language with its own lexer, parser, AST, and LLVM IR backend — written entirely in Python.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![LLVM](https://img.shields.io/badge/LLVM-IR-orange?logo=llvm&logoColor=white)](https://llvm.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![rply](https://img.shields.io/badge/rply-lexer%2Fparser-purple)](https://github.com/alex/rply)
[![llvmlite](https://img.shields.io/badge/llvmlite-codegen-yellow)](https://github.com/numba/llvmlite)

NovaLang compiles `.nova` source files down to **LLVM IR** — the same intermediate representation used by Clang/C++, Rust, and Swift. Programs run instantly via JIT or compile to a native executable.

</div>

---

## 📑 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Language Reference](#-language-reference)
- [The IDE](#-the-ide)
- [How It Works](#-how-it-works)
- [Known Limitations](#-known-limitations)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- 🔢 **Data types** — integer, float, boolean, string
- ➕ **Arithmetic** — `+ - * / %` and unary minus
- 🔍 **Comparison** — `== != > < >= <=`
- 🔗 **Logical operators** — `&& || !`
- 🔁 **Control flow** — `if`, `if / else`, `while` loops
- 🖨️ **I/O** — `print()` for all supported types
- 💬 **Comments** — `// single-line` and `/* multi-line */`
- ♻️ **Variable re-assignment**
- ⚡ **JIT execution** — run programs instantly, no separate LLVM install required
- 🖥️ **GUI IDE** — dark/light themed editor with syntax highlighting, error markers, and an examples gallery

---

## 📁 Project Structure

```
NovaLang/
├── lexer.py         # Tokenizer (rply)
├── nova_parser.py   # Grammar + AST builder (rply)
├── nova_ast.py       # AST nodes — emit LLVM IR via .eval()
├── codegen.py        # LLVM module setup (llvmlite)
├── main.py           # CLI compiler entry point
├── Ide.py            # GUI IDE (tkinter)
├── input.nova        # Sample program
└── README.md
```

| File | Role | Description |
|---|---|---|
| `lexer.py` | Tokenizer | Converts source text into a token stream |
| `nova_parser.py` | Grammar + AST | Defines grammar rules, builds AST node objects |
| `nova_ast.py` | IR Emitter | Each AST node class emits LLVM IR via `.eval()` |
| `codegen.py` | LLVM Module | Sets up the module, declares `printf`, verifies & saves IR |
| `main.py` | CLI Compiler | Drives lexer → parser → eval, handles `--run` and errors |
| `Ide.py` | GUI IDE | Full tkinter IDE — editor, console, syntax highlighting |

---

## 📦 Requirements

```bash
pip install rply llvmlite
```

<details>
<summary><b>Optional — native <code>.exe</code> compilation</b></summary>
<br>

You don't need these to run NovaLang — `--run` JIT-executes programs directly in Python. They're only needed if you want to compile to a standalone native executable:

| Tool | Purpose |
|---|---|
| [LLVM](https://github.com/llvm/llvm-project/releases) (`clang`, `llc`) | Compile IR to native assembly/executables |
| Visual Studio Build Tools (Windows) | Provides `libcmt.lib` / `kernel32.lib` for the linker |

</details>

---

## 🚀 Quick Start

```bash
git clone https://github.com/<your-username>/NovaLang.git
cd NovaLang
pip install rply llvmlite

# Compile and run instantly
python main.py input.nova --run
```

---

## 🛠 Usage

```bash
# Compile and run with JIT (recommended)
python main.py input.nova --run

# Compile only (writes LLVM IR to a file)
python main.py input.nova -o output.ll

# Use a custom source file
python main.py myprogram.nova --run

# Launch the GUI IDE
python Ide.py
```

### CLI Flags

| Flag | Description |
|---|---|
| `source` | Path to `.nova` file (default: `input.nova`) |
| `-o, --output` | Output `.ll` file path (default: `output.ll`) |
| `--run` | JIT-execute the program immediately after compiling |
| `-q, --quiet` | Suppress banner and info messages |

---

## 📖 Language Reference

<details>
<summary><b>Types</b></summary>
<br>

```nova
42          // integer
3.14        // float
true        // boolean
false       // boolean
"hello"     // string
```
</details>

<details>
<summary><b>Variables</b></summary>
<br>

```nova
x = 10;
x = x + 1;   // re-assignment supported
```
</details>

<details>
<summary><b>Operators</b></summary>
<br>

| Category | Operators |
|---|---|
| Arithmetic | `+` `-` `*` `/` `%` |
| Unary | `-x` |
| Comparison | `==` `!=` `>` `<` `>=` `<=` |
| Logical | `&&` `\|\|` `!` |
</details>

<details>
<summary><b>Control Flow</b></summary>
<br>

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

// while loop
i = 1;
while (i < 5) {
    print(i);
    i = i + 1;
}
```
</details>

<details>
<summary><b>Example — FizzBuzz</b></summary>
<br>

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
</details>

---

## 🖥 The IDE

```bash
python Ide.py
```

| Feature | Description |
|---|---|
| Syntax highlighting | Keywords, strings, numbers, operators, comments |
| Dark / light theme | `Ctrl+T` — preference saved between sessions |
| Error highlighting | Failing lines marked in red with messages |
| Examples gallery | 6 built-in programs — `Ctrl+E` |
| Console / LLVM IR tabs | View output or generated IR side by side |
| File management | New, Open, Save, Recent Files |

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

## ⚙️ How It Works

```
source.nova
    │
    ▼
 Lexer (rply)         tokenizes the source text
    │
    ▼
 Parser (rply)        builds AST nodes per grammar rules
    │
    ▼
 AST nodes (.eval())  each node emits LLVM IR via llvmlite
    │
    ▼
 CodeGen              wraps IR in an LLVM module, verifies it
    │
    ▼
 output.ll            LLVM IR — ready for JIT or llc/clang
```

<details>
<summary><b>Why deferred evaluation matters</b></summary>
<br>

AST nodes store their children as unevaluated objects rather than calling `.eval()` immediately. This lets a `while` loop position the LLVM builder inside the correct basic block (`while_header`, `while_body`, `while_exit`) *before* evaluating the condition or body — which is what makes loops behave correctly instead of running forever or emitting IR in the wrong place.
</details>

<details>
<summary><b>What is LLVM?</b></summary>
<br>

LLVM is a compiler backend toolkit. Instead of writing a custom machine-code generator, NovaLang compiles to LLVM's intermediate representation — the same IR used by Clang/C++, Rust, and Swift — and lets LLVM (or `llvmlite`'s JIT) handle the rest.
</details>

---

## ⚠️ Known Limitations

- No user-defined functions yet
- No arrays
- Single-file programs only (no imports/modules)

---

## 🗺 Roadmap

- [ ] `for` loop
- [ ] `return` statement
- [ ] User-defined functions
- [ ] Arrays
- [ ] Type inference
- [ ] Standard library

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---



---

<div align="center">

Made with 🐍 Python · ⚡ LLVM

</div>
