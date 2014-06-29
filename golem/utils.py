import inspect


def number_of_times_to_string(value):
    if value == 0:
        return 'never'
    elif value == 1:
        return 'once'
    elif value == 2:
        return 'twice'
    else:
        return "%s times" % value


class FunctionInspector(object):

    def __init__(self, func):
        self.func = func
        self._argspec = inspect.getargspec(func)

    def decode_call(self, *args, **kwargs):
        spec = inspect.getargspec(self.func)
        spec_args = spec.args[1:]
        spec_defaults = spec.defaults or []
        required_args = spec_args[:-len(spec_defaults)] if spec_defaults else spec_args
        for k in kwargs:
            if k not in spec_args:
                raise TypeError("%s() got an unexpected keyword argument %r" % (self.func.func_name, k))
        if args and not spec_args:
            raise TypeError("%s() takes no arguments (%d given)" % (self.func.func_name, len(args)))
        elif len(args) > len(spec_args):
            raise TypeError(self.__render_invalid_number_of_args_message(args, required_args, spec_defaults))
        elif len(args) != len(required_args):
            raise TypeError(self.__render_invalid_number_of_args_message(args, required_args, spec_defaults))

    def __render_invalid_number_of_args_message(self, given, required, default):
        tmp = ["%s() takes" % self.func.func_name]
        if default and len(given) > len(required) + len(default):
            tmp.append('at most %d' % (len(required) + len(default)))
        else:
            tmp.append(('at least %d' if default else 'exactly %d') % len(required))
        tmp.append('argument' if len(required) == 1 else 'arguments')
        tmp.append("(%d given)" % len(given))
        return ' '.join(tmp)
