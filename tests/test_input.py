import unittest

import mpbn

class InputTest(unittest.TestCase):
    def test_nonmonotonic(self):
        mbn = mpbn.MPBooleanNetwork()
        def oops():
            mbn["a"] = "(b&!c)|(!b&c)"
        self.assertRaises(AssertionError, oops)


