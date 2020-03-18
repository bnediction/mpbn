"""
This module provides a simple implementation of Most Permissive Boolean Networks
(MPBNs) for computing reachability properties, attractors, and reachable
attractors in locally-monotonic Boolean networks.
See https://arxiv.org/abs/1808.10240 for technical details.

It relies on clingo Answer-Set Programming solver
(https://github.com/potassco/clingo).

Examples are available at https://nbviewer.jupyter.org/github/pauleve/mpbn/tree/master/examples/

Quick example:

>>> mbn = mpbn.MPBooleanNetwork({
        "a": "!b",
        "b": "!a",
        "c": "!a & b"})
>>> list(mbn.attractors())
[{'a': 0, 'b': 1, 'c': 1}, {'a': 1, 'b': 0, 'c': 0}]
>>> mbn.reachability({'a': 0, 'b': 1, 'c': 1}, {'a': 1, 'b': 0, 'c': 0})
False
>>> mbn.reachability({'a': 0, 'b': 0, 'c': 0}, {'a': 1, 'b': 1, 'c': 1})
True
>>> list(mbn.attractors(reachable_from={'a': 0, 'b': 1, 'c': 0}))
[{'a': 0, 'b': 1, 'c': 1}]
"""

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
    Most Permissive Boolean Network

    Extends ``colomoto.minibn.BooleanNetwork`` class by adding methods for
    computing reachable and attractor properties with the Most Permissive
    semantics.
    It requires that the Boolean network is *locally monotonic*.

    Ensures that the Boolean functions are monotonic and in disjunctive normal
    form (DNF).
    The local-monotonic checking requires that a literal never appears
    with both signs in a same Boolean function.
    """
    def __init__(self, bn=minibn.BooleanNetwork(), auto_dnf=True):
        """
        Constructor for :py:class:`.MPBoooleanNetwork`.

        :param bn: Boolean network to copy from
        :type bn: :py:class:`colomoto.minibn.BooleanNetwork` or any type accepted by
            :py:class:`colomoto.minibn.BooleanNetwork` constructor
        :param bool auto_dnf: if ``False``, turns off automatic DNF
            transformation of local functions

        Examples:

        >>> mbn = MPBooleanNetwork("network.bnet")
        >>> bn = BooleanNetwork()
        >>> bn["a"] = ".."; ...
        >>> mbn = MPBooleanNetwork(bn)
        """
        self.auto_dnf = auto_dnf
        super(MPBooleanNetwork, self).__init__(bn)

    def formula_well_formed(self, f):
        pos_lits = set()
        neg_lits = set()
        def is_lit(f):
            if isinstance(f, self.ba.Symbol):
                pos_lits.add(f.obj)
                return True
            if isinstance(f, self.ba.NOT) \
                    and isinstance(f.args[0], self.ba.Symbol):
                neg_lits.add(f.args[0].obj)
                return True
            return False

        def is_clause(f):
            if is_lit(f):
                return True
            if isinstance(f, self.ba.AND):
                for g in f.args:
                    if not is_lit(g):
                        return False
                return True
            return False

        def assert_monotonicity():
            both = pos_lits.intersection(neg_lits)
            assert not both, \
                f"expression '{f}' contains literals with both signs ({both}). Try .simplify()?"

        if f in [self.ba.TRUE, self.ba.FALSE]:
            return True
        if is_clause(f):
            assert_monotonicity()
            return True
        if isinstance(f, self.ba.OR):
            for g in f.args:
                if not is_clause(g):
                    return False
            assert_monotonicity()
            return True
        return False

    def __setitem__(self, a, f):
        """
        Assigns the Boolean function ``f`` to component ``a``.
        Unless :py:attr:`.auto_dnf` is ``False``, ``f`` is converted into DNF
        form first.
        """
        if isinstance(f, str):
            f = self.ba.parse(f)
        f = self._autobool(f)
        if self.auto_dnf and not self.formula_well_formed(f):
            f = self.ba.dnf(f).simplify()
            assert self.formula_well_formed(f)
        return super().__setitem__(self._autokey(a), f)

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
        facts = ["timepoint({},{}).".format(e,t)]
        facts += [" mp_state({},{},\"{}\",{}).".format(e,t,n,s2v(s))
                    for (n,s) in c.items()]
        if complete:
            facts += [" 1 {{mp_state({},{},\"{}\",(-1;1))}} 1.".format(e,t,n)
                        for n in self if n not in c]
        return "".join(facts)

    def reachability(self, x, y):
        """
        Returns ``True`` whenever the configuration `y` is reachable from `x`
        with the Most Permissive semantics.
        Configurations can be partially defined.
        In that case, returns ``True`` whenever there exists a configuration
        matching with `y` which is reachable with at least one configuration
        matching with `x`

        :param dict[str,int] x: initial configuration
        :param dict[str,int] y: target configuration
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

    def attractors(self, reachable_from=None, constraints={}, limit=0, star='*'):
        """
        Iterator over attractors of the MPBN.
        An attractor is an hypercube, represented by a dictionnary mapping every
        component of the network to either ``0``, ``1``, or ``star``.

        :param dict[str,int] reachable_from: restrict to the attractors
            reachable from the given configuration. Whenever partial, restrict
            attractors to the one reachable by at least one matching
            configuration.
        :param dict[str,int] constraints: consider only attractors matching with
            the given constraints.
        :param int limit: maximum number of solutions, ``0`` for unlimited.
        :param str star: value to use for components which are free in the
            attractor
        """
        s = clingo_subsets(limit=limit)
        s.load(aspf("mp_eval.asp"))
        s.load(aspf("mp_attractor.asp"))
        s.add("base", [], self.asp_of_bn())
        e = "__a"
        t2 = "final"
        if reachable_from:
            t1 = "0"
            s.load(aspf("mp_positivereach-np.asp"))
            s.add("base", [], self.asp_of_cfg(e,t1,reachable_from, complete=True))
            s.add("base", [], "is_reachable({},{},{}).".format(e,t1,t2))
            s.add("base", [], "mp_state({},{},N,V) :- attractor(N,V).".format(e,t2))

        for n, b in constraints.items():
            s.add("base", [], "mp_reach({},{},\"{}\",{}).".format(e,t2,n,s2v(b)))
            s.add("base", [], ":- mp_reach({},{},\"{}\",{}).".format(e,t2,n,s2v(1-b)))

        s.add("base", [], "#show attractor/2.")

        s.ground([("base",[])])
        for sol in s.solve(yield_=True):
            attractor = {}
            data = sol.symbols(shown=True)
            for d in data:
                if d.name != "attractor":
                    continue
                (n, v) = d.arguments
                n = n.string
                v = v.number
                if v == 2:
                    v = star
                else:
                    v = 1 if v == 1 else 0
                if n in attractor:
                    attractor[n] = star
                else:
                    attractor[n] = v
            yield attractor


def load(filename, **opts):
    """
    Create a :py:class:`.MPBooleanNetwork` object from ``filename`` in BoolNet
    format; ``filename`` can be a local file or an URL.
    """
    return MPBooleanNetwork.load(filename, **opts)


__all__ = ["load", "MPBooleanNetwork"]
