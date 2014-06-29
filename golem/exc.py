from golem import _utils


class GolemWarning(Warning):
    pass


class UnexpectedMockCallError(AssertionError):

    def __init__(self, call):
        self.call = call

    def __str__(self):
        return "Unexpected mock function called: %s" % self.call


class ExpectationNotConsumedError(AssertionError):

    def __init__(self, call):
        self.call = call

    def __str__(self):
        return "Trying to overwrite pending expectation for %s" % self.call


class MockSaturationError(AssertionError):

    def __init__(self, call, expectation):
        self.call = call
        self.expectation = expectation

    @property
    def actual_calls(self):
        if self.expectation.actual_calls == 0:
            return 'never called'
        else:
            return 'called %s' % _utils.number_of_times_to_string(self.expectation.actual_calls)

    @property
    def expected_calls(self):
        return str(self.expectation.expected_calls)


class MockOversaturatedError(MockSaturationError):

    def __str__(self):
        return "Oversaturated mock function %s:\n"\
            "Actual: %s\n"\
            "Expected: %s" % (self.call, self.actual_calls, self.expected_calls)


class MockUndersaturatedError(MockSaturationError):

    def __str__(self):
        return "Undersaturated mock function %s:\n"\
            "Actual: %s\n"\
            "Expected: %s" % (self.call, self.actual_calls, self.expected_calls)
