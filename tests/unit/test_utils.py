import unittest

from golem.utils import FunctionInspector


class TestFunctionInspector(unittest.TestCase):

    def setUp(self):

        def foo():
            pass

        def bar(a):
            pass

        def baz(a, b):
            pass

        def spam(a, b, c=None):
            pass

        self.foo = foo
        self.bar = bar
        self.baz = baz
        self.spam = spam

    def test_ifFunctionTakesNoParameters_decodeRaisesTypeErrorIfCalledWithOne(self):
        uut = FunctionInspector(self.foo)
        with self.assertRaisesRegexp(TypeError, "foo\(\) takes no arguments \(1 given\)"):
            uut.normalize(1)

    def test_ifFunctionDoesNotHaveArgumentOfGivenName_decodeRaisesTypeError(self):
        uut = FunctionInspector(self.bar)
        with self.assertRaisesRegexp(TypeError, "bar\(\) got an unexpected keyword argument 'b'"):
            uut.normalize(b=1)

    def test_ifDecodeCalledWithTooManyArguments_TypeErrorIsRaised(self):
        uut = FunctionInspector(self.bar)
        with self.assertRaisesRegexp(TypeError, "bar\(\) takes exactly 1 argument \(2 given\)"):
            uut.normalize(1, 2)
        uut = FunctionInspector(self.baz)
        with self.assertRaisesRegexp(TypeError, "baz\(\) takes exactly 2 arguments \(3 given\)"):
            uut.normalize(1, 2, 3)

    def test_ifDecodeCalledWithTooFewArguments_TypeErrorIsRaised(self):
        uut = FunctionInspector(self.spam)
        with self.assertRaisesRegexp(TypeError, "spam\(\) takes at least 2 arguments \(1 given\)"):
            uut.normalize(1)

    def test_ifDecodeForFunctionWithDefaultArgsCalledWithTooManyArguments_TypeErrorIsRaised(self):
        uut = FunctionInspector(self.spam)
        with self.assertRaisesRegexp(TypeError, "spam\(\) takes at most 3 arguments \(4 given\)"):
            uut.normalize(1, 2, 3, 4)
