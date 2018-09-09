
__version__ = "0.1a0"

# TODO: check local-monotonicity
# TODO: reachability

import os
from colomoto import minibn

import clingo

__asplibdir__ = os.path.join(os.path.dirname(__file__), "..", "asplib")
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

class MPBooleanNetwork(minibn.BooleanNetwork):
    """
    TODO
    """
    def __init__(self, bn):
        """
        TODO
        """
        assert isinstance(bn, minibn.BooleanNetwork)
        super(MPBooleanNetwork, self).__init__()
        self.ba = bn.ba
        for n, f in bn.items():
            self[n] = self.ba.dnf(f).simplify()

    def asp_of_bn(self):
        def clauses_of_dnf(f):
            if f == self.ba.FALSE:
                return []
            if isinstance(f, self.ba.OR):
                return f.args
            else:
                return [f]
        def literals_of_clause(c):
            def make_literal(l):
                if isinstance(l, self.ba.NOT):
                    return (l.args[0].obj, -1)
                else:
                    return (l.obj, 1)
            lits = c.args if isinstance(c, self.ba.AND) else [c]
            return map(make_literal, lits)
        facts = []
        for n, f in self.items():
            facts.append("node(\"{}\").".format(n))
            for cid, c in enumerate(clauses_of_dnf(f)):
                facts.append("\n")
                for m, v in literals_of_clause(c):
                    facts.append(" clause(\"{}\",{},\"{}\",{}).".format(n, cid, m, v))
            facts.append("\n")
        return "".join(facts)

    def attractors(self, limit=0, star='*', yield_=False):
        """
        TODO
        """
        s = clingo_subsets(limit=limit)
        s.load(aspf("mp_attractor.asp"))
        s.add("base", [], self.asp_of_bn())
        s.ground([("base",[])])
        if not yield_:
            results = []
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
            if yield_:
                yield attractor
            else:
                results.append(attractor)
        if not yield_:
            return results


def load(bn):
    """
    TODO
    """
    return MPBooleanNetwork(bn)

