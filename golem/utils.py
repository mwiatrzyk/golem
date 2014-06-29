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

    def normalize(self, *args, **kwargs):
        self.__validate(args, kwargs)
        return self.__create_normalization_result(args, kwargs)

    def __validate(self, args, kwargs):
        given = len(args) + len(kwargs)
        for k in kwargs:
            if k not in self.arg_names:
                raise TypeError("%s() got an unexpected keyword argument %r" % (self.func.func_name, k))
        if len(args) == len(self.arg_names_required):
            for k in kwargs:
                if k in self.arg_names_required:
                    raise TypeError("%s() got multiple values for keyword argument %r" % (self.func.func_name, k))
        if args and not self.arg_names:
            raise TypeError("%s() takes no arguments (%d given)" % (self.func.func_name, len(args)))
        elif given > len(self.arg_names):
            raise TypeError(self.__render_too_many_arguments_error(given))
        elif given < len(self.arg_names_required):
            raise TypeError(self.__render_too_few_arguments_error(given))

    def __create_normalization_result(self, args, kwargs):
        result = dict(zip(self.arg_names_required, args))
        result.update(self.arg_defaults)
        result.update(kwargs)
        return result

    def __render_too_many_arguments_error(self, given):
        tmp = ["%s() takes" % self.func.func_name]
        tmp.append(('at most %d' if self.min_args != self.max_args else 'exactly %d') % self.max_args)
        tmp.append('argument' if self.min_args == 1 else 'arguments')
        tmp.append("(%d given)" % given)
        return ' '.join(tmp)

    def __render_too_few_arguments_error(self, given):
        tmp = ["%s() takes" % self.func.func_name]
        tmp.append(('at least %d' if self.min_args != self.max_args else 'exactly %d') % self.min_args)
        tmp.append('argument' if self.min_args == 1 else 'arguments')
        tmp.append("(%d given)" % given)
        return ' '.join(tmp)

    @property
    def arg_names(self):
        return tuple(self._argspec.args)

    @property
    def arg_names_required(self):
        if not self.arg_defaults:
            return self.arg_names
        return self.arg_names[:-len(self.arg_defaults)]

    @property
    def arg_defaults(self):
        if not self._argspec.defaults:
            return {}
        default_arg_names = self.arg_names[-len(self._argspec.defaults):]
        return dict(zip(default_arg_names, self._argspec.defaults))

    @property
    def min_args(self):
        return len(self.arg_names_required)

    @property
    def max_args(self):
        return len(self.arg_names)
