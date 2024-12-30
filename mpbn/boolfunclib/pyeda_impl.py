import clingo
import networkx as nx

from pyeda.boolalg.minimization import *
import pyeda.boolalg.expr
from pyeda.inter import expr
from pyeda.boolalg import bdd

from colomoto import minibn

def expr2str(ex):
    """
    converts a pyeda Boolean expression to string representation
    """
    def _protect(e):
        if isinstance(e, (pyeda.boolalg.expr.OrOp, pyeda.boolalg.expr.AndOp)):
            return f"({expr2str(e)})"
        return expr2str(e)
    if isinstance(ex, pyeda.boolalg.expr.Variable):
        return str(ex)
    elif isinstance(ex, pyeda.boolalg.expr._One):
        return "1"
    elif isinstance(ex, pyeda.boolalg.expr._Zero):
        return "0"
    elif isinstance(ex, pyeda.boolalg.expr.Complement):
        return f"!{_protect(ex.__invert__())}"
    elif isinstance(ex, pyeda.boolalg.expr.NotOp):
        return f"!{_protect(ex.x)}"
    elif isinstance(ex, pyeda.boolalg.expr.OrOp):
        return " | ".join(map(_protect, ex.xs))
    elif isinstance(ex, pyeda.boolalg.expr.AndOp):
        return " & ".join(map(_protect, ex.xs))
    raise NotImplementedError(str(ex), type(ex))

def expr2bpy(ex, ba):
    """
    converts a pyeda Boolean expression into a boolean.py one
    """
    if isinstance(ex, pyeda.boolalg.expr.Variable):
        return ba.Symbol(str(ex))
    elif isinstance(ex, pyeda.boolalg.expr._One):
        return ba.TRUE
    elif isinstance(ex, pyeda.boolalg.expr._Zero):
        return ba.FALSE
    elif isinstance(ex, pyeda.boolalg.expr.Complement):
        return ba.NOT(ba.Symbol(str(ex.__invert__())))
    elif isinstance(ex, pyeda.boolalg.expr.NotOp):
        return ba.NOT(expr2bpy(ex.x, ba))
    elif isinstance(ex, pyeda.boolalg.expr.OrOp):
        return ba.OR(*(expr2bpy(x, ba) for x in ex.xs))
    elif isinstance(ex, pyeda.boolalg.expr.AndOp):
        return ba.AND(*(expr2bpy(x, ba) for x in ex.xs))
    raise NotImplementedError(str(ex), type(ex))

def asp_of_bdd(bid, b):
    _rules = dict()
    def register(node, nid=None):
        if node is bdd.BDDNODEONE:
            if nid is not None:
                _rules[bid] = f"bdd({clingo.String(nid)},1)"
            return 1
        elif node is bdd.BDDNODEZERO:
            if nid is not None:
                _rules[bid] = f"bdd({clingo.String(nid)},-1)"
            return -1
        nid = clingo.String(f"{bid}_n{id(node)}" if nid is None else nid)
        if nid not in _rules:
            var = clingo.String(bdd._VARS[node.root].qualname)
            lo = register(node.lo)
            hi = register(node.hi)
            a = f"bdd({nid},{var},{lo},{hi})"
            _rules[nid] = a
        return nid
    register(b.node, bid)
    return _rules.values()

def bddasp_of_boolfunc(ba, f, i):
    e = expr(str(f).replace("!","~"))
    b = bdd.expr2bdd(e)
    atoms = asp_of_bdd(i, b)
    return "\n".join((f"{a}." for a in atoms))

def make_dnf_boolfunc(ba, f, try_unate_hard=False, simplify=True):
    """
    try_unate_hard: use costly CNF/DNF transformations
    simplify: use boolean.py simplification method
    """
    e = expr(str(f).replace("!","~"))
    e = e.to_dnf()
    e = e.simplify()
    e = expr2bpy(e, ba)
    if try_unate_hard:
        e = minibn.simplify_dnf(self.ba, e)
    elif simplify:
        e = e.simplify()
    return e

def bn_of_asynchronous_transition_graph(adyn, names,
            parse_node=(lambda n: tuple(map(int, n))),
            bn_class=minibn.BooleanNetwork,
            simplify=True):
    """
    Convert the transition graph of a (fully) asynchronous Boolean network to
    a propositional logic representation.

    The object `adyn` must be an instance of `networkx.DiGraph`.
    The `parse_node` function must return a tuple of 0 and 1 from an `adyn`
    node. By default, it is assumed that nodes are strings of binary values.
    Returned object will be of `bn_class`, instantiated with a dictionnary
    mapping component names to a string representation of their Boolean expression.
    """
    relabel = {label: parse_node(label) for label in adyn.nodes()}
    adyn = nx.relabel_nodes(adyn, relabel)
    n = len(next(iter(adyn.nodes)))
    assert n == len(names), "list of component names and dimension of configuraitons seem different"
    assert adyn.number_of_nodes() == 2**n, "unexpected number of nodes in the transition graph"

    def expr_of_cfg(x):
        e = "&".join(f"{'~' if not v else ''}{names[i]}" for i, v in enumerate(x))
        return f"({e})"

    f = []
    for i in range(n):
        pos = []
        for x in adyn.nodes():
            dx = list(x)
            dx[i] = 1-x[i]
            y = dx if tuple(dx) in adyn[x] else x
            target = y[i]
            if target:
                pos.append(x)
        if not pos:
            f.append(expr("0"))
        else:
            e = expr("|".join(map(expr_of_cfg,pos)))
            e, = espresso_exprs(e.to_dnf())
            f.append(e)
    f = map(expr2str, f)
    f = bn_class(dict(zip(names, f)))
    if simplify:
        f = f.simplify()
    return f

