
__version__ = "0.1a0"

# TODO: check local-monotonicity
# TODO: partial configurations

import os
from colomoto import minibn

from boolean import boolean
import clingo

__asplibdir__ = os.path.join(os.path.dirname(__file__), "asplib")
def aspf(basename):
    return os.path.join(__asplibdir__, basename)

def clingo_subsets(limit=0):
    s = clingo.Control()
    s.configuration.solve.models = limit
    s.configuration.solve.project = 1
    s.configuration.solve.enum_mode = "domRec"
    s.configuration.solver[0].heuristic = "Domain"
    s.configuration.solver[0].dom_mod = "5,16"
    return s

def clingo_exists():
    s = clingo.Control()
    s.configuration.solve.models = 1
    return s

def s2v(s):
    return 1 if s > 0 else -1

class MPBooleanNetwork(minibn.BooleanNetwork):
    """
    TODO
    """
    def __init__(self, bn):
        """
        TODO
        """
        if isinstance(bn, str):
            if "\n" in bn or not os.path.exists(bn):
                bn = minibn.BooleanNetwork(bn)
            else:
                bn = minibn.BooleanNetwork.load(bn)
        elif isinstance(bn, dict):
            bn = minibn.BooleanNetwork(bn)
        assert isinstance(bn, minibn.BooleanNetwork)
        super(MPBooleanNetwork, self).__init__()
        self.ba = bn.ba
        for n, f in bn.items():
            self[n] = self.ba.dnf(f).simplify()

    def asp_of_bn(self):
        def clauses_of_dnf(f):
            if f == self.ba.FALSE:
                return [False]
            if f == self.ba.TRUE:
                return [True]
            if isinstance(f, boolean.OR):
                return f.args
            else:
                return [f]
        def literals_of_clause(c):
            def make_literal(l):
                if isinstance(l, boolean.NOT):
                    return (l.args[0].obj, -1)
                else:
                    return (l.obj, 1)
            lits = c.args if isinstance(c, boolean.AND) else [c]
            return map(make_literal, lits)
        facts = []
        for n, f in self.items():
            facts.append("node(\"{}\").".format(n))
            for cid, c in enumerate(clauses_of_dnf(f)):
                facts.append("\n")
                if isinstance(c, bool):
                    facts.append(" constant(\"{}\",{}).".format(n, s2v(c)))
                else:
                    for m, v in literals_of_clause(c):
                        facts.append(" clause(\"{}\",{},\"{}\",{}).".format(n, cid, m, v))
            facts.append("\n")
        return "".join(facts)

    def asp_of_cfg(self, e, t, c, complete=False):
        """
        TODO
        """
        facts = ["timepoint({},{}).".format(e,t)]
        facts += [" mp_state({},{},\"{}\",{}).".format(e,t,n,s2v(s)) \
                    for (n,s) in c.items()]
        if complete:
            facts += [" 1 {{mp_state({},{},\"{}\",(-1;1))}} 1.".format(e,t,n) \
                        for n in self if n not in c]
        return "".join(facts)

    def reachability(self, x, y):
        """
        TODO
        """
        s = clingo_exists()
        s.load(aspf("mp_eval.asp"))
        s.load(aspf("mp_positivereach-np.asp"))
        s.add("base", [], self.asp_of_bn())
        e = "default"
        t1 = 0
        t2 = 1
        s.add("base", [], self.asp_of_cfg(e,t1,x,complete=True))
        s.add("base", [], self.asp_of_cfg(e,t2,y))
        s.add("base", [], "is_reachable({},{},{}).".format(e,t1,t2))
        s.ground([("base",[])])
        res = s.solve()
        return res.satisfiable

    def attractors(self, limit=0, star='*', reachable_from=None):
        """
        TODO
        """
        s = clingo_subsets(limit=limit)
        s.load(aspf("mp_eval.asp"))
        s.load(aspf("mp_attractor.asp"))
        s.add("base", [], self.asp_of_bn())
        if reachable_from:
            e = "__a"
            t1 = "0"
            t2 = "final"
            s.load(aspf("mp_positivereach-np.asp"))
            s.add("base", [], self.asp_of_cfg(e,t1,reachable_from, complete=True))
            s.add("base", [], "is_reachable({},{},{}).".format(e,t1,t2))
            s.add("base", [], "mp_state({},{},N,V) :- attractor(N,V).".format(e,t2))
        s.ground([("base",[])])
        for sol in s.solve(yield_=True):
            attractor = {}
            data = sol.symbols(shown=True)
            for d in data:
                if d.name != "attractor":
                    continue
                (n, v) = d.arguments
                n = n.string
                v = 1 if v.number == 1 else 0
                if n in attractor:
                    attractor[n] = star
                else:
                    attractor[n] = v
            yield attractor

