import unittest

from colomoto import minibn
import mpbn

class AttractorRechabilityTest_Automata18(unittest.TestCase):
    def setUp(self):
        bn = minibn.BooleanNetwork.load("examples/automata18.bnet")
        self.mbn = mpbn.load(bn)
        self.c0 = dict(a=0,b=0,c=0)
        self.c1 = dict(a=1,b=1,c=1)
        self.ci = dict(a=0,b=1,c=0)
        self.cd = dict(a=1,b=0,c=0)
    def test_c0(self):
        assert len(list(self.mbn.attractors(reachable_from=self.c0))) == 2
    def test_ci(self):
        assert len(list(self.mbn.attractors(reachable_from=self.ci))) == 1


