import inspect
import warnings
import collections

from golem import exc
from golem.times import Exactly, AtLeast


class mock_method(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype):
        return MockMethod(obj, self.func)


class MockMethod(object):

    def __init__(self, obj, func):
        self.obj = obj
        self.func = func

    def __call__(self, *args, **kwargs):
        call = MockMethodCall(self, args, kwargs)
        if not self.expectations:
            warnings.warn("Uniterested mock function called: %s" % call, exc.GolemWarning)
            return
        expectation = self.expectations.get(call)
        if expectation is None:
            raise exc.UnexpectedMockCallError(call)
        result = expectation.consume(call)
        if expectation.is_oversaturated():
            raise exc.MockOversaturatedError(call, expectation)
        return result

    def __eq__(self, other):
        return self.obj == other.obj and\
            self.func == other.func

    def decode(self, *args, **kwargs):
        spec = inspect.getargspec(self.func)
        spec_args = spec.args[1:]
        spec_defaults = spec.defaults or []
        required_args = spec_args[:-len(spec_defaults)] if spec_defaults else spec_args
        for k in kwargs:
            if k not in spec_args:
                raise TypeError("%s() got an unexpected keyword argument %r" % (self.func_name, k))
        if args and not spec_args:
            raise TypeError("%s() takes no arguments (%d given)" % (self.func_name, len(args)))
        elif len(args) > len(spec_args):
            raise TypeError(self.__render_invalid_number_of_args_message(args, required_args, spec_defaults))
        elif len(args) != len(required_args):
            raise TypeError(self.__render_invalid_number_of_args_message(args, required_args, spec_defaults))

    def __render_invalid_number_of_args_message(self, given, required, default):
        tmp = ["%s() takes" % self.func_name]
        if default and len(given) > len(required) + len(default):
            tmp.append('at most %d' % (len(required) + len(default)))
        else:
            tmp.append(('at least %d' if default else 'exactly %d') % len(required))
        tmp.append('argument' if len(required) == 1 else 'arguments')
        tmp.append("(%d given)" % len(given))
        return ' '.join(tmp)

    def expectCall(self, *args, **kwargs):
        call = MockMethodCall(self, args, kwargs)
        if call in self.expectations:
            if not self.expectations[call].is_saturated():
                raise exc.ExpectationNotConsumedError(call)
        self.expectations[call] = expectation = Expectation()
        return expectation

    def assertSaturated(self):
        for call, expectation in self.expectations.iteritems():
            if expectation.is_undersaturated():
                raise exc.MockUndersaturatedError(call, expectation)

    @property
    def expectations(self):
        if not hasattr(self.obj, '_mock_expectations'):
            self.obj._mock_expectations = {}
        return self.obj._mock_expectations.setdefault(self.func, {})

    @property
    def func_name(self):
        return "%s.%s" % (self.obj.__class__.__name__, self.func.func_name)


class MockMethodCall(object):

    def __init__(self, method, args, kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        return self.method == other.method and\
            self.args == other.args and\
            self.kwargs == other.kwargs

    def __hash__(self):
        return 1

    def __str__(self):
        tmp = []
        if self.args:
            tmp.append(', '.join(repr(x) for x in self.args))
        if self.kwargs:
            tmp.append(', '.join("%s=%r" % (k, v) for k, v in sorted(self.kwargs.iteritems())))
        return "%s(%s)" % (self.method.func_name, ', '.join(tmp))

    def __repr__(self):
        return str(self)


class Expectation(object):

    def __init__(self):
        self._times = Exactly(1)
        self._single_actions = collections.deque()
        self._repeatable_action = None

    def consume(self, call):
        self._times += 1
        action = self.__consume_action()
        if action is not None:
            return action(call)

    def __consume_action(self):
        if self._single_actions:
            return self._single_actions.popleft()
        elif self._repeatable_action:
            return self._repeatable_action
        else:
            return None

    def times(self, times):
        if isinstance(times, int):
            self._times = Exactly(times)
        else:
            self._times = times

    def willOnce(self, action):
        self._single_actions.append(action)
        self._times = Exactly(len(self._single_actions))
        return self

    def willRepeatedly(self, action):
        self._times = AtLeast(len(self._single_actions))
        self._repeatable_action = action

    def is_undersaturated(self):
        return self._times.is_undersaturated()

    def is_oversaturated(self):
        return self._times.is_oversaturated()

    def is_saturated(self):
        return not self.is_oversaturated() and\
            not self.is_undersaturated()

    @property
    def actual_calls(self):
        return self._times.actual

    @property
    def expected_calls(self):
        return self._times
