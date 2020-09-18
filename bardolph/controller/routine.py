class Routine:
    def __init__(self, name, address=0):
        self._name = name
        self._address = address
        self._params = []

    @property
    def name(self):
        return self._name

    @property
    def params(self):
        return self._params

    def add_param(self, name):
        self._params.append(name)

    def has_param(self, name):
        return name in self._params

    def set_address(self, address):
        self._address = address

    def get_address(self):
        return self._address
