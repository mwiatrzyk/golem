import unittest

from golem import exc, mock_method, AtLeast, AtMost, Return, Invoke, _
from golem.core import Expectation


class TestMockMethod(unittest.TestCase):

    def setUp(self):

        class Interface(object):

            @mock_method
            def foo(self, a, b, c=1, d=None):
                pass

            @mock_method
            def bar(self):
                pass

        self.iface = Interface()

    def test_whenMockCalledWithNoExpectationsSet_passWithWarning(self):
        self.iface.foo(1, 2)

    def test_whenMockCalledWithExpectationsSetForOtherMock_passWithWarning(self):
        self.iface.bar.expectCall()
        self.iface.foo(1, 3)

    def test_whenExpectedMockCalled_pass(self):
        self.iface.foo.expectCall(1, 2)
        self.iface.foo(1, 2)
        self.iface.foo.assertSaturated()

    def test_whenNoExpectationsSetForMockAndAssertSatisfiedCalled_pass(self):
        self.iface.foo.assertSaturated()
        self.iface.bar.assertSaturated()

    def test_whenExpectedMockCalled_assertSatisfiedWillPass(self):
        self.iface.foo.expectCall(1, 2)
        self.iface.foo(1, 2)
        self.iface.foo.assertSaturated()

    def test_whenTwoDifferentExpectationsGiven_bothMustBeSatisfied(self):
        self.iface.foo.expectCall(1, 2)
        self.iface.foo.expectCall(3, 4)

        self.iface.foo(3, 4)
        self.iface.foo(1, 2)

        self.iface.foo.assertSaturated()

    def test_whenExpectingToBeCalledTwiceAndMockCalledOnce_fail(self):
        self.iface.foo.expectCall(1, 2).times(2)
        self.iface.foo(1, 2)
        with self.assertRaisesRegexp(exc.MockUndersaturatedError, "Undersaturated mock function Interface.foo\(1, 2\):\nActual: called once\nExpected: to be called twice"):
            self.iface.foo.assertSaturated()

    def test_whenExpectationGivenOnceAndMockCalledTwice_fail(self):
        self.iface.foo.expectCall(1, 2)
        self.iface.foo(1, 2)
        with self.assertRaisesRegexp(exc.MockOversaturatedError, "Oversaturated mock function Interface.foo\(1, 2\):\nActual: called twice\nExpected: to be called once"):
            self.iface.foo(1, 2)

    def test_whenUnexpectedMockCalled_fail(self):
        self.iface.foo.expectCall(1, 2)
        with self.assertRaisesRegexp(exc.UnexpectedMockCallError, "Unexpected mock function called: Interface.foo\(1, 3\)"):
            self.iface.foo(1, 3)

    def test_whenExpectedMockNeverCalled_fail(self):
        self.iface.foo.expectCall(1, 2)
        with self.assertRaisesRegexp(exc.MockUndersaturatedError, "Undersaturated mock function Interface.foo\(1, 2\):\nActual: never called\nExpected: to be called once"):
            self.iface.foo.assertSaturated()

    def test_whenMockIsExpectedToBeNeverCalledAndItIsCalled_fail(self):
        self.iface.foo.expectCall(1, 2).times(0)
        with self.assertRaisesRegexp(exc.MockOversaturatedError, "Oversaturated mock function Interface.foo\(1, 2\):\nActual: called once\nExpected: to be never called"):
            self.iface.foo(1, 2)

    def test_whenMockIsExpectedToBeCalledTwiceAndItIsCalledThreeTimes_fail(self):
        self.iface.foo.expectCall(1, 2).times(2)
        self.iface.foo(1, 2)
        self.iface.foo(1, 2)
        with self.assertRaisesRegexp(exc.MockOversaturatedError, "Oversaturated mock function Interface.foo\(1, 2\):\nActual: called 3 times\nExpected: to be called twice"):
            self.iface.foo(1, 2)

    def test_whenMockIsExpectedToBeCalledTwiceAndItIsCalledOnce_fail(self):
        self.iface.foo.expectCall(1, 2).times(2)
        self.iface.foo(1, 2)
        with self.assertRaisesRegexp(exc.MockUndersaturatedError, "Undersaturated mock function Interface.foo\(1, 2\):\nActual: called once\nExpected: to be called twice"):
            self.iface.foo.assertSaturated()

    def test_whenGivingAnotherExpectationWhenExistingNotConsumed_fail(self):
        self.iface.bar.expectCall().times(2)
        with self.assertRaisesRegexp(exc.ExpectationNotConsumedError, "Trying to overwrite pending expectation for Interface.bar\(\)"):
            self.iface.bar.expectCall()

    def test_whenGivingAnotherExpectatioAfterExistingWasConsumed_pass(self):
        self.iface.bar.expectCall()
        self.iface.bar()
        self.iface.bar.expectCall().times(2)
        self.iface.bar()
        self.iface.bar()
        self.iface.bar.assertSaturated()

    def test_ifMustBeCalledAtLeastTwice_failsIfCalledOnce(self):
        self.iface.bar.expectCall().times(AtLeast(2))
        self.iface.bar()
        with self.assertRaisesRegexp(exc.MockUndersaturatedError, "Undersaturated mock function Interface.bar\(\):\nActual: called once\nExpected: to be called at least twice"):
            self.iface.bar.assertSaturated()

    def test_ifMustBeCalledAtLeastTwice_passesIfCalledTwice(self):
        self.iface.bar.expectCall().times(AtLeast(2))
        self.iface.bar()
        self.iface.bar()
        self.iface.bar.assertSaturated()

    def test_ifMustBeCalledAtLeastZeroTimes_passesEvenIfNotCalled(self):
        self.iface.bar.expectCall().times(AtLeast(0))
        self.iface.bar.assertSaturated()

    def test_ifMustBeCalledAtMostOnce_failsIfCalledTwice(self):
        self.iface.bar.expectCall().times(AtMost(1))
        self.iface.bar()
        with self.assertRaisesRegexp(exc.MockOversaturatedError, "Oversaturated mock function Interface.bar\(\):\nActual: called twice\nExpected: to be called at most once"):
            self.iface.bar()

    def test_ifMustBeCalledAtMostOnce_passesIfNeverCalled(self):
        self.iface.bar.expectCall().times(AtMost(1))
        self.iface.bar.assertSaturated()

    def test_ifMustBeCalledAtMostOnce_passesIfCalledOnce(self):
        self.iface.bar.expectCall().times(AtMost(1))
        self.iface.bar()
        self.iface.bar.assertSaturated()

    def test_ifExpectingToOnceReturnOne_passIfOneIsReturnedOnce(self):
        self.iface.foo.expectCall(1, 2).willOnce(Return(1))
        self.assertEqual(1, self.iface.foo(1, 2))
        self.iface.foo.assertSaturated()

    def test_ifExpectingToReturnOneAndTwoInARow_passIfOnceAndTwoReturned(self):
        self.iface.foo.expectCall(1, 2).\
            willOnce(Return(1)).\
            willOnce(Return(2))
        self.assertEqual(1, self.iface.foo(1, 2))
        self.assertEqual(2, self.iface.foo(1, 2))
        self.iface.foo.assertSaturated()

    def test_ifExpectingToReturnOneAndTwoInARow_failIfCalledOnce(self):
        self.iface.foo.expectCall(1, 2).willOnce(Return(1)).willOnce(Return(2))
        self.assertEqual(1, self.iface.foo(1, 2))
        with self.assertRaisesRegexp(exc.MockUndersaturatedError, "Undersaturated mock function Interface.foo\(1, 2\):\nActual: called once\nExpected: to be called twice"):
            self.iface.foo.assertSaturated()

    def test_ifExpectingToReturnOne_failIfCalledTwice(self):
        self.iface.bar.expectCall().willOnce(Return(1))
        self.assertEqual(1, self.iface.bar())
        with self.assertRaisesRegexp(exc.MockOversaturatedError, "Oversaturated mock function Interface.bar\(\):\nActual: called twice\nExpected: to be called once"):
            self.iface.bar()

    def test_ifExpectingToRepeatedlyInvokeCallback_invokeItAndReturnItsResultEachTimeCalled(self):

        def callback(a, b):
            return a + b

        self.iface.foo.expectCall(_, _).willRepeatedly(Invoke(callback))
        self.assertEqual(2, self.iface.foo(1, 1))
        self.assertEqual(3, self.iface.foo(1, 2))
        self.assertEqual(4, self.iface.foo(3, 1))
        self.iface.foo.assertSaturated()

    def test_willRepeatedlyIsOptional(self):
        self.iface.foo.expectCall(1, 2).willRepeatedly(Return(1))
        self.iface.foo.assertSaturated()

    def test_ifExpectingToOnceReturnOneAndThenRepeatedlyReturnTwo_passIfCalledOnce(self):
        self.iface.bar.expectCall().willOnce(Return(1)).willRepeatedly(Return(2))
        self.assertEqual(1, self.iface.bar())
        self.iface.bar.assertSaturated()

    def test_ifExpectingToOnceReturnOneAndThenRepeatedlyReturnTwo_passIfCalledThreeTimes(self):
        self.iface.bar.expectCall().willOnce(Return(1)).willRepeatedly(Return(2))
        self.assertEqual(1, self.iface.bar())
        self.assertEqual(2, self.iface.bar())
        self.assertEqual(2, self.iface.bar())
        self.iface.bar.assertSaturated()

    def test_ifExpectingToOnceReturnOneAndThenRepeatedlyReturnTwo_failIfNeverCalled(self):
        self.iface.bar.expectCall().willOnce(Return(1)).willRepeatedly(Return(2))
        with self.assertRaisesRegexp(exc.MockUndersaturatedError, "Undersaturated mock function Interface.bar\(\):\nActual: never called\nExpected: to be called at least once"):
            self.iface.bar.assertSaturated()
