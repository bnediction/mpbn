import unittest

import mpbn

class DyanmicsTest(unittest.TestCase):
    def test_automata18(self):
        mbn = mpbn.MPBooleanNetwork("examples/automata18.bnet")
        dynamics = mbn.dynamics()
