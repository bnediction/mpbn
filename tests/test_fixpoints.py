import unittest

import mpbn

def t_of_d(d):
    return tuple(sorted(d.items()))


class TestFixedpoints(unittest.TestCase):
    def setUp(self):
        self.mbn = mpbn.MPBooleanNetwork("examples/automata18.bnet")
        self.c0 = dict(a=0,b=0,c=0)
        self.c1 = dict(a=1,b=1,c=1)
        self.ci = dict(a=0,b=1,c=0)
        self.cd = dict(a=1,b=0,c=0)
        self.all_fps = set([(("a",0),("b",1),("c",1)),
            (("a",1),("b",0),("c",0))])
    def test_all(self):
        fps = set(map(t_of_d,self.mbn.fixedpoints()))
        self.assertEqual(fps, self.all_fps)
    def test_reachable(self):
        self.assertEqual(len(list(self.mbn.fixedpoints(reachable_from=self.ci))), 1)
    def test_limit(self):
        self.assertEqual(len(list(self.mbn.fixedpoints(limit=1))), 1)