"""
NovaLang AST Nodes
Each class represents a language construct and emits LLVM IR via .eval().
"""

from llvmlite import ir

# ── Helpers ──────────────────────────────────────────────────────────────────

INT32   = ir.IntType(32)
FLOAT   = ir.FloatType()
INT1    = ir.IntType(1)
INT8    = ir.IntType(8)
VOIDPTR = INT8.as_pointer()

_str_counter = 0
_fmt_counter = 0

def _fresh_str_name():
    global _str_counter
    _str_counter += 1
    return f"str_{_str_counter}"

def _fresh_fmt_name():
    global _fmt_counter
    _fmt_counter += 1
    return f"fmt_{_fmt_counter}"


# ── Literals ─────────────────────────────────────────────────────────────────

class Number:
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module  = module
        self.value   = ir.Constant(INT32, int(value))

    def eval(self):
        return self.value


class FloatNum:
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module  = module
        self.value   = ir.Constant(FLOAT, float(value))

    def eval(self):
        return self.value


class Boolean:
    def __init__(self, builder, module, value: bool):
        self.builder = builder
        self.module  = module
        self.value   = ir.Constant(INT1, int(value))

    def eval(self):
        return self.value


class StringLiteral:
    def __init__(self, builder, module, text):
        self.builder = builder
        self.module  = module
        self.text    = text[1:-1] + "\0"   # strip quotes, add null terminator

    def eval(self):
        fmt     = self.text.encode("utf8")
        arr_ty  = ir.ArrayType(INT8, len(fmt))
        gvar    = ir.GlobalVariable(self.module, arr_ty, name=_fresh_str_name())
        gvar.initializer     = ir.Constant(arr_ty, bytearray(fmt))
        gvar.global_constant = True
        gvar.linkage         = "internal"
        return self.builder.bitcast(gvar, VOIDPTR)


# ── Arithmetic ────────────────────────────────────────────────────────────────

def _to_float(builder, val):
    if val.type == FLOAT:
        return val
    return builder.sitofp(val, FLOAT, name="tofloat")


class Sum:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module  = module
        self.left    = left
        self.right   = right

    def eval(self):
        l, r = self.left.eval(), self.right.eval()
        if l.type == FLOAT or r.type == FLOAT:
            return self.builder.fadd(_to_float(self.builder, l), _to_float(self.builder, r), name="faddtmp")
        return self.builder.add(l, r, name="sumtmp")


class Sub:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module  = module
        self.left    = left
        self.right   = right

    def eval(self):
        l, r = self.left.eval(), self.right.eval()
        if l.type == FLOAT or r.type == FLOAT:
            return self.builder.fsub(_to_float(self.builder, l), _to_float(self.builder, r), name="fsubtmp")
        return self.builder.sub(l, r, name="subtmp")


class Mul:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module  = module
        self.left    = left
        self.right   = right

    def eval(self):
        l, r = self.left.eval(), self.right.eval()
        if l.type == FLOAT or r.type == FLOAT:
            return self.builder.fmul(_to_float(self.builder, l), _to_float(self.builder, r), name="fmultmp")
        return self.builder.mul(l, r, name="multmp")


class Div:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module  = module
        self.left    = left
        self.right   = right

    def eval(self):
        l, r = self.left.eval(), self.right.eval()
        if l.type == FLOAT or r.type == FLOAT:
            return self.builder.fdiv(_to_float(self.builder, l), _to_float(self.builder, r), name="fdivtmp")
        return self.builder.sdiv(l, r, name="divtmp")


class Mod:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module  = module
        self.left    = left
        self.right   = right

    def eval(self):
        l, r = self.left.eval(), self.right.eval()
        return self.builder.srem(l, r, name="modtmp")


class Negate:
    def __init__(self, builder, module, operand):
        self.builder = builder
        self.module  = module
        self.operand = operand

    def eval(self):
        v = self.operand.eval()
        if v.type == FLOAT:
            return self.builder.fneg(v, name="fnegtmp")
        return self.builder.neg(v, name="negtmp")


# ── Comparisons & Logical ─────────────────────────────────────────────────────

class Comparison:
    def __init__(self, builder, module, scope, operator, left, right):
        self.builder  = builder
        self.module   = module
        self.scope    = scope
        self.operator = operator
        self.left     = left
        self.right    = right

    def eval(self):
        l, r = self.left.eval(), self.right.eval()
        op_map = {'GT': '>', 'LT': '<', 'GTE': '>=', 'LTE': '<=', 'EQ': '==', 'NEQ': '!='}
        op = op_map.get(self.operator)
        if op is None:
            raise ValueError(f"Unknown comparison operator: {self.operator}")
        if l.type == FLOAT or r.type == FLOAT:
            return self.builder.fcmp_ordered(op, _to_float(self.builder, l),
                                             _to_float(self.builder, r), name="fcmptmp")
        return self.builder.icmp_signed(op, l, r, name="cmptmp")


class LogicalAnd:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module  = module
        self.left    = left
        self.right   = right

    def eval(self):
        return self.builder.and_(self.left.eval(), self.right.eval(), name="andtmp")


class LogicalOr:
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module  = module
        self.left    = left
        self.right   = right

    def eval(self):
        return self.builder.or_(self.left.eval(), self.right.eval(), name="ortmp")


class LogicalNot:
    def __init__(self, builder, module, operand):
        self.builder = builder
        self.module  = module
        self.operand = operand

    def eval(self):
        return self.builder.not_(self.operand.eval(), name="nottmp")


# ── I/O ───────────────────────────────────────────────────────────────────────

class Print:
    def __init__(self, builder, module, printf, value):
        self.builder = builder
        self.module  = module
        self.printf  = printf
        self.value   = value

    def _make_fmt(self, text):
        raw = (text + "\0").encode("utf8")
        arr = ir.ArrayType(INT8, len(raw))
        gv  = ir.GlobalVariable(self.module, arr, name=_fresh_fmt_name())
        gv.initializer     = ir.Constant(arr, bytearray(raw))
        gv.global_constant = True
        gv.linkage         = "internal"
        return self.builder.bitcast(gv, VOIDPTR)

    def eval(self):
        v = self.value.eval()
        if v.type == FLOAT:
            promoted = self.builder.fpext(v, ir.DoubleType(), name="dbl")
            self.builder.call(self.printf, [self._make_fmt("%f\n"), promoted])
        elif v.type == VOIDPTR:
            self.builder.call(self.printf, [self._make_fmt("%s\n"), v])
        elif v.type == INT1:
            true_s  = StringLiteral(self.builder, self.module, '"true"').eval()
            false_s = StringLiteral(self.builder, self.module, '"false"').eval()
            result  = self.builder.select(v, true_s, false_s, name="boolstr")
            self.builder.call(self.printf, [self._make_fmt("%s\n"), result])
        else:
            self.builder.call(self.printf, [self._make_fmt("%d\n"), v])


# ── Variables ─────────────────────────────────────────────────────────────────

class VariableAssign:
    def __init__(self, builder, module, scope, name, value):
        self.builder = builder
        self.module  = module
        self.scope   = scope
        self.name    = name
        self.value   = value

    def eval(self):
        val = self.value.eval()
        if self.name in self.scope:
            self.builder.store(val, self.scope[self.name])
            return self.scope[self.name]
        else:
            alloca = self.builder.alloca(val.type, name=self.name)
            self.builder.store(val, alloca)
            self.scope[self.name] = alloca
            return alloca


class VariableReference:
    def __init__(self, builder, module, scope, name):
        self.builder = builder
        self.module  = module
        self.scope   = scope
        self.name    = name

    def eval(self):
        if self.name not in self.scope:
            raise NameError(f"[NovaLang] Undefined variable: '{self.name}'")
        return self.builder.load(self.scope[self.name], name=f"load_{self.name}")


# ── Control Flow ──────────────────────────────────────────────────────────────

class IfElse:
    def __init__(self, builder, module, cond, if_block, else_block):
        self.builder    = builder
        self.module     = module
        self.cond       = cond
        self.if_block   = if_block
        self.else_block = else_block

    def eval(self):
        cond_val = self.cond.eval()
        with self.builder.if_else(cond_val) as (then, otherwise):
            with then:
                self.if_block.eval()
            with otherwise:
                self.else_block.eval()


class IfOnly:
    def __init__(self, builder, module, cond, if_block):
        self.builder  = builder
        self.module   = module
        self.cond     = cond
        self.if_block = if_block

    def eval(self):
        cond_val = self.cond.eval()
        with self.builder.if_then(cond_val):
            self.if_block.eval()


class WhileLoop:
    """
    Emits a proper LLVM while loop:

        br header
      header:
        cond = <evaluate condition>
        cbranch cond, body, exit
      body:
        <evaluate body statements>
        br header          ← loop back
      exit:
        <continue>

    The condition and body AST nodes are stored unevaluated and only
    have .eval() called inside the correct basic blocks, so the IR
    instructions land in the right place and reads/writes to alloca'd
    variables work correctly across iterations.
    """
    def __init__(self, builder, module, cond_node, body_node):
        self.builder   = builder
        self.module    = module
        self.cond_node = cond_node   # AST node — NOT yet eval()'d
        self.body_node = body_node   # AST node — NOT yet eval()'d

    def eval(self):
        fn = self.builder.block.parent

        header_block = fn.append_basic_block("while_header")
        body_block   = fn.append_basic_block("while_body")
        exit_block   = fn.append_basic_block("while_exit")

        # Jump into header
        self.builder.branch(header_block)

        # ── Header: evaluate condition ────────────────────────────────────
        self.builder.position_at_end(header_block)
        cond_val = self.cond_node.eval()          # emits cmp instruction HERE
        self.builder.cbranch(cond_val, body_block, exit_block)

        # ── Body: evaluate statements, then loop back ─────────────────────
        self.builder.position_at_end(body_block)
        self.body_node.eval()                     # emits body instructions HERE
        self.builder.branch(header_block)         # unconditional back-edge

        # ── Exit: continue after loop ─────────────────────────────────────
        self.builder.position_at_end(exit_block)


# ── Block (multiple statements) ───────────────────────────────────────────────

class Block:
    def __init__(self, stmts):
        self.stmts = stmts

    def eval(self):
        result = None
        for s in self.stmts:
            result = s.eval()
        return result