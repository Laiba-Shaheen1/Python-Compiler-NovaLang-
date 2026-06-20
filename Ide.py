"""
NovaLang IDE — responsive GUI editor with dark/light themes.
Run with:  python Ide.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import sys
import os
import io
import re
import ctypes
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer       import Lexer
from nova_parser import NovaParser
from codegen     import CodeGen

FONT_FAMILY = "Segoe UI"
MONO        = "Consolas"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ide_config.json")

THEMES = {
    "dark": {
        "bg": "#0d1117", "bg2": "#161b22", "bg3": "#21262d", "border": "#30363d",
        "fg": "#e6edf3", "fg2": "#8b949e",
        "accent": "#58a6ff", "accent2": "#1f6feb",
        "green": "#3fb950", "red": "#f85149", "yellow": "#d29922",
        "purple": "#bc8cff", "orange": "#ffa657", "cyan": "#39d0d8",
        "current_line": "#21262d", "error_line": "#3d1515", "error_gutter": "#f85149",
        "status_fg": "white",
    },
    "light": {
        "bg": "#ffffff", "bg2": "#f6f8fa", "bg3": "#eaeef2", "border": "#d0d7de",
        "fg": "#1f2328", "fg2": "#656d76",
        "accent": "#0969da", "accent2": "#0550ae",
        "green": "#1a7f37", "red": "#cf222e", "yellow": "#9a6700",
        "purple": "#8250df", "orange": "#bc4c00", "cyan": "#0550ae",
        "current_line": "#f0f6ff", "error_line": "#ffebe9", "error_gutter": "#cf222e",
        "status_fg": "white",
    },
}

KW_KEYWORDS  = r'\b(if|else|while|print|true|false)\b'
KW_NUMBERS   = r'\b\d+(\.\d+)?\b'
KW_STRINGS   = r'"[^"]*"'
KW_COMMENTS  = r'//[^\n]*|/\*.*?\*/'
KW_OPERATORS = r'[+\-*/%=<>!&|]+'

HELP_TEXT = """NovaLang Quick Reference
─────────────────────────

Types: int, float, bool, string
  42   3.14   true/false   "hello"

Variables & print:
  x = 10;
  print(x);
  print("Hello!");

If / else:
  if (x > 0) { print(1); }
  else { print(0); }

While loop:
  i = 0;
  while (i < 5) {
      print(i);
      i = i + 1;
  }

Operators:
  + - * / %   == != > < >= <=
  && || !

Shortcuts:
  Ctrl+Enter  Run
  Ctrl+S      Save
  Ctrl+O      Open
  Ctrl+F      Find
  Ctrl+T      Toggle theme
"""

EXAMPLES = [
    {
        "title": "Getting Started",
        "desc": "Variables, arithmetic, strings, if-else, and a while loop.",
        "code": """// Welcome to NovaLang!
x = 10;
y = 3;

print(x + y);
print(x * y);
print("Hello, NovaLang!");

if (x > y) {
    print(1);
} else {
    print(0);
}

i = 1;
while (i < 4) {
    print(i);
    i = i + 1;
}
""",
    },
    {
        "title": "Full Language Tour",
        "desc": "All features: floats, booleans, comparisons, logic, loops.",
        "code": """// Integer arithmetic
a = 5;
b = 10;
print(a + b);
print(a * b);
print(b % 3);

// Floating-point
x = 3.14;
print(x);

// Unary minus
neg = -7;
print(neg);

print("Hello, NovaLang!");
flag = true;
print(flag);

if (a < b) {
    print(a);
} else {
    print(b);
}

if (a == 5) {
    print(a);
}

if (a < b && b == 10) {
    print(1);
}

i = 1;
while (i < 4) {
    print(i);
    i = i + 1;
}
""",
    },
    {
        "title": "FizzBuzz",
        "desc": "Classic 1–15 FizzBuzz using modulo and conditionals.",
        "code": """n = 1;
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
""",
    },
    {
        "title": "Sum 1 to N",
        "desc": "Accumulate a total with a while loop.",
        "code": """n = 10;
sum = 0;
i = 1;

while (i <= n) {
    sum = sum + i;
    i = i + 1;
}

print(sum);
""",
    },
    {
        "title": "Comparison Demo",
        "desc": "All comparison and logical operators.",
        "code": """a = 7;
b = 12;

print(a == b);
print(a != b);
print(a < b);
print(a > b);
print(a <= 7);
print(b >= 12);

if (a < b && b > 0) {
    print(1);
}

if (a > 20 || b == 12) {
    print(1);
}

if (!false) {
    print(1);
}
""",
    },
    {
        "title": "Intentional Errors",
        "desc": "Demo error highlighting — try running this!",
        "code": """// This example has deliberate errors for testing.

x = 10;
print(x);

// Undefined variable below:
print(undefined_var);

// Syntax error below:
if (x > 0 {
    print(1);
}
""",
    },
]

SNIPPETS = {
    "Hello World": 'print("Hello, NovaLang!");',
    "Variables":   "x = 10;\ny = 3;\nprint(x + y);",
    "If-Else":     "if (x > 0) {\n    print(1);\n} else {\n    print(0);\n}",
    "While Loop":  "i = 0;\nwhile (i < 5) {\n    print(i);\n    i = i + 1;\n}",
    "Arithmetic":  "a = 10;\nb = 3;\nprint(a + b);\nprint(a * b);\nprint(a % b);",
}


class ToolTip:
    def __init__(self, widget, text, get_colors):
        self.widget = widget
        self.text = text
        self.get_colors = get_colors
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None):
        if self.tip:
            return
        c = self.get_colors()
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, bg=c["bg3"], fg=c["fg"],
                 font=(FONT_FAMILY, 9), padx=8, pady=4,
                 relief=tk.SOLID, bd=1).pack()

    def _hide(self, _event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


def strip_comments(source):
    source = re.sub(r'//[^\n]*', '', source)
    source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
    return source


def split_statements(source):
    source = strip_comments(source)
    statements, current, depth = [], [], 0
    i, n = 0, len(source)
    while i < n:
        ch = source[i]
        if ch == '{':
            depth += 1; current.append(ch)
        elif ch == '}':
            depth -= 1; current.append(ch)
            if depth == 0:
                j = i + 1
                while j < n and source[j] in ' \t\n\r': j += 1
                rest  = source[j:j+4]
                after = source[j+4] if j+4 < n else ''
                if rest == 'else' and (after == '' or not (after.isalnum() or after == '_')):
                    pass
                else:
                    stmt = ''.join(current).strip()
                    if stmt: statements.append(stmt)
                    current = []
        elif ch == ';' and depth == 0:
            current.append(ch)
            stmt = ''.join(current).strip()
            if stmt: statements.append(stmt)
            current = []
        else:
            current.append(ch)
        i += 1
    leftover = ''.join(current).strip()
    if leftover: statements.append(leftover)
    return statements


def map_statement_lines(source, statements):
    """Map each statement to its 1-based start line in the original source."""
    pos = 0
    mapped = []
    for stmt in statements:
        m = re.search(r'\S+', stmt)
        if not m:
            mapped.append((stmt, 1))
            continue
        needle = m.group()
        idx = source.find(needle, pos)
        if idx == -1:
            line = 1
        else:
            line = source[:idx].count('\n') + 1
            pos = idx + len(needle)
        mapped.append((stmt, line))
    return mapped


def compile_source(source: str) -> tuple[str, bool, str, list[int]]:
    """Returns (output_text, success, llvm_ir, error_line_numbers)."""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        lexer   = Lexer().get_lexer()
        codegen = CodeGen()
        pg      = NovaParser(codegen.module, codegen.builder, codegen.printf)
        pg.parse()
        parser = pg.get_parser()

        statements = split_statements(source)
        stmt_lines = map_statement_lines(source, statements)
        errors = []
        error_lines = []

        for (stmt, line_no) in stmt_lines:
            stripped = stmt.strip()
            if not stripped:
                continue
            try:
                tokens = lexer.lex(stripped)
                result = parser.parse(tokens)
                if result is not None:
                    result.eval()
            except (SyntaxError, ValueError, NameError) as e:
                msg = str(e).replace("[NovaLang] ", "")
                errors.append((line_no, msg))
                error_lines.append(line_no)

        if errors:
            sys.stdout = old_stdout
            text = "\n".join(f"  Line {ln}: {msg}" for ln, msg in errors)
            return text, False, "", error_lines

        codegen.create_ir()
        ir_string = str(codegen.module)
        sys.stdout = old_stdout

        import tempfile, subprocess
        with tempfile.NamedTemporaryFile(suffix='.ll', delete=False, mode='w') as f:
            f.write(ir_string)
            tmp_ll = f.name

        result_proc = subprocess.run(
            [sys.executable, "-c", f"""
import sys, ctypes
sys.path.insert(0, r'{os.path.dirname(os.path.abspath(__file__))}')
from llvmlite import binding
binding.initialize_all_targets()
binding.initialize_all_asmprinters()
if sys.platform == 'win32':
    ctypes.CDLL('msvcrt.dll', mode=ctypes.RTLD_GLOBAL)
else:
    ctypes.CDLL(None, mode=ctypes.RTLD_GLOBAL)
with open(r'{tmp_ll}') as f:
    ir_str = f.read()
triple  = binding.get_default_triple()
target  = binding.Target.from_triple(triple)
machine = target.create_target_machine()
mod     = binding.parse_assembly(ir_str)
mod.verify()
engine  = binding.create_mcjit_compiler(mod, machine)
engine.finalize_object()
engine.run_static_constructors()
main_ptr = engine.get_function_address('main')
cfunc = ctypes.CFUNCTYPE(None)(main_ptr)
cfunc()
"""],
            capture_output=True, text=True, timeout=10
        )
        os.unlink(tmp_ll)

        output = result_proc.stdout
        if result_proc.returncode != 0:
            err = result_proc.stderr.strip()
            return f"Runtime error:\n{err}", False, ir_string, []
        return output if output else "(no output)", True, ir_string, []

    except Exception as e:
        sys.stdout = old_stdout
        return f"{type(e).__name__}: {e}", False, "", []
    finally:
        sys.stdout = old_stdout


class NovaIDE(tk.Tk):
    RESPONSIVE_BREAK = 920
    DEFAULT_FONT_SIZE = 13

    def __init__(self):
        super().__init__()
        self.title("NovaLang IDE")
        self.geometry("1200x760")
        self.minsize(640, 480)

        self._current_file = None
        self._modified = False
        self._font_size = self.DEFAULT_FONT_SIZE
        self._last_ir = ""
        self._console_text = ""
        self._pane_orient = "horizontal"
        self._help_visible = False
        self._recent_files = []
        self._reflowing = False
        self._error_lines = []
        self._theme_name = self._load_theme_pref()
        self._c = THEMES[self._theme_name]
        self._menus = []

        self.configure(bg=self._c["bg"])
        self._build_menu()
        self._build_header()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()
        self._bind_shortcuts()
        self._apply_theme()
        self._load_default()

        self.bind("<Configure>", self._on_resize)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _colors(self):
        return self._c

    def _load_theme_pref(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("theme") in THEMES:
                    return data["theme"]
        except (OSError, json.JSONDecodeError):
            pass
        return "dark"

    def _save_theme_pref(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"theme": self._theme_name}, f)
        except OSError:
            pass

    # ── theme ─────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        self._c = THEMES[self._theme_name]
        self._apply_theme()
        self._save_theme_pref()
        label = "Light" if self._theme_name == "light" else "Dark"
        self._status_var.set(f"{label} theme applied")

    def _apply_theme(self):
        c = self._c
        self.configure(bg=c["bg"])

        for frame in (self._body, self._center, self._help_frame,
                      self._editor_panel, self._output_panel, self._editor_frame):
            if frame:
                frame.configure(bg=c["bg"])
        for frame in (self._header, self._toolbar, self._toolbar_row,
                      getattr(self, "_editor_hdr", None),
                      getattr(self, "_output_hdr", None)):
            if frame:
                frame.configure(bg=c["bg2"])
        self._statusbar.configure(bg=c["accent2"])
        self._shortcut_label.configure(bg=c["bg3"], fg=c["fg2"])
        self._vsb.configure(bg=c["bg3"], troughcolor=c["bg2"], activebackground=c["border"])
        self._hsb.configure(bg=c["bg3"], troughcolor=c["bg2"], activebackground=c["border"])

        for b in self._toolbar_btns:
            if b is self._run_btn:
                b.configure(fg=c["bg"], bg=c["green"], activebackground=c["green"])
            elif b is not self._theme_btn:
                b.configure(fg=c["fg"], bg=c["bg3"], activebackground=c["bg3"],
                            highlightbackground=c["border"])
            else:
                b.configure(fg=c["fg"], bg=c["bg3"], highlightbackground=c["border"])
        for lbl in (self._status_lbl, self._cursor_lbl):
            lbl.configure(bg=c["accent2"], fg=c["status_fg"])

        for w in self._themed_labels:
            w.configure(bg=c[w._theme_bg_key], fg=c[w._theme_fg_key])

        self._line_nums.configure(bg=c["bg2"], fg=c["fg2"], selectbackground=c["bg2"])
        self._editor.configure(bg=c["bg"], fg=c["fg"],
                               insertbackground=c["accent"],
                               selectbackground=c["accent2"])
        self._output.configure(bg=c["bg"], fg=c["fg"], selectbackground=c["accent2"])
        self._help_text.configure(bg=c["bg2"], fg=c["fg2"])

        self._editor.tag_config("keyword",  foreground=c["purple"])
        self._editor.tag_config("number",   foreground=c["orange"])
        self._editor.tag_config("string",   foreground=c["green"])
        self._editor.tag_config("comment",  foreground=c["fg2"])
        self._editor.tag_config("operator", foreground=c["cyan"])
        self._editor.tag_config("current_line", background=c["current_line"])
        self._editor.tag_config("error_line", background=c["error_line"],
                                 foreground=c["red"])

        self._line_nums.tag_config("error_gutter", foreground=c["error_gutter"],
                                   background=c["error_line"])

        self._output.tag_config("success", foreground=c["green"])
        self._output.tag_config("error",   foreground=c["red"])
        self._output.tag_config("info",    foreground=c["accent"])
        self._output.tag_config("dim",     foreground=c["fg2"])

        self._tab_console.configure(bg=c["bg2"],
            fg=c["accent"] if self._active_tab == "console" else c["fg2"])
        self._tab_ir.configure(bg=c["bg2"],
            fg=c["accent"] if self._active_tab == "ir" else c["fg2"])
        self._status_dot.configure(bg=c["bg2"], fg=c["fg2"])

        for menu in self._menus:
            menu.configure(bg=c["bg2"], fg=c["fg"],
                           activebackground=c["accent2"], activeforeground="white")

        if self._theme_btn:
            icon = "☀️ Light" if self._theme_name == "dark" else "🌙 Dark"
            self._theme_btn.configure(text=icon)

        self._highlight_all()
        self._highlight_current_line()
        if self._error_lines:
            self._highlight_error_lines(self._error_lines)

    def _themed_label(self, parent, bg_key, fg_key, **kwargs):
        c = self._c
        lbl = tk.Label(parent, bg=c[bg_key], fg=c[fg_key], **kwargs)
        lbl._theme_bg_key = bg_key
        lbl._theme_fg_key = fg_key
        self._themed_labels.append(lbl)
        return lbl

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_menu(self):
        self._menus = []
        menubar = tk.Menu(self, tearoff=0)
        self._menus.append(menubar)

        def sub():
            m = tk.Menu(menubar, tearoff=0)
            self._menus.append(m)
            return m

        file_m = sub()
        file_m.add_command(label="New",          command=self._new,        accelerator="Ctrl+N")
        file_m.add_command(label="Open...",      command=self._open,       accelerator="Ctrl+O")
        file_m.add_command(label="Save",         command=self._save,       accelerator="Ctrl+S")
        file_m.add_command(label="Save As...",   command=self._save_as)
        file_m.add_separator()
        file_m.add_command(label="Examples Gallery...", command=self._show_examples, accelerator="Ctrl+E")
        file_m.add_separator()
        self._recent_menu = sub()
        file_m.add_cascade(label="Recent Files", menu=self._recent_menu)
        self._update_recent_menu()
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_m)

        edit_m = sub()
        edit_m.add_command(label="Undo",         command=lambda: self._editor.edit_undo())
        edit_m.add_command(label="Redo",         command=lambda: self._editor.edit_redo())
        edit_m.add_separator()
        edit_m.add_command(label="Find...",      command=self._find,       accelerator="Ctrl+F")
        edit_m.add_command(label="Select All",   command=self._select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Edit", menu=edit_m)

        view_m = sub()
        view_m.add_command(label="Toggle Theme", command=self._toggle_theme, accelerator="Ctrl+T")
        view_m.add_command(label="Examples Gallery...", command=self._show_examples)
        view_m.add_command(label="Toggle Reference Panel", command=self._toggle_help)
        menubar.add_cascade(label="View", menu=view_m)

        run_m = sub()
        run_m.add_command(label="Run",           command=self._run,        accelerator="Ctrl+Enter")
        run_m.add_command(label="Clear Output",  command=self._clear_output)
        run_m.add_command(label="Export LLVM IR...", command=self._export_ir)
        menubar.add_cascade(label="Run", menu=run_m)

        insert_m = sub()
        for name, code in SNIPPETS.items():
            insert_m.add_command(label=name, command=lambda c=code: self._insert_snippet(c))
        menubar.add_cascade(label="Insert", menu=insert_m)

        help_m = sub()
        help_m.add_command(label="About NovaLang", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_m)

        self.config(menu=menubar)

    def _build_header(self):
        self._themed_labels = []
        self._header = tk.Frame(self, height=46, bg=self._c["bg2"])
        self._header.pack(fill=tk.X, side=tk.TOP)
        self._header.pack_propagate(False)

        self._themed_label(self._header, "bg2", "accent",
                           text="⬡ NovaLang", font=(MONO, 15, "bold"), padx=16
                           ).pack(side=tk.LEFT, pady=8)

        self._themed_label(self._header, "bg2", "fg2",
                           text="IDE  v2.1", font=(FONT_FAMILY, 10)
                           ).pack(side=tk.LEFT, pady=12)

        self._title_var = tk.StringVar(value="untitled.nova")
        self._themed_label(self._header, "bg2", "fg2",
                           textvariable=self._title_var, font=(MONO, 10)
                           ).pack(side=tk.RIGHT, padx=16)

    def _build_toolbar(self):
        self._toolbar = tk.Frame(self)
        self._toolbar.pack(fill=tk.X, side=tk.TOP)

        row = tk.Frame(self._toolbar, bg=self._c["bg3"])
        row.pack(fill=tk.X, padx=8, pady=6)
        self._toolbar_row = row
        self._toolbar.configure(bg=self._c["bg3"])

        self._toolbar_btns = []
        self._theme_btn = None

        specs = [
            ("📄 New",    self._new,           "btn",   "New file (Ctrl+N)"),
            ("📂 Open",   self._open,          "btn",   "Open file (Ctrl+O)"),
            ("💾 Save",   self._save,          "btn",   "Save file (Ctrl+S)"),
            ("▶ Run",     self._run,           "run",   "Compile & run (Ctrl+Enter)"),
            ("📚 Examples", self._show_examples, "btn",   "Open examples gallery (Ctrl+E)"),
            ("🗑 Clear",  self._clear_output,  "btn",   "Clear output panel"),
            ("📋 Copy",   self._copy_output,   "btn",   "Copy console output"),
            ("📤 IR",     self._export_ir,     "btn",   "Export LLVM IR to file"),
            ("📖 Help",   self._toggle_help,   "btn",   "Toggle reference panel"),
            ("☀️ Light",  self._toggle_theme,  "btn",   "Toggle dark/light theme (Ctrl+T)"),
        ]

        for text, cmd, kind, tip in specs:
            c = self._c
            if kind == "run":
                fg, bg = c["bg"], c["green"]
            else:
                fg, bg = c["fg"], c["bg3"]
            b = tk.Button(row, text=text, command=cmd,
                          font=(FONT_FAMILY, 10, "bold"),
                          fg=fg, bg=bg, activebackground=bg,
                          activeforeground=fg, relief=tk.FLAT,
                          cursor="hand2", padx=12, pady=5, bd=0)
            if kind != "run":
                b.config(highlightthickness=1, highlightbackground=c["border"])
            b.pack(side=tk.LEFT, padx=3)
            ToolTip(b, tip, self._colors)
            self._toolbar_btns.append(b)
            if kind == "run":
                self._run_btn = b
            if cmd == self._toggle_theme:
                self._theme_btn = b

        self._shortcut_label = tk.Label(row,
            text="Ctrl+Enter · Ctrl+S · Ctrl+E · Ctrl+T",
            font=(FONT_FAMILY, 9), fg=self._c["fg2"], bg=self._c["bg3"])
        self._shortcut_label.pack(side=tk.RIGHT, padx=8)

    def _build_body(self):
        self._body = tk.Frame(self)
        self._body.pack(fill=tk.BOTH, expand=True)

        self._help_frame = tk.Frame(self._body, width=220)
        self._help_text = tk.Text(self._help_frame, font=(MONO, 10),
                                  relief=tk.FLAT, bd=0,
                                  wrap=tk.WORD, padx=12, pady=12,
                                  state=tk.DISABLED, cursor="arrow")
        self._help_text.pack(fill=tk.BOTH, expand=True)
        self._help_text.config(state=tk.NORMAL)
        self._help_text.insert("1.0", HELP_TEXT)
        self._help_text.config(state=tk.DISABLED)

        self._center = tk.Frame(self._body)
        self._center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._pane = tk.PanedWindow(self._center, orient=tk.HORIZONTAL,
                                    sashwidth=5, sashrelief=tk.FLAT, bd=0,
                                    opaqueresize=True)
        self._pane.pack(fill=tk.BOTH, expand=True)

        self._editor_panel = self._make_editor_panel()
        self._output_panel = self._make_output_panel()
        self._pane.add(self._editor_panel, minsize=280)
        self._pane.add(self._output_panel, minsize=220)

    def _make_editor_panel(self):
        panel = tk.Frame(self._pane)

        hdr = tk.Frame(panel, height=32, bg=self._c["bg2"])
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        self._editor_hdr = hdr
        self._themed_label(hdr, "bg2", "fg2", text="  Editor",
                           font=(FONT_FAMILY, 9, "bold")).pack(side=tk.LEFT, pady=8)

        self._line_count_var = tk.StringVar(value="0 lines")
        self._themed_label(hdr, "bg2", "fg2", textvariable=self._line_count_var,
                           font=(FONT_FAMILY, 9)).pack(side=tk.RIGHT, padx=12)

        editor_frame = tk.Frame(panel, bg=self._c["bg"])
        editor_frame.pack(fill=tk.BOTH, expand=True)
        self._editor_frame = editor_frame

        self._line_nums = tk.Text(editor_frame, width=4,
                                  font=(MONO, self._font_size),
                                  relief=tk.FLAT, bd=0,
                                  state=tk.DISABLED, cursor="arrow", padx=6)
        self._line_nums.pack(side=tk.LEFT, fill=tk.Y)

        self._editor = tk.Text(editor_frame,
                               font=(MONO, self._font_size),
                               relief=tk.FLAT, bd=0,
                               undo=True, wrap=tk.NONE,
                               padx=12, pady=8,
                               spacing1=2, spacing3=2,
                               tabs="4c")
        self._editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = tk.Scrollbar(editor_frame, command=self._sync_scroll, relief=tk.FLAT, bd=0)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = tk.Scrollbar(panel, orient=tk.HORIZONTAL,
                           command=self._editor.xview, relief=tk.FLAT, bd=0)
        hsb.pack(fill=tk.X)
        self._editor.config(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._vsb = vsb
        self._hsb = hsb

        self._editor.bind("<KeyRelease>", self._on_key)
        self._editor.bind("<Key>", self._on_key_press, add="+")
        self._editor.bind("<MouseWheel>", self._on_scroll)
        self._editor.bind("<Button-1>", self._on_click, add="+")
        self._editor.bind("<<Modified>>", self._on_modified)

        return panel

    # FIX 1: _make_output_panel is now correctly indented as a method of NovaIDE
    def _make_output_panel(self):
        panel = tk.Frame(self._pane)

        hdr = tk.Frame(panel, height=32, bg=self._c["bg2"])
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        self._output_hdr = hdr

        # Console Tab
        self._tab_console = tk.Label(
            hdr,
            text="  Console",
            font=(FONT_FAMILY, 9),
            cursor="hand2",
            padx=4
        )
        self._tab_console.pack(side=tk.LEFT, pady=8)

        # LLVM IR Tab
        self._tab_ir = tk.Label(
            hdr,
            text="  LLVM IR",
            font=(FONT_FAMILY, 9),
            cursor="hand2",
            padx=4
        )
        self._tab_ir.pack(side=tk.LEFT, pady=8)

        self._tab_console.bind(
            "<Button-1>",
            lambda e: self._switch_tab("console")
        )
        self._tab_ir.bind(
            "<Button-1>",
            lambda e: self._switch_tab("ir")
        )

        self._status_dot = tk.Label(
            hdr,
            text="● Ready",
            font=(FONT_FAMILY, 9)
        )
        self._status_dot.pack(side=tk.RIGHT, padx=12)

        self._output = tk.Text(
            panel,
            font=(MONO, self._font_size),
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED,
            wrap=tk.WORD,
            padx=16,
            pady=12,
            spacing1=3
        )
        self._output.pack(fill=tk.BOTH, expand=True)

        self._active_tab = "console"
        return panel

    # FIX 2: _build_statusbar is now correctly indented as a method of NovaIDE
    def _build_statusbar(self):
        self._statusbar = tk.Frame(self, height=26)
        self._statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        self._statusbar.pack_propagate(False)

        self._status_var = tk.StringVar(value="Ready — write Nova code and press Run")
        self._status_lbl = tk.Label(self._statusbar, textvariable=self._status_var,
                                    font=(FONT_FAMILY, 9), padx=12)
        self._status_lbl.pack(side=tk.LEFT, pady=3)

        self._cursor_var = tk.StringVar(value="Ln 1, Col 1")
        self._cursor_lbl = tk.Label(self._statusbar, textvariable=self._cursor_var,
                                    font=(MONO, 9), padx=12)
        self._cursor_lbl.pack(side=tk.RIGHT, pady=3)

        self._editor.bind("<KeyRelease>", self._update_cursor, add="+")
        self._editor.bind("<ButtonRelease>", self._update_cursor, add="+")

    def _bind_shortcuts(self):
        self.bind("<Control-Return>", lambda e: self._run())
        self.bind("<Control-s>",      lambda e: self._save())
        self.bind("<Control-o>",      lambda e: self._open())
        self.bind("<Control-n>",      lambda e: self._new())
        self.bind("<Control-f>",      lambda e: self._find())
        self.bind("<Control-a>",      lambda e: self._select_all())
        self.bind("<Control-e>",      lambda e: self._show_examples())
        self.bind("<Control-t>",      lambda e: self._toggle_theme())
        self.bind("<Control-plus>",   lambda e: self._change_font(1))
        self.bind("<Control-minus>",  lambda e: self._change_font(-1))
        self.bind("<Control-equal>",  lambda e: self._change_font(1))

    # ── responsive layout ─────────────────────────────────────────────────────

    def _on_resize(self, event=None):
        if event and event.widget is not self:
            return
        w = self.winfo_width()
        if w < 1:
            return

        want = "vertical" if w < self.RESPONSIVE_BREAK else "horizontal"
        if want != self._pane_orient:
            self._reflow_panels(want)

        if self._shortcut_label:
            if w < self.RESPONSIVE_BREAK:
                self._shortcut_label.pack_forget()
            else:
                self._shortcut_label.pack(side=tk.RIGHT, padx=8)

    def _reflow_panels(self, orient):
        if self._reflowing:
            return
        self._reflowing = True
        try:
            self._pane.forget(self._editor_panel)
            self._pane.forget(self._output_panel)
            self._pane.destroy()

            self._pane = tk.PanedWindow(self._center,
                orient=tk.VERTICAL if orient == "vertical" else tk.HORIZONTAL,
                bg=self._c["border"], sashwidth=5,
                sashrelief=tk.FLAT, bd=0, opaqueresize=True)
            self._pane.pack(fill=tk.BOTH, expand=True)

            min_editor = 180 if orient == "vertical" else 280
            min_output = 140 if orient == "vertical" else 220
            self._pane.add(self._editor_panel, minsize=min_editor)
            self._pane.add(self._output_panel, minsize=min_output)
            self._pane_orient = orient
        finally:
            self._reflowing = False

    # ── error highlighting ────────────────────────────────────────────────────

    def _clear_error_highlights(self):
        self._error_lines = []
        self._editor.tag_remove("error_line", "1.0", tk.END)
        self._line_nums.config(state=tk.NORMAL)
        self._line_nums.tag_remove("error_gutter", "1.0", tk.END)
        self._line_nums.config(state=tk.DISABLED)

    def _highlight_error_lines(self, lines):
        self._error_lines = lines
        for ln in lines:
            self._editor.tag_add("error_line", f"{ln}.0", f"{ln}.end")
            self._line_nums.config(state=tk.NORMAL)
            self._line_nums.tag_add("error_gutter", f"{ln}.0", f"{ln}.end")
            self._line_nums.config(state=tk.DISABLED)
        if lines:
            self._editor.see(f"{lines[0]}.0")
            self._editor.mark_set(tk.INSERT, f"{lines[0]}.0")

    # ── editor helpers ────────────────────────────────────────────────────────

    def _load_default(self):
        self._load_example_code(EXAMPLES[0]["code"])

    def _load_example_code(self, code):
        self._editor.delete("1.0", tk.END)
        self._editor.insert("1.0", code)
        self._editor.edit_modified(False)
        self._modified = False
        self._current_file = None
        self._update_title()
        self._clear_error_highlights()
        self._clear_output()
        self._highlight_all()
        self._update_line_numbers()
        self._highlight_current_line()

    def _sync_scroll(self, *args):
        self._editor.yview(*args)
        self._line_nums.yview(*args)

    def _on_scroll(self, event=None):
        self.after(10, self._update_line_numbers)

    def _on_click(self, event=None):
        self.after(10, self._highlight_current_line)

    def _on_key(self, event=None):
        self._clear_error_highlights()
        self._highlight_all()
        self._update_line_numbers()
        self._highlight_current_line()

    def _on_key_press(self, event):
        if event.keysym == "Return":
            self.after(1, self._auto_indent)

    def _auto_indent(self):
        pos = self._editor.index(tk.INSERT)
        line = int(pos.split(".")[0])
        prev = self._editor.get(f"{line-1}.0", f"{line-1}.end")
        indent = len(prev) - len(prev.lstrip())
        if prev.rstrip().endswith("{"):
            indent += 4
        if indent > 0:
            self._editor.insert(tk.INSERT, " " * indent)

    def _on_modified(self, event=None):
        if self._editor.edit_modified():
            self._modified = True
            self._update_title()
            self._editor.edit_modified(False)

    def _update_title(self):
        name = os.path.basename(self._current_file) if self._current_file else "untitled.nova"
        star = " ●" if self._modified else ""
        self._title_var.set(f"{name}{star}")

    def _update_line_numbers(self):
        self._line_nums.config(state=tk.NORMAL)
        self._line_nums.delete("1.0", tk.END)
        lines = int(self._editor.index(tk.END).split(".")[0]) - 1
        self._line_nums.insert("1.0", "\n".join(str(i) for i in range(1, lines + 1)))
        if self._error_lines:
            for ln in self._error_lines:
                if ln <= lines:
                    self._line_nums.tag_add("error_gutter", f"{ln}.0", f"{ln}.end")
        self._line_nums.config(state=tk.DISABLED)
        self._line_nums.yview_moveto(self._editor.yview()[0])
        self._line_count_var.set(f"{lines} line{'s' if lines != 1 else ''}")

    def _update_cursor(self, event=None):
        pos = self._editor.index(tk.INSERT)
        ln, col = pos.split(".")
        self._cursor_var.set(f"Ln {ln}, Col {int(col)+1}")

    def _highlight_current_line(self):
        self._editor.tag_remove("current_line", "1.0", tk.END)
        ln = self._editor.index(tk.INSERT).split(".")[0]
        self._editor.tag_add("current_line", f"{ln}.0", f"{ln}.end")

    def _highlight_all(self):
        src = self._editor.get("1.0", tk.END)
        for tag in ("keyword", "number", "string", "comment", "operator"):
            self._editor.tag_remove(tag, "1.0", tk.END)

        for tag, pat, flags in [
            ("comment",  KW_COMMENTS,  re.DOTALL),
            ("string",   KW_STRINGS,   0),
            ("keyword",  KW_KEYWORDS,  0),
            ("number",   KW_NUMBERS,   0),
            ("operator", KW_OPERATORS, 0),
        ]:
            for m in re.finditer(pat, src, flags):
                start = f"1.0 + {m.start()} chars"
                end   = f"1.0 + {m.end()} chars"
                self._editor.tag_add(tag, start, end)

    def _change_font(self, delta):
        self._font_size = max(9, min(24, self._font_size + delta))
        self._editor.config(font=(MONO, self._font_size))
        self._line_nums.config(font=(MONO, self._font_size))
        self._output.config(font=(MONO, self._font_size))
        self._status_var.set(f"Font size: {self._font_size}pt")

    def _set_output(self, text, tag=""):
        self._output.config(state=tk.NORMAL)
        self._output.delete("1.0", tk.END)
        if tag:
            self._output.insert(tk.END, text, tag)
        else:
            self._output.insert(tk.END, text)
        self._output.config(state=tk.DISABLED)
        if self._active_tab == "console":
            self._save_console_view()

    def _append_output(self, text, tag=""):
        self._output.config(state=tk.NORMAL)
        if tag:
            self._output.insert(tk.END, text, tag)
        else:
            self._output.insert(tk.END, text)
        self._output.config(state=tk.DISABLED)
        if self._active_tab == "console":
            self._save_console_view()

    def _save_console_view(self):
        self._console_text = self._output.get("1.0", tk.END)

    # ── tabs ──────────────────────────────────────────────────────────────────

    def _switch_tab(self, tab):
        if tab == self._active_tab:
            return
        if self._active_tab == "console":
            self._save_console_view()

        self._active_tab = tab
        c = self._c
        if tab == "console":
            self._tab_console.config(fg=c["accent"], font=(FONT_FAMILY, 9, "bold"))
            self._tab_ir.config(fg=c["fg2"], font=(FONT_FAMILY, 9))
            self._output.config(state=tk.NORMAL)
            self._output.delete("1.0", tk.END)
            self._output.insert("1.0", self._console_text)
            self._output.config(state=tk.DISABLED)
        else:
            self._tab_ir.config(fg=c["accent"], font=(FONT_FAMILY, 9, "bold"))
            self._tab_console.config(fg=c["fg2"], font=(FONT_FAMILY, 9))
            self._output.config(state=tk.NORMAL)
            self._output.delete("1.0", tk.END)
            if self._last_ir:
                self._output.insert("1.0", self._last_ir, "dim")
            else:
                self._output.insert("1.0", "Run your program to generate LLVM IR.", "dim")
            self._output.config(state=tk.DISABLED)

    # ── examples gallery ──────────────────────────────────────────────────────

    def _show_examples(self):
        if hasattr(self, "_gallery") and self._gallery.winfo_exists():
            self._gallery.lift()
            return

        c = self._c
        win = tk.Toplevel(self)
        win.title("Examples Gallery")
        win.geometry("780x520")
        win.minsize(560, 400)
        win.transient(self)
        self._gallery = win

        hdr = tk.Frame(win, bg=c["bg2"], height=48)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  📚  Examples Gallery", font=(FONT_FAMILY, 13, "bold"),
                 bg=c["bg2"], fg=c["accent"]).pack(side=tk.LEFT, pady=10)
        tk.Label(hdr, text="Pick an example to preview, then load it into the editor",
                 font=(FONT_FAMILY, 9), bg=c["bg2"], fg=c["fg2"]).pack(side=tk.LEFT, padx=8)

        body = tk.PanedWindow(win, orient=tk.HORIZONTAL, bg=c["border"],
                              sashwidth=4, sashrelief=tk.FLAT, bd=0)
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg=c["bg"])
        body.add(left, minsize=200)

        tk.Label(left, text="Examples", font=(FONT_FAMILY, 10, "bold"),
                 bg=c["bg"], fg=c["fg2"]).pack(anchor="w", padx=12, pady=(12, 4))

        list_frame = tk.Frame(left, bg=c["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        lb = tk.Listbox(list_frame, font=(FONT_FAMILY, 10),
                        bg=c["bg2"], fg=c["fg"],
                        selectbackground=c["accent2"],
                        selectforeground="white",
                        relief=tk.FLAT, bd=0,
                        highlightthickness=1,
                        highlightbackground=c["border"],
                        activestyle="none")
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(list_frame, command=lb.yview, relief=tk.FLAT, bd=0)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        lb.config(yscrollcommand=sb.set)

        for i, ex in enumerate(EXAMPLES):
            lb.insert(tk.END, f"  {ex['title']}")

        right = tk.Frame(body, bg=c["bg"])
        body.add(right, minsize=320)

        desc_var = tk.StringVar(value=EXAMPLES[0]["desc"])
        tk.Label(right, textvariable=desc_var, font=(FONT_FAMILY, 10),
                 bg=c["bg"], fg=c["fg2"], wraplength=400,
                 justify=tk.LEFT).pack(anchor="w", padx=12, pady=(12, 4))

        preview = tk.Text(right, font=(MONO, 11),
                          bg=c["bg2"], fg=c["fg"],
                          relief=tk.FLAT, bd=0,
                          wrap=tk.NONE, padx=12, pady=10,
                          state=tk.DISABLED)
        preview.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        btn_row = tk.Frame(right, bg=c["bg"])
        btn_row.pack(fill=tk.X, padx=12, pady=10)

        def show_preview(idx):
            ex = EXAMPLES[idx]
            desc_var.set(ex["desc"])
            preview.config(state=tk.NORMAL)
            preview.delete("1.0", tk.END)
            preview.insert("1.0", ex["code"])
            preview.config(state=tk.DISABLED)

        def load_selected():
            sel = lb.curselection()
            if not sel:
                return
            idx = sel[0]
            if not self._confirm_discard():
                return
            ex = EXAMPLES[idx]
            self._load_example_code(ex["code"])
            self._status_var.set(f"Loaded example: {ex['title']}")
            win.destroy()

        def on_select(_event=None):
            sel = lb.curselection()
            if sel:
                show_preview(sel[0])

        lb.bind("<<ListboxSelect>>", on_select)
        lb.selection_set(0)
        show_preview(0)

        tk.Button(btn_row, text="Load into Editor", command=load_selected,
                  bg=c["green"], fg=c["bg"], relief=tk.FLAT,
                  font=(FONT_FAMILY, 10, "bold"), padx=16, pady=6,
                  cursor="hand2").pack(side=tk.RIGHT)
        tk.Button(btn_row, text="Cancel", command=win.destroy,
                  bg=c["bg3"], fg=c["fg"], relief=tk.FLAT,
                  font=(FONT_FAMILY, 10), padx=16, pady=6,
                  cursor="hand2",
                  highlightthickness=1,
                  highlightbackground=c["border"]).pack(side=tk.RIGHT, padx=8)

        win.configure(bg=c["bg"])
        left.configure(bg=c["bg"])
        right.configure(bg=c["bg"])
        btn_row.configure(bg=c["bg"])

    # ── actions ───────────────────────────────────────────────────────────────

    def _run(self):
        source = self._editor.get("1.0", tk.END).strip()
        if not source:
            self._status_var.set("Nothing to run — add some code first")
            return

        self._clear_error_highlights()
        self._switch_tab("console")
        self._set_output("Compiling and running...\n", "dim")
        self._status_var.set("Running...")
        self._run_btn.config(state=tk.DISABLED)
        self._status_dot.config(text="● Running", fg=self._c["yellow"])

        def task():
            output, success, ir, error_lines = compile_source(source)
            self.after(0, lambda: self._show_result(output, success, ir, error_lines))

        threading.Thread(target=task, daemon=True).start()

    def _show_result(self, output, success, ir, error_lines):
        self._run_btn.config(state=tk.NORMAL)
        self._last_ir = ir
        if success:
            self._set_output("Program output:\n\n", "info")
            self._append_output(output, "success")
            self._status_var.set("Compiled and ran successfully")
            self._status_dot.config(text="● Success", fg=self._c["green"])
        else:
            self._set_output("Errors found:\n\n", "info")
            self._append_output(output, "error")
            if error_lines:
                self._highlight_error_lines(error_lines)
                self._status_var.set(
                    f"Failed on line{'s' if len(error_lines) > 1 else ''} "
                    f"{', '.join(str(l) for l in error_lines)}")
            else:
                self._status_var.set("Compilation failed — check errors above")
            self._status_dot.config(text="● Failed", fg=self._c["red"])
            if ir:
                self._last_ir = ir

    def _clear_output(self):
        self._console_text = ""
        self._set_output("")
        self._last_ir = ""
        self._status_var.set("Ready")
        self._status_dot.config(text="● Ready", fg=self._c["fg2"])

    def _copy_output(self):
        text = self._output.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._status_var.set("Output copied to clipboard")

    def _export_ir(self):
        if not self._last_ir:
            messagebox.showinfo("Export IR", "Run your program first to generate LLVM IR.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".ll",
            filetypes=[("LLVM IR", "*.ll"), ("All files", "*.*")],
            initialfile="output.ll")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._last_ir)
            self._status_var.set(f"LLVM IR saved → {os.path.basename(path)}")

    def _insert_snippet(self, code):
        self._editor.insert(tk.INSERT, code + "\n")
        self._on_key()

    def _find(self):
        c = self._c
        dialog = tk.Toplevel(self)
        dialog.title("Find")
        dialog.configure(bg=c["bg2"])
        dialog.geometry("360x100")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Find:", bg=c["bg2"], fg=c["fg"],
                 font=(FONT_FAMILY, 10)).pack(padx=16, pady=(12, 4), anchor="w")
        entry = tk.Entry(dialog, font=(MONO, 11), bg=c["bg"], fg=c["fg"],
                         insertbackground=c["accent"], relief=tk.FLAT, bd=4)
        entry.pack(fill=tk.X, padx=16, pady=4)
        entry.focus_set()

        def do_find():
            query = entry.get()
            if not query:
                return
            start = self._editor.search(query, tk.INSERT, tk.END)
            if not start:
                start = self._editor.search(query, "1.0", tk.END)
            if start:
                end = f"{start}+{len(query)}c"
                self._editor.tag_remove(tk.SEL, "1.0", tk.END)
                self._editor.tag_add(tk.SEL, start, end)
                self._editor.mark_set(tk.INSERT, end)
                self._editor.see(start)
            else:
                self._status_var.set(f'"{query}" not found')

        btn_row = tk.Frame(dialog, bg=c["bg2"])
        btn_row.pack(fill=tk.X, padx=16, pady=8)
        tk.Button(btn_row, text="Find Next", command=do_find,
                  bg=c["accent"], fg="white", relief=tk.FLAT,
                  font=(FONT_FAMILY, 10, "bold"), padx=12, pady=4,
                  cursor="hand2").pack(side=tk.RIGHT)
        entry.bind("<Return>", lambda e: do_find())

    def _select_all(self):
        self._editor.tag_add(tk.SEL, "1.0", tk.END)
        return "break"

    def _toggle_help(self):
        self._help_visible = not self._help_visible
        if self._help_visible:
            self._help_frame.pack(side=tk.RIGHT, fill=tk.Y, before=self._center)
            self._help_frame.pack_propagate(False)
        else:
            self._help_frame.pack_forget()

    def _show_about(self):
        messagebox.showinfo("About NovaLang",
            "NovaLang IDE v2.1\n\n"
            "A simple compiled language targeting LLVM IR.\n"
            "Features: dark/light themes, examples gallery,\n"
            "line-specific error highlighting.\n\n"
            "Built with Python, rply, llvmlite, and tkinter.")

    def _confirm_discard(self):
        if not self._modified:
            return True
        return messagebox.askyesno("Unsaved Changes",
            "You have unsaved changes. Discard them?")

    def _new(self):
        if not self._confirm_discard():
            return
        self._editor.delete("1.0", tk.END)
        self._current_file = None
        self._modified = False
        self._update_title()
        self._clear_error_highlights()
        self._clear_output()
        self._update_line_numbers()

    def _add_recent(self, path):
        path = os.path.abspath(path)
        if path in self._recent_files:
            self._recent_files.remove(path)
        self._recent_files.insert(0, path)
        self._recent_files = self._recent_files[:8]
        self._update_recent_menu()

    def _update_recent_menu(self):
        self._recent_menu.delete(0, tk.END)
        if not self._recent_files:
            self._recent_menu.add_command(label="(none)", state=tk.DISABLED)
            return
        for path in self._recent_files:
            label = os.path.basename(path)
            self._recent_menu.add_command(
                label=label, command=lambda p=path: self._open_path(p))

    def _open_path(self, path):
        if not self._confirm_discard():
            return
        if not os.path.exists(path):
            messagebox.showerror("Open File", f"File not found:\n{path}")
            return
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self._editor.delete("1.0", tk.END)
        self._editor.insert("1.0", content)
        self._editor.edit_modified(False)
        self._current_file = path
        self._modified = False
        self._update_title()
        self._clear_error_highlights()
        self._highlight_all()
        self._update_line_numbers()
        self._add_recent(path)

    def _open(self):
        path = filedialog.askopenfilename(
            filetypes=[("Nova files", "*.nova"), ("All files", "*.*")])
        if path:
            self._open_path(path)

    def _save(self):
        if self._current_file:
            self._write_file(self._current_file)
        else:
            self._save_as()

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".nova",
            filetypes=[("Nova files", "*.nova"), ("All files", "*.*")])
        if path:
            self._write_file(path)

    def _write_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._editor.get("1.0", tk.END))
        self._current_file = path
        self._modified = False
        self._update_title()
        self._add_recent(path)
        self._status_var.set(f"Saved → {os.path.basename(path)}")

    def _on_close(self):
        if self._confirm_discard():
            self.destroy()


if __name__ == "__main__":
    app = NovaIDE()
    app.mainloop()