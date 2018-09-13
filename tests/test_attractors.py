import unittest

from colomoto import minibn
import mpbn

class AttractorsTest(unittest.TestCase):
    def test_automata18(self):
        bn = minibn.BooleanNetwork.load("examples/automata18.bnet")
        mbn = mpbn.load(bn)
        attractors = mbn.attractors()
        print(attractors)
        assert len(attractors) == 2
