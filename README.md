NovaLang ⬡

A compiled programming language with its own lexer, parser, AST, and LLVM IR backend — written entirely in Python.

NovaLang compiles .nova source files down to LLVM IR, the same intermediate representation used by Clang/C++, Rust, and Swift. Programs can be run instantly via JIT or compiled to a native executable.


Table of Contents


Features
Project Structure
Requirements
Installation
Usage
Language Reference
The IDE
How It Works
Known Limitations
Roadmap
License



Features


Data types — integer, float, boolean, string
Arithmetic — + - * / % and unary minus
Comparison — == != > < >= <=
Logical operators — && || !
Control flow — if, if / else, while loops
I/O — print() for all supported types
Comments — // single-line and /* multi-line */
Variable re-assignment
JIT execution — run programs instantly, no separate LLVM install required
GUI IDE — dark/light themed editor with syntax highlighting, error line markers, and an examples gallery



Project Structure

FileRoleDescriptionlexer.pyTokenizerConverts source text into a token stream using rplynova_parser.pyGrammar + ASTDefines grammar rules and builds AST node objectsnova_ast.pyIR EmitterEach AST node class emits LLVM IR via .eval()codegen.pyLLVM ModuleSets up the LLVM module, declares printf, verifies and saves output.llmain.pyCLI CompilerDrives lexer → parser → eval, handles --run flag and errorsIde.pyGUI IDEFull tkinter IDE — editor, console, syntax highlighting, themesinput.novaSample programDefault source file compiled by main.py


Requirements

Python packages

bashpip install rply llvmlite

Optional (for native .exe compilation only)

ToolPurposeLLVM (clang, llc)Compile IR to native assembly/executablesVisual Studio Build Tools (Windows)Provides libcmt.lib / kernel32.lib needed by the linker


You do not need Flex, Bison, or any C/C++ toolchain to run NovaLang — rply handles lexing and parsing entirely in Python, and the --run flag JIT-executes programs directly.




Installation

bashgit clone <your-repo-url>
cd NovaLang
pip install rply llvmlite


Usage

Compile and run with JIT (recommended)

bashpython main.py input.nova --run

Compile only (writes LLVM IR to a file)

bashpython main.py input.nova -o output.ll

Use a custom source file

bashpython main.py myprogram.nova --run

Launch the GUI IDE

bashpython Ide.py

CLI options

FlagDescriptionsourcePath to .nova file (default: input.nova)-o, --outputOutput .ll file path (default: output.ll)--runJIT-execute the program immediately after compiling-q, --quietSuppress banner and info messages


Language Reference

Types

nova42          // integer
3.14        // float
true        // boolean
false       // boolean
"hello"     // string

Variables

novax = 10;
x = x + 1;   // re-assignment supported

Operators

CategoryOperatorsArithmetic+ - * / %Unary-xComparison== != > < >= <=Logical&& || !

Print

novaprint(42);
print(3.14);
print("Hello, NovaLang!");
print(true);

If / Else

novaif (x > 10) {
    print(1);
} else {
    print(0);
}

// if without else is also valid
if (x == 5) {
    print(x);
}

While Loop

novai = 1;
while (i < 5) {
    print(i);
    i = i + 1;
}

Comments

nova// single-line comment
/* multi-line
   comment */

Example — FizzBuzz

novan = 1;
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


The IDE

Run with:

bashpython Ide.py

FeatureDescriptionSyntax highlightingKeywords, strings, numbers, operators, commentsDark / light themeToggle with Ctrl+T, preference saved between sessionsError highlightingFailing lines marked in red with line-specific messagesExamples gallery6 built-in programs (Ctrl+E)Console / LLVM IR tabsView program output or the generated IR side by sideFile managementNew, Open, Save, Recent FilesFindCtrl+FFont zoomCtrl+ / Ctrl-

Keyboard Shortcuts

ShortcutActionCtrl+EnterRunCtrl+SSaveCtrl+OOpenCtrl+NNewCtrl+FFindCtrl+EExamples galleryCtrl+TToggle theme


How It Works

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

Why deferred evaluation matters

AST nodes store their children as unevaluated objects rather than calling .eval() immediately. This means a while loop can position the LLVM builder inside the correct basic block (while_header, while_body, while_exit) before evaluating the condition or body — which is what makes loops behave correctly instead of running forever or emitting IR in the wrong place.

What is LLVM?

LLVM is a compiler backend toolkit. Instead of writing a custom machine-code generator, NovaLang compiles to LLVM's intermediate representation (IR) — the same IR used by Clang/C++, Rust, and Swift — and lets LLVM (or llvmlite's JIT) handle the rest.






Roadmap

FeatureDifficultyfor loopEasyreturn statementEasyUser-defined functionsMediumArraysMediumType inferenceHardStandard libraryHard
