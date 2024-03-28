import networkx as nx
from pyeda.boolalg.minimization import *
from pyeda.inter import expr

from colomoto import minibn

def bn_of_asynchronous_transition_graph(adyn, names,
            parse_node=(lambda n: tuple(map(int, n))),
            bn_class=minibn.BooleanNetwork):
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
        f.append(expr("|".join(map(expr_of_cfg,pos))))
    f = bn_class(dict(zip(names, map(lambda e: str(e).replace('~','!'), espresso_exprs(*f)))))
    return f

if __name__ == "__main__":
    import mpbn

    f = mpbn.MPBooleanNetwork({
        "x1": "x2",
        "x2": "x3",
        "x3": "x1"})
    g = f.dynamics("asynchronous")
    print(bn_of_asynchronous_transition_graph(g, list(f)))
