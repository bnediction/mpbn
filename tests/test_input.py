import unittest

import mpbn

class InputTest(unittest.TestCase):
    def test_nonmonotonic(self):
        mbn = mpbn.MPBooleanNetwork(encoding="unate-dnf")
        def oops():
            mbn["a"] = "(b&!c)|(!b&c)"
        self.assertRaises(AssertionError, oops)
        mbn = mpbn.MPBooleanNetwork()
        mbn["a"] = "(b&!c)|(!b&c)"
