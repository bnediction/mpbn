import networkx as nx
import clingo

from boolean import boolean
from colomoto import minibn

from typing import Optional

from biodivine_aeon import Bdd, BddPointer
from biodivine_aeon import BddVariableSet, BddValuation

def is_unate_symbolic(f: Bdd) -> boolean:
    """
    Returns `True` if the given `biodivine_aeon.Bdd` represents a unate function
    (i.e. all arguments are locally monotonic).

    The way this is handled is that we test for positive/negative monotonicity by
    symbolically expressing the inputs where decreasing the input increases the
    output (i.e. a counterexample to positive monotonicity), or vice versa.
    """
    variables = f.__ctx__().variable_ids()
    f_false = f.l_not()
    f_true = f
    for var in f.support_set():
        var_is_true = f.__ctx__().mk_literal(var, True)
        var_is_false = f.__ctx__().mk_literal(var, False)
        
        f_1_to_0 = f_false.l_and(var_is_true).r_exists(var)
        f_0_to_1 = f_true.l_and(var_is_false).r_exists(var)
        is_positive = f_0_to_1.l_and(f_1_to_0).r_exists(variables).l_not().is_true()        
        
        f_0_to_0 = f_false.l_and(var_is_false).r_exists(var)
        f_1_to_1 = f_true.l_and(var_is_true).r_exists(var)
        is_negative = f_0_to_0.l_and(f_1_to_1).r_exists(variables).l_not().is_true()

        # An input cannot be both positive and negative at the same time.
        assert not (is_positive and is_negative)

        if (not is_positive) and (not is_negative):
            return False
    return True


def ba_to_bdd(ba: boolean.BooleanAlgebra, f: boolean.Expression, ctx: BddVariableSet | None = None) -> Bdd:
    """
    Takes a `boolean.Expression` (with the associated `boolean.BooleanAlgebra`) and
    converts it to a `biodivine_aeon.Bdd`. 

    Note that the `Bdd` has an associated `biodivine_aeon.BddVariableSet` context, which maps the 
    variable IDs to names. You can provide your own context, or one will be created for you
    (to access the underlying context object, use `bdd.__ctx__()`).
    """
    ba_vars = f.symbols
    variables = sorted([ str(var) for var in ba_vars ])
    if ctx is None:        
        ctx = BddVariableSet(variables)
    else:
        # Check that all variables that exist in `f` also exist in `ctx`.
        assert all((ctx.find_variable(var) is not None) for var in variables)
    def ba_to_bdd_rec(f: boolean.Expression) -> Bdd:
        if type(f) is ba.TRUE or isinstance(f, minibn._TRUE):
            return ctx.mk_const(True)
        if type(f) is ba.FALSE or isinstance(f, minibn._FALSE):
            return ctx.mk_const(False)        
        if type(f) is ba.Symbol: 
            return ctx.mk_literal(str(f.obj), True)
        if type(f) is ba.NOT:
            assert len(f.args) == 1, "Cannot transform NOT with more than one argument."
            return ba_to_bdd_rec(f.args[0]).l_not()
        if type(f) is ba.AND:
            result = ctx.mk_const(True)
            for arg in f.args:
                result = result.l_and(ba_to_bdd_rec(arg))
            return result
        if type(f) is ba.OR:
            result = ctx.mk_const(False)
            for arg in f.args:
                result = result.l_or(ba_to_bdd_rec(arg))
            return result        
        raise NotImplementedError(str(f), type(f))
        
    return ba_to_bdd_rec(f)
        
def bdd_to_dnf(ba: boolean.BooleanAlgebra, f: Bdd) -> boolean.Expression:
    """
    Convert a `biodivine_aeon.Bdd` to a `boolean.Expression` in disjunctive normal form.
    """
    if f.is_true():
        return ba.TRUE
    if f.is_false():
        return ba.FALSE    
    ctx = f.__ctx__()
    # Technically, `optimize=True` should be set by default, but just in case.
    dnf = f.to_dnf(optimize=True)
    # Maps BDD variables to BooleanAlgebra Symbols.
    var_to_symbol = { var: ba.Symbol(ctx.get_variable_name(var)) for var in ctx.variable_ids() }
    ba_clauses = []
    for clause in dnf:
        literals = []
        for (var, value) in clause.items():            
            if value:
                literals.append(var_to_symbol[var])
            else:
                literals.append(ba.NOT(var_to_symbol[var]))                
        assert len(literals) > 0
        if len(literals) == 1:
            ba_clauses.append(literals[0])
        else:
            ba_clauses.append(ba.AND(*literals))
    assert len(ba_clauses) > 0 
    if len(ba_clauses) == 1:
        return ba_clauses[0]
    else:
        return ba.OR(*ba_clauses)

def make_dnf_boolfunc(ba, f, **unused_opts):
    bdd = ba_to_bdd(ba, f)
    return bdd_to_dnf(ba, bdd)

def asp_of_bdd(var_name, bdd: Bdd) -> list[str]:
    """
    Convert a `biodivine_aeon.Bdd` into a list of `clingo` atoms
    representing the individual BDD nodes.    
    """
    if bdd.is_false():
        return [f"bdd({clingo.String(var_name)},-1)"]
    if bdd.is_true():
        return [f"bdd({clingo.String(var_name)},1)"]
    
    _rules = {}
    def _rec(node: BddPointer, node_name: Optional[str] = None) -> str:
        if node.is_zero():
            return "-1"
        if node.is_one():
            return "1"
        if node_name is None:
            node_name = f"{var_name}_n{int(node)}"        
        node_name_clingo = clingo.String(node_name)
        if node_name_clingo in _rules:
            # The node was already declared.
            return node_name_clingo
        node_var = bdd.node_variable(node)
        assert node_var is not None # Only `None` if node is terminal.
        (lo, hi) = bdd.node_links(node)
        var = clingo.String(bdd.__ctx__().get_variable_name(node_var))
        lo = _rec(lo)
        hi = _rec(hi)
        atom = f"bdd({node_name_clingo},{var},{lo},{hi})"
        _rules[node_name_clingo] = atom
        return node_name_clingo
    _rec(bdd.root(), var_name)

    return list(_rules.values())

def bddasp_of_boolfunc(ba, f, var_name):
    f_bdd = ba_to_bdd(ba, f)
    atoms = asp_of_bdd(var_name, f_bdd)
    return "\n".join((f"{a}." for a in atoms))

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

    bdd_ctx = BddVariableSet(names)

    f = []
    for i in range(n):
        pos = []
        for x in adyn.nodes():
            dx = list(x)
            dx[i] = 1-x[i]
            y = dx if tuple(dx) in adyn[x] else x
            target = y[i]
            if target:
                pos.append(BddValuation(bdd_ctx, list(x)))
        if len(pos) == 0:
            f.append(bdd_ctx.mk_false())
        else:
            f.append(bdd_ctx.mk_dnf(pos))

    bn = bn_class()
    for (i, name) in enumerate(names):
        bn[name] = bdd_to_dnf(bn.ba, f[i])
    if simplify:
        bn = bn.simplify()
    return bn
