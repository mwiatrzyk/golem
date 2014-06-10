class ExpectCallMixin(object):

    def expectCall(self, method, *args, **kwargs):
        raise TypeError("'expectCall' used with non-mock method")
