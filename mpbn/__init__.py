
# TODO: input from minibn
# TODO: convert to DNF, simplify
# TODO: check local-monotonicity
# TODO: export to ASP
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
    # subset solutions only
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
        super(self, MPBooleanNetwork).__init__(XXX)
        raise NotImplementedError

    def _bn_asp(self):
        raise NotImplementedError

    def attractors(self, limit=0, star='*', yield_=False):
        """
        TODO
        """
        s = clingo_subsets(limit=limit)
        s.load(aspf("mp_attractor.asp"))
        s.add("base", [], self._bn_asp())
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
        return results


def load(bn):
    """
    TODO
    """
    return MPBooleanNetwork(bn)


if __name__ == "__main__":
    raise NotImplementedError

