from golem import _utils


class TimesBase(object):

    def __init__(self, expected):
        self.actual = 0
        self.expected = expected

    def __iadd__(self, other):
        self.actual += other
        return self


class Exactly(TimesBase):

    def __str__(self):
        if self.expected == 0:
            return 'to be never called'
        else:
            return 'to be called %s' % _utils.number_of_times_to_string(self.expected)

    def __eq__(self, other):
        return self.expected == other

    def is_undersaturated(self):
        return self.expected > self.actual

    def is_oversaturated(self):
        return self.expected < self.actual


class AtLeast(TimesBase):

    def __str__(self):
        return 'to be called at least %s' % _utils.number_of_times_to_string(self.expected)

    def is_undersaturated(self):
        return self.expected > self.actual

    def is_oversaturated(self):
        return False


class AtMost(TimesBase):

    def __str__(self):
        return 'to be called at most %s' % _utils.number_of_times_to_string(self.expected)

    def is_undersaturated(self):
        return False

    def is_oversaturated(self):
        return self.expected < self.actual
