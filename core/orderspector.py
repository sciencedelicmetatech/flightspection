MAX_STEPS = 30

def redexes(lhs, term):
    if not lhs or term is None: return []
    out, start = [], 0
    while True:
        i = term.find(lhs, start)
        if i < 0: break
        out.append(i)
        start = i + 1
    return out

def apply_at(term, pos, lhs, rhs):
    return term[:pos] + rhs + term[pos + len(lhs):]

def rewrite(term, rules, max_steps=MAX_STEPS):
    if term is None: return None, 0
    if not rules: return term, 0
    steps = 0
    while True:
        moved = False
        for lhs, rhs in rules:
            if not lhs: continue
            pos = redexes(lhs, term)
            if pos:
                term = apply_at(term, pos[0], lhs, rhs)
                moved = True
                steps += 1
                if steps >= max_steps: return None, steps
                break
        if not moved: break
    return term, steps

def apply_order(term, first, second):
    t, s1 = rewrite(term, [first])
    if t is None: return None, s1
    t, s2 = rewrite(t, [second])
    return t, s1 + s2

def verify(a, b, terms):
    for t in terms:
        rab, _ = apply_order(t, a, b)
        rba, _ = apply_order(t, b, a)
        if rab is None or rba is None: return True, "DIVERGE", 0
        if rab != rba:
            if len(rab) < len(rba): return True, "AB", 0
            if len(rba) < len(rab): return True, "BA", 0
            return True, "TIE", 0
    return False, None, 0

# Static proposers
def p_overlap(a, b, term):
    la, lb = a[0], b[0]
    pa, pb = redexes(la, term), redexes(lb, term)
    for x in pa:
        xe = x + len(la)
        for y in pb:
            ye = y + len(lb)
            if x < ye and y < xe: return True, 0
    return False, 0

def p_self_growth(a, b, term=None):
    for lhs, rhs in (a, b):
        if lhs and rhs and lhs in rhs: return True, 0
    return False, 0

TERM_FREE = {"static_self_growth"}
DEFAULT_PROPOSERS = [("overlap", p_overlap), ("static_self_growth", p_self_growth)]

def propose(a, b, term, proposers=DEFAULT_PROPOSERS):
    for name, fn in proposers:
        fired, _ = (fn(a, b) if name in TERM_FREE else fn(a, b, term))
        if fired: return True
    return False

def eval_gated(a, b, terms, proposers=DEFAULT_PROPOSERS):
    for t in terms:
        if propose(a, b, t, proposers): return verify(a, b, terms)
    return False, None, 0