import unittest

from golem.core import MockMethod


class TestMockMethod(unittest.TestCase):

    def setUp(self):

        class Interface(object):

            def foo(self):
                pass

            def bar(self, a):
                pass

            def baz(self, a, b):
                pass

            def spam(self, a, b, c=None):
                pass

        self.Interface = Interface

    def test_ifFunctionTakesNoParameters_decodeRaisesTypeErrorIfCalledWithOne(self):
        uut = MockMethod(self.Interface(), self.Interface.foo)
        with self.assertRaisesRegexp(TypeError, "Interface.foo\(\) takes no arguments \(1 given\)"):
            uut.decode(1)

    def test_ifFunctionDoesNotHaveArgumentOfGivenName_decodeRaisesTypeError(self):
        uut = MockMethod(self.Interface(), self.Interface.bar)
        with self.assertRaisesRegexp(TypeError, "Interface.bar\(\) got an unexpected keyword argument 'b'"):
            uut.decode(b=1)

    def test_ifDecodeCalledWithTooManyArguments_TypeErrorIsRaised(self):
        uut = MockMethod(self.Interface(), self.Interface.bar)
        with self.assertRaisesRegexp(TypeError, "Interface.bar\(\) takes exactly 1 argument \(2 given\)"):
            uut.decode(1, 2)
        uut = MockMethod(self.Interface(), self.Interface.baz)
        with self.assertRaisesRegexp(TypeError, "Interface.baz\(\) takes exactly 2 arguments \(3 given\)"):
            uut.decode(1, 2, 3)

    def test_ifDecodeCalledWithTooFewArguments_TypeErrorIsRaised(self):
        uut = MockMethod(self.Interface(), self.Interface.spam)
        with self.assertRaisesRegexp(TypeError, "Interface.spam\(\) takes at least 2 arguments \(1 given\)"):
            uut.decode(1)

    def test_ifDecodeForFunctionWithDefaultArgsCalledWithTooManyArguments_TypeErrorIsRaised(self):
        uut = MockMethod(self.Interface(), self.Interface.spam)
        with self.assertRaisesRegexp(TypeError, "Interface.spam\(\) takes at most 3 arguments \(4 given\)"):
            uut.decode(1, 2, 3, 4)
