class Return(object):

    def __init__(self, what):
        self.what = what

    def __call__(self, *args, **kwargs):
        return self.what


class Invoke(object):

    def __init__(self, callback):
        self.callback = callback

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)
