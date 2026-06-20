from collections import defaultdict, deque

# ─────────────────────────────
# Grammar
# ─────────────────────────────
class Grammar:
    def __init__(self, productions):
        self.productions = [(productions[0][0] + "'", [productions[0][0]])] + productions

        self.non_terminals = set(lhs for lhs, _ in self.productions)
        self.terminals = set()

        for _, rhs in self.productions:
            for s in rhs:
                if s not in self.non_terminals:
                    self.terminals.add(s)

        self.terminals.add('$')


# ─────────────────────────────
# FIRST
# ─────────────────────────────
def compute_first(g):
    FIRST = {nt: set() for nt in g.non_terminals}

    changed = True
    while changed:
        changed = False
        for lhs, rhs in g.productions:
            before = len(FIRST[lhs])

            for sym in rhs:
                if sym in g.terminals:
                    FIRST[lhs].add(sym)
                    break
                FIRST[lhs] |= FIRST[sym]
                break

            if len(FIRST[lhs]) != before:
                changed = True

    return FIRST


# ─────────────────────────────
# FOLLOW
# ─────────────────────────────
def compute_follow(g, FIRST):
    FOLLOW = {nt: set() for nt in g.non_terminals}

    start = g.productions[0][0]
    FOLLOW[start].add('$')

    changed = True
    while changed:
        changed = False

        for lhs, rhs in g.productions:
            for i, B in enumerate(rhs):

                if B not in g.non_terminals:
                    continue

                before = len(FOLLOW[B])

                if i + 1 >= len(rhs):
                    FOLLOW[B] |= FOLLOW[lhs]
                else:
                    nxt = rhs[i + 1]
                    if nxt in g.terminals:
                        FOLLOW[B].add(nxt)
                    else:
                        FOLLOW[B] |= FIRST.get(nxt, set())

                if len(FOLLOW[B]) != before:
                    changed = True

    return FOLLOW


# ─────────────────────────────
# LR(0)
# ─────────────────────────────
def closure(items, g):
    closure = set(items)

    while True:
        new = set()

        for p, dot in closure:
            lhs, rhs = g.productions[p]

            if dot < len(rhs):
                sym = rhs[dot]
                if sym in g.non_terminals:
                    for i, (l, r) in enumerate(g.productions):
                        if l == sym:
                            new.add((i, 0))

        if new.issubset(closure):
            break

        closure |= new

    return closure


def goto(items, symbol, g):
    moved = {(p, dot + 1) for p, dot in items
             if dot < len(g.productions[p][1]) and g.productions[p][1][dot] == symbol}

    return closure(moved, g)


def build_states(g):
    start = {(0, 0)}
    states = [closure(start, g)]
    trans = {}
    queue = deque([0])

    while queue:
        i = queue.popleft()
        state = states[i]

        symbols = set()
        for p, dot in state:
            rhs = g.productions[p][1]
            if dot < len(rhs):
                symbols.add(rhs[dot])

        for sym in symbols:
            nxt = goto(state, sym, g)

            if nxt not in states:
                states.append(nxt)
                queue.append(len(states) - 1)

            trans[(i, sym)] = states.index(nxt)

    return states, trans


# ─────────────────────────────
# SLR TABLE
# ─────────────────────────────
def build_slr(g, states, trans, FOLLOW):
    ACTION = defaultdict(dict)
    GOTO = defaultdict(dict)

    for i, state in enumerate(states):
        for p, dot in state:
            lhs, rhs = g.productions[p]

            if dot < len(rhs):
                sym = rhs[dot]
                if sym in g.terminals:
                    ACTION[i][sym] = ('shift', trans[(i, sym)])

            else:
                if p == 0:
                    ACTION[i]['$'] = ('accept',)
                else:
                    for f in FOLLOW[lhs]:
                        ACTION[i][f] = ('reduce', p)

        for nt in g.non_terminals:
            if (i, nt) in trans:
                GOTO[i][nt] = trans[(i, nt)]

    return ACTION, GOTO


# ─────────────────────────────
# PARSER (CLEAN OUTPUT)
# ─────────────────────────────
def parse_slr(input_str, ACTION, GOTO, g):
    tokens = input_str.split() + ['$']

    stack = ['$']
    state_stack = [0]
    i = 0

    print("Stack\t\tInput\t\tAction")

    while True:
        state = state_stack[-1]
        a = tokens[i]

        act = ACTION.get(state, {}).get(a)

        print(f"{' '.join(stack)}\t\t{' '.join(tokens[i:])}\t\t{act}")

        if act is None:
            print("REJECT")
            return False

        # SHIFT
        if act[0] == 'shift':
            stack.append(a)
            state_stack.append(act[1])
            i += 1

        # REDUCE
        elif act[0] == 'reduce':
            p = act[1]
            lhs, rhs = g.productions[p]

            for _ in rhs:
                stack.pop()
                state_stack.pop()

            stack.append(lhs)
            state_stack.append(GOTO[state_stack[-1]][lhs])

        # ACCEPT
        elif act[0] == 'accept':
            print(f"{' '.join(stack)}\t\t$\t\tACCEPT")
            print("ACCEPT")
            return True


# ─────────────────────────────
# MAIN (TASK 1)
# ─────────────────────────────
if __name__ == "__main__":

    productions = [
        ('E', ['E', '+', 'T']),
        ('E', ['T']),
        ('T', ['T', '*', 'F']),
        ('T', ['F']),
        ('F', ['(', 'E', ')']),
        ('F', ['id'])
    ]

    g = Grammar(productions)

    FIRST = compute_first(g)
    FOLLOW = compute_follow(g, FIRST)

    states, trans = build_states(g)
    ACTION, GOTO = build_slr(g, states, trans, FOLLOW)

    parse_slr("id + id * id", ACTION, GOTO, g)