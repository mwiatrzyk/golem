class MockTestCaseMixin(object):

    @property
    def mock_registry(self):
        if not hasattr(self, '_mock_registry'):
            self._mock_registry = set()
        return self._mock_registry

    def expectCall(self, func, *args, **kwargs):
        self.mock_registry.add(func)
        return func.expectCall(*args, **kwargs)

    def assertSaturated(self):
        for f in self.mock_registry:
            f.assertSaturated()
