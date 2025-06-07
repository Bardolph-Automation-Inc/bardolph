from collections import OrderedDict

class Cache:
    def __init__(self, capacity=2048):
        self._capacity = capacity
        self._cache = OrderedDict()

    def get(self, key):
        return self._cache.get(key, None)

    def put(self, key, value):
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self._capacity:
            self._cache.popitem(last=True)
        self._cache[key] = value
