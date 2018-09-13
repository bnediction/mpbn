import unittest

import mpbn

class AttractorsTest(unittest.TestCase):
    def test_automata18(self):
        mbn = mpbn.MPBooleanNetwork("examples/automata18.bnet")
        attractors = list(mbn.attractors())
        self.assertEqual(len(attractors), 2)
