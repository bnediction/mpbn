import unittest

import mpbn

class RechabilityTest_Automata18(unittest.TestCase):
    def setUp(self):
        self.mbn = mpbn.MPBooleanNetwork("examples/automata18.bnet")
        self.c0 = dict(a=0,b=0,c=0)
        self.c1 = dict(a=1,b=1,c=1)
        self.ci = dict(a=0,b=1,c=0)
        self.cd = dict(a=1,b=0,c=0)
    def test_c0c1(self):
        self.assertTrue(self.mbn.reachability(self.c0, self.c1))
    def test_c0ci(self):
        self.assertTrue(self.mbn.reachability(self.c0, self.ci))
    def test_cicd(self):
        self.assertFalse(self.mbn.reachability(self.ci, self.cd))
