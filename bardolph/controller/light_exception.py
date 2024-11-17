class LightException(Exception):
    def __init__(self, cause):
        super().__init__('Exception from light API {}'.format(cause))
        self._cause = cause

    @property
    def cause(self):
        return self._cause


class NotImplementedException(LightException):
    def __init__(self, feature):
        super().__init__('Feature not available: {}'.format(feature))

