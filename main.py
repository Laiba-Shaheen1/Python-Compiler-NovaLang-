"""
NovaLang Compiler — main entry point
Usage:
    python main.py                        # compile input.nova
    python main.py myfile.nova            # compile custom file
    python main.py myfile.nova -o out.ll  # custom output
    python main.py myfile.nova --run      # compile AND run via JIT
"""

import sys
import os
import re
import ctypes
import argparse

from lexer       import Lexer
from nova_parser import NovaParser
from codegen     import CodeGen

BANNER = r"""
  _   _                   _
 | \ | | _____   ____ _  | |    __ _ _ __   __ _
 |  \| |/ _ \ \ / / _` | | |   / _` | '_ \ / _` |
 | |\  | (_) \ V / (_| | | |__| (_| | | | | (_| |
 |_| \_|\___/ \_/ \__,_| |_____\__,_|_| |_|\__, |
                                             |___/
 NovaLang Compiler v1.0  —  LLVM-backed toy language
"""


def parse_args():
    ap = argparse.ArgumentParser(
        prog="novalang",
        description="NovaLang — a simple compiled language targeting LLVM IR"
    )
    ap.add_argument("source", nargs="?", default="input.nova",
                    help="Source file to compile (default: input.nova)")
    ap.add_argument("-o", "--output", default="output.ll",
                    help="Output LLVM IR file (default: output.ll)")
    ap.add_argument("--run", action="store_true",
                    help="JIT-execute the program after compiling")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="Suppress banner and info messages")
    return ap.parse_args()


def strip_comments(source: str) -> str:
    source = re.sub(r'//[^\n]*', '', source)
    source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
    return source


def split_statements(source: str) -> list:
    source = strip_comments(source)
    statements = []
    current    = []
    depth      = 0
    i          = 0
    n          = len(source)

    while i < n:
        ch = source[i]
        if ch == '{':
            depth += 1
            current.append(ch)
        elif ch == '}':
            depth -= 1
            current.append(ch)
            if depth == 0:
                j = i + 1
                while j < n and source[j] in ' \t\n\r':
                    j += 1
                rest  = source[j:j+4]
                after = source[j+4] if j + 4 < n else ''
                if rest == 'else' and (after == '' or not (after.isalnum() or after == '_')):
                    pass
                else:
                    stmt = ''.join(current).strip()
                    if stmt:
                        statements.append(stmt)
                    current = []
        elif ch == ';' and depth == 0:
            current.append(ch)
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
        else:
            current.append(ch)
        i += 1

    leftover = ''.join(current).strip()
    if leftover:
        statements.append(leftover)
    return statements


def jit_run(ir_string: str):
    """Execute compiled LLVM IR using llvmlite's built-in JIT engine."""
    from llvmlite import binding

    # Register ALL targets (fixes "no targets are registered" on newer llvmlite)
    binding.initialize_all_targets()
    binding.initialize_all_asmprinters()

    # Load C runtime so printf works on Windows
    if sys.platform == "win32":
        ctypes.CDLL("msvcrt.dll", mode=ctypes.RTLD_GLOBAL)
    else:
        ctypes.CDLL(None, mode=ctypes.RTLD_GLOBAL)

    triple  = binding.get_default_triple()
    target  = binding.Target.from_triple(triple)
    machine = target.create_target_machine()

    mod = binding.parse_assembly(ir_string)
    mod.verify()

    engine = binding.create_mcjit_compiler(mod, machine)
    engine.finalize_object()
    engine.run_static_constructors()

    main_ptr = engine.get_function_address("main")
    cfunc    = ctypes.CFUNCTYPE(None)(main_ptr)
    cfunc()


def compile_file(source_path: str, output_path: str,
                 run: bool = False, quiet: bool = False):
    if not quiet:
        print(BANNER)

    if not os.path.exists(source_path):
        print(f"[NovaLang] Error: source file '{source_path}' not found.")
        sys.exit(1)

    with open(source_path, encoding="utf-8") as f:
        source = f.read()

    if not quiet:
        print(f"[NovaLang] Compiling: {source_path}")

    lexer   = Lexer().get_lexer()
    codegen = CodeGen()

    pg = NovaParser(codegen.module, codegen.builder, codegen.printf)
    pg.parse()
    parser = pg.get_parser()

    statements = split_statements(source)

    errors = []
    for stmt in statements:
        stripped = stmt.strip()
        if not stripped:
            continue
        try:
            tokens = lexer.lex(stripped)
            result = parser.parse(tokens)
            if result is not None:
                result.eval()
        except (SyntaxError, ValueError, NameError) as e:
            errors.append((stripped[:80], str(e)))

    if errors:
        print("\n[NovaLang] Compilation failed with errors:\n")
        for src, msg in errors:
            print(f"  >> {src}")
            print(f"     ^ {msg}\n")
        sys.exit(1)

    codegen.create_ir()
    codegen.save_ir(output_path)

    if not quiet:
        print(f"[NovaLang] Success!  LLVM IR written to '{output_path}'")

    if run:
        if not quiet:
            print(f"\n[NovaLang] Running via JIT...\n{'─'*40}")
        jit_run(str(codegen.module))
        if not quiet:
            print(f"{'─'*40}\n[NovaLang] Done.")
    else:
        if not quiet:
            print(f"\n  Run with:  python main.py {source_path} --run\n")


if __name__ == "__main__":
    args = parse_args()
    compile_file(args.source, args.output, args.run, args.quiet)