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

    def test_ifFunctionTakesNoParametersAndCalledWithNoParameters_emptyDictIsReturned(self):
        uut = FunctionInspector(self.foo)
        self.assertEqual({}, uut.normalize())

    def test_ifFunctionDoesNotHaveArgumentOfGivenName_decodeRaisesTypeError(self):
        uut = FunctionInspector(self.bar)
        with self.assertRaisesRegexp(TypeError, "bar\(\) got an unexpected keyword argument 'b'"):
            uut.normalize(b=1)

    def test_ifNormalizeCalledWithValidKeywordArgument_itIsReturnedAsResult(self):
        uut = FunctionInspector(self.bar)
        self.assertEqual({'a': 1}, uut.normalize(a=1))

    def test_ifDecodeCalledWithTooManyArguments_TypeErrorIsRaised(self):
        uut = FunctionInspector(self.bar)
        with self.assertRaisesRegexp(TypeError, "bar\(\) takes exactly 1 argument \(2 given\)"):
            uut.normalize(1, 2)
        uut = FunctionInspector(self.baz)
        with self.assertRaisesRegexp(TypeError, "baz\(\) takes exactly 2 arguments \(3 given\)"):
            uut.normalize(1, 2, 3)

    def test_ifNormalizingPositionalArguments_theyAreDecodedToTheirNames(self):
        uut = FunctionInspector(self.baz)
        self.assertEqual({'a': 1, 'b': 2}, uut.normalize(1, 2))

    def test_ifNormalizingPositionalAndKeywordArguments_theyAreDecodedToTheirNames(self):
        uut = FunctionInspector(self.spam)
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, uut.normalize(1, 2, c=3))

    def test_ifNormalizingWithRequiredArgsOnly_defaultsAreIncludedInResultAsWell(self):
        uut = FunctionInspector(self.spam)
        self.assertEqual({'a': 1, 'b': 2, 'c': None}, uut.normalize(1, 2))

    def test_ifDecodeCalledWithTooFewArguments_TypeErrorIsRaised(self):
        uut = FunctionInspector(self.spam)
        with self.assertRaisesRegexp(TypeError, "spam\(\) takes at least 2 arguments \(1 given\)"):
            uut.normalize(1)
        uut = FunctionInspector(self.baz)
        with self.assertRaisesRegexp(TypeError, "baz\(\) takes exactly 2 arguments \(1 given\)"):
            uut.normalize(1)

    def test_ifDecodeForFunctionWithDefaultArgsCalledWithTooManyArguments_TypeErrorIsRaised(self):
        uut = FunctionInspector(self.spam)
        with self.assertRaisesRegexp(TypeError, "spam\(\) takes at most 3 arguments \(4 given\)"):
            uut.normalize(1, 2, 3, 4)

    def test_ifDecodingMixedPositionalAndKeywordArguments_normalizationSucceeds(self):
        uut = FunctionInspector(self.baz)
        self.assertEqual({'a': 1, 'b': 2}, uut.normalize(1, b=2))
