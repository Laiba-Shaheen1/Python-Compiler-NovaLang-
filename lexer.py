"""
NovaLang Lexer
Tokenizes .nova source files into a stream of tokens for the parser.
"""

from rply import LexerGenerator


class Lexer:
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # --- Keywords (must be before IDENTIFIER) ---
        self.lexer.add('PRINT',    r'print')
        self.lexer.add('IF',       r'if')
        self.lexer.add('ELSE',     r'else')
        self.lexer.add('WHILE',    r'while')
        self.lexer.add('AND',      r'&&')
        self.lexer.add('OR',       r'\|\|')
        self.lexer.add('NOT',      r'!')
        self.lexer.add('TRUE',     r'true')
        self.lexer.add('FALSE',    r'false')

        # --- Identifiers ---
        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')

        # --- Literals ---
        self.lexer.add('FLOAT',   r'\d+\.\d+')
        self.lexer.add('NUMBER',  r'\d+')
        self.lexer.add('STRING',  r'"[^"]*"')

        # --- Operators ---
        self.lexer.add('EQ',      r'==')
        self.lexer.add('NEQ',     r'!=')
        self.lexer.add('GTE',     r'>=')
        self.lexer.add('LTE',     r'<=')
        self.lexer.add('GT',      r'>')
        self.lexer.add('LT',      r'<')
        self.lexer.add('ASSIGN',  r'=')
        self.lexer.add('MUL',     r'\*')
        self.lexer.add('DIV',     r'/')
        self.lexer.add('MOD',     r'%')
        self.lexer.add('SUM',     r'\+')
        self.lexer.add('SUB',     r'-')

        # --- Delimiters ---
        self.lexer.add('OPEN_PAREN',   r'\(')
        self.lexer.add('CLOSE_PAREN',  r'\)')
        self.lexer.add('OPEN_BRACE',   r'\{')
        self.lexer.add('CLOSE_BRACE',  r'\}')
        self.lexer.add('SEMI_COLON',   r';')
        self.lexer.add('COMMA',        r',')

        # --- Ignore whitespace and comments ---
        self.lexer.ignore(r'//[^\n]*')   # single-line comments
        self.lexer.ignore(r'/\*.*?\*/')  # multi-line comments (non-greedy)
        self.lexer.ignore(r'\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
