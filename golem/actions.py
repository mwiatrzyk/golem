class Return(object):

    def __init__(self, what):
        self.what = what

    def __call__(self, call):
        return self.what


class Invoke(object):

    def __init__(self, callback):
        self.callback = callback

    def __call__(self, call):
        return self.callback(*call.args, **call.kwargs)
