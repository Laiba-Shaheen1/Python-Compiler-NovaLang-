# NovaLang 🚀

A simple compiled language that targets **LLVM IR**, built in Python with `rply` and `llvmlite`.

---

## Project Structure

```
NovaLang/
├── main.py        ← Compiler entry point (CLI)
├── lexer.py       ← Tokenizer (rply)
├── parser.py      ← Grammar + AST builder (rply)
├── nova_ast.py    ← AST node classes (emit LLVM IR)
├── codegen.py     ← LLVM module / engine setup (llvmlite)
├── input.nova     ← Sample source file
└── output.ll      ← Generated LLVM IR (after compilation)
```

---

## Requirements

### Python packages
```bash
pip install rply llvmlite
```

### System tools (at least one needed to *run* the output)

| Tool | Purpose | Install |
|------|---------|---------|
| **LLVM / `lli`** | Run `.ll` IR directly | [llvm.org](https://llvm.org/releases/) or `choco install llvm` |
| **`llc`** | Compile IR → native assembly | Comes with LLVM |
| **GCC / Clang** | Link assembly → executable | MinGW on Windows |

> **VS Code** — install the *LLVM* extension for `.ll` syntax highlighting.  
> **Flex / Bison** — not needed; `rply` handles lexing + parsing entirely in Python.

---

## Usage

```bash
# Compile the default input.nova → output.ll
python main.py

# Compile a custom file
python main.py myprogram.nova

# Custom output path
python main.py myprogram.nova -o myprogram.ll

# Run the generated IR (requires LLVM lli)
lli output.ll

# Compile to a native executable (requires llc + gcc)
llc output.ll -o output.s
gcc output.s -o program
./program
```

---

## Language Reference

### Types
| Type | Example |
|------|---------|
| Integer (i32) | `42`, `-7` |
| Float (f32) | `3.14`, `-0.5` |
| Boolean | `true`, `false` |
| String | `"Hello!"` |

### Operators
| Category | Operators |
|----------|-----------|
| Arithmetic | `+  -  *  /  %` |
| Unary | `-expr` (negate) |
| Comparison | `==  !=  >  <  >=  <=` |
| Logical | `&&  \|\|  !` |

### Statements

```nova
// Variable assignment
x = 42;
name = "Nova";

// Print
print(x);
print("Hello, world!");

// If-else
if (x > 10) {
    print(1);
} else {
    print(0);
}

// If without else
if (x == 42) {
    print(x);
}

// While loop
i = 0;
while (i < 5) {
    print(i);
    i = i + 1;
}
```

### Comments
```nova
// Single-line comment
/* Multi-line
   comment */
```

---

## How It Works

```
source.nova
    │
    ▼
 Lexer (rply)         — tokenises the source text
    │
    ▼
 Parser (rply)        — builds AST nodes according to grammar rules
    │
    ▼
 AST nodes (.eval())  — each node emits LLVM IR via llvmlite
    │
    ▼
 CodeGen              — wraps everything in an LLVM module
    │
    ▼
 output.ll            — LLVM IR ready for lli / llc
```

---

## What Changed From the Original "Toy" Compiler

| Feature | Before | After (NovaLang) |
|---------|--------|-----------------|
| Name | toy | **NovaLang** |
| Source extension | `.toy` | `.nova` |
| Multiplication / Division | ✗ | ✅ `*` `/` |
| Modulo | ✗ | ✅ `%` |
| Float literals | ✗ | ✅ `3.14` |
| String literals | ✗ | ✅ `"hello"` |
| Boolean literals | ✗ | ✅ `true` / `false` |
| Logical operators | ✗ | ✅ `&& \|\| !` |
| `>=` / `<=` / `!=` | ✗ | ✅ |
| Unary minus | ✗ | ✅ `-expr` |
| `while` loop | ✗ | ✅ |
| `if` without `else` | ✗ | ✅ |
| Re-assignment | ✗ | ✅ |
| Multi-line comments | ✗ | ✅ `/* ... */` |
| CLI with `--output` flag | ✗ | ✅ |
| Nice error messages | ✗ | ✅ with line numbers |

---

## License
GNU General Public License v3 — see `LICENSE`.
