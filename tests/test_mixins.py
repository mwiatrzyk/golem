import unittest

import golem


class TestExpectCallMixin(unittest.TestCase):

    def test_whenExpectCallUsedForNonMockMethods_TypeErrorIsRaised(self):

        class Interface(object):
            def foo(self):
                pass

        class TestCase(golem.ExpectCallMixin):
            def test_interface(self):
                self.expectCall(Interface().foo)

        with self.assertRaisesRegexp(TypeError, "'expectCall' used with non-mock method"):
            TestCase().test_interface()
