"""
NovaLang Parser
Builds a grammar using rply and returns an AST on each parse.
AST nodes store their children unevaluated — .eval() is called
by the caller (main.py) which triggers IR emission in the right order.
"""

from rply import ParserGenerator
from nova_ast import (
    Number, FloatNum, Boolean, StringLiteral,
    Sum, Sub, Mul, Div, Mod, Negate,
    Print, VariableAssign, VariableReference,
    Comparison, LogicalAnd, LogicalOr, LogicalNot,
    IfElse, IfOnly, WhileLoop, Block,
)

_ALL_TOKENS = [
    'NUMBER', 'FLOAT', 'STRING', 'TRUE', 'FALSE',
    'PRINT',
    'OPEN_PAREN', 'CLOSE_PAREN',
    'OPEN_BRACE', 'CLOSE_BRACE',
    'SEMI_COLON',
    'SUM', 'SUB', 'MUL', 'DIV', 'MOD',
    'GT', 'LT', 'GTE', 'LTE', 'EQ', 'NEQ',
    'AND', 'OR', 'NOT',
    'IF', 'ELSE', 'WHILE',
    'IDENTIFIER', 'ASSIGN',
]


class NovaParser:
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator(
            _ALL_TOKENS,
            precedence=[
                ('left',  ['OR']),
                ('left',  ['AND']),
                ('right', ['NOT']),
                ('left',  ['EQ', 'NEQ']),
                ('left',  ['GT', 'LT', 'GTE', 'LTE']),
                ('left',  ['SUM', 'SUB']),
                ('left',  ['MUL', 'DIV', 'MOD']),
                ('right', ['UMINUS']),
                ('left',  ['ASSIGN']),
            ]
        )
        self.module  = module
        self.builder = builder
        self.printf  = printf
        self.scope   = {}

    def b(self): return self.builder
    def m(self): return self.module
    def s(self): return self.scope

    def parse(self):
        pg = self.pg

        @pg.production('program : statement')
        def program(p):
            return p[0]

        # ── blocks ───────────────────────────────────────────────────────────

        @pg.production('block : statement')
        def block_single(p):
            return Block([p[0]])

        @pg.production('block : block statement')
        def block_multi(p):
            p[0].stmts.append(p[1])
            return p[0]

        # ── statements ───────────────────────────────────────────────────────

        @pg.production('statement : IDENTIFIER ASSIGN expression SEMI_COLON')
        def assignment(p):
            return VariableAssign(self.b(), self.m(), self.s(), p[0].getstr(), p[2])

        @pg.production('statement : PRINT OPEN_PAREN expression CLOSE_PAREN SEMI_COLON')
        def print_stmt(p):
            return Print(self.b(), self.m(), self.printf, p[2])

        @pg.production('statement : IF OPEN_PAREN condition CLOSE_PAREN '
                       'OPEN_BRACE block CLOSE_BRACE '
                       'ELSE OPEN_BRACE block CLOSE_BRACE')
        def if_else_stmt(p):
            return IfElse(self.b(), self.m(), p[2], p[5], p[9])

        @pg.production('statement : IF OPEN_PAREN condition CLOSE_PAREN '
                       'OPEN_BRACE block CLOSE_BRACE')
        def if_only_stmt(p):
            return IfOnly(self.b(), self.m(), p[2], p[5])

        @pg.production('statement : WHILE OPEN_PAREN condition CLOSE_PAREN '
                       'OPEN_BRACE block CLOSE_BRACE')
        def while_stmt(p):
            # Pass cond and body nodes directly — they are NOT eval()'d yet.
            # WhileLoop.eval() will call their .eval() inside the correct
            # LLVM basic blocks (header and body respectively).
            return WhileLoop(self.b(), self.m(), p[2], p[5])

        # ── conditions ───────────────────────────────────────────────────────

        @pg.production('condition : expression GT expression')
        @pg.production('condition : expression LT expression')
        @pg.production('condition : expression GTE expression')
        @pg.production('condition : expression LTE expression')
        @pg.production('condition : expression EQ expression')
        @pg.production('condition : expression NEQ expression')
        def comparison(p):
            return Comparison(self.b(), self.m(), self.s(),
                              p[1].gettokentype(), p[0], p[2])

        @pg.production('condition : condition AND condition')
        def logical_and(p):
            return LogicalAnd(self.b(), self.m(), p[0], p[2])

        @pg.production('condition : condition OR condition')
        def logical_or(p):
            return LogicalOr(self.b(), self.m(), p[0], p[2])

        @pg.production('condition : NOT condition')
        def logical_not(p):
            return LogicalNot(self.b(), self.m(), p[1])

        @pg.production('condition : OPEN_PAREN condition CLOSE_PAREN')
        def paren_cond(p):
            return p[1]

        # ── expressions ──────────────────────────────────────────────────────

        @pg.production('expression : expression SUM expression')
        @pg.production('expression : expression SUB expression')
        @pg.production('expression : expression MUL expression')
        @pg.production('expression : expression DIV expression')
        @pg.production('expression : expression MOD expression')
        def binary_expr(p):
            op = p[1].gettokentype()
            cls = {'SUM': Sum, 'SUB': Sub, 'MUL': Mul, 'DIV': Div, 'MOD': Mod}[op]
            return cls(self.b(), self.m(), p[0], p[2])

        @pg.production('expression : SUB expression', precedence='UMINUS')
        def unary_minus(p):
            return Negate(self.b(), self.m(), p[1])

        @pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
        def paren_expr(p):
            return p[1]

        @pg.production('expression : NUMBER')
        def number_expr(p):
            return Number(self.b(), self.m(), p[0].getstr())

        @pg.production('expression : FLOAT')
        def float_expr(p):
            return FloatNum(self.b(), self.m(), p[0].getstr())

        @pg.production('expression : STRING')
        def string_expr(p):
            return StringLiteral(self.b(), self.m(), p[0].getstr())

        @pg.production('expression : TRUE')
        def true_expr(p):
            return Boolean(self.b(), self.m(), True)

        @pg.production('expression : FALSE')
        def false_expr(p):
            return Boolean(self.b(), self.m(), False)

        @pg.production('expression : IDENTIFIER')
        def var_expr(p):
            return VariableReference(self.b(), self.m(), self.s(), p[0].getstr())

        # ── error ─────────────────────────────────────────────────────────────

        @pg.error
        def error_handle(token):
            if token.gettokentype() == '$end':
                raise SyntaxError("[NovaLang] Unexpected end of input")
            raise SyntaxError(
                f"[NovaLang] Unexpected token '{token.getstr()}' "
                f"(type={token.gettokentype()}) "
                f"at position {token.source_pos}"
            )

    def get_parser(self):
        return self.pg.build()