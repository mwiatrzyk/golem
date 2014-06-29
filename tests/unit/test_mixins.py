import unittest

from golem import exc, mock_method
from golem.mixins import MockTestCaseMixin


class TestMockTestCaseMixin(unittest.TestCase):

    def setUp(self):

        class Interface(object):

            @mock_method
            def foo(self):
                pass

            @mock_method
            def bar(self, a):
                pass

            @mock_method
            def baz(self, a, b, c=None):
                pass

        self.iface = Interface()
        self.uut = MockTestCaseMixin()

    def test_ifSingleExpectCallGiven_failsIfNotSatisfied(self):
        self.uut.expectCall(self.iface.foo)
        with self.assertRaises(exc.MockUndersaturatedError):
            self.uut.assertSaturated()

    def test_ifSingleExpectCallGivenAndSatisfied_pass(self):
        self.uut.expectCall(self.iface.baz, 1, 2, c=3)
        self.iface.baz(1, 2, c=3)
        self.uut.assertSaturated()

    def test_ifTwoDifferentExpectCallsGiven_failsIfOnlyOneSatisfied(self):
        self.uut.expectCall(self.iface.foo)
        self.uut.expectCall(self.iface.bar, 1)
        self.iface.bar(1)
        with self.assertRaises(exc.MockUndersaturatedError):
            self.uut.assertSaturated()

    def test_ifTwoDifferentExpectCallsGivenAndBothSatisfied_pass(self):
        self.uut.expectCall(self.iface.foo)
        self.uut.expectCall(self.iface.bar, 1)
        self.iface.bar(1)
        self.iface.foo()
        self.uut.assertSaturated()

    def test_ifTwoDifferentExpectationsSetForOneFunctionAndOnlyOneSatisfied_fail(self):
        self.uut.expectCall(self.iface.bar, 1)
        self.uut.expectCall(self.iface.bar, 2)
        self.iface.bar(2)
        with self.assertRaises(exc.MockUndersaturatedError):
            self.uut.assertSaturated()

    def test_ifTwoDifferentExpectationsSetForOneFunctionAndBothSatisfied_pass(self):
        self.uut.expectCall(self.iface.bar, 1)
        self.uut.expectCall(self.iface.bar, 2)
        self.iface.bar(2)
        self.iface.bar(1)
        self.uut.assertSaturated()
