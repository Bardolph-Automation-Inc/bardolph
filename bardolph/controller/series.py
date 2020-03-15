class Series:
    def __init__(self, first=0, delta=0):
        self._first = first
        self._delta = delta
        self._iter = iter(SeriesIter(self).values())

    def init(self, first, delta):
        self.__init__(first, delta)
        self._iter = iter(SeriesIter(self).values())
        
    @property
    def first(self):
        return self._first
    
    @property
    def delta(self):
        return self._delta
   
    def next(self):
        return self._iter.__next__()


class SeriesIter:
    def __init__(self, series):
        self._first = series.first
        self._current = series.first
        self._delta = series.delta
        
    def values(self):
        self._current = self._first
        yield self._first

        while True:
            self._current += self._delta
            yield self._current
