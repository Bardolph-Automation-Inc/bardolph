import re

from . import i_lib


class TimePattern(i_lib.TimePattern):
    HOURS_24 = set(range(0, 24))
    MINUTES_60 = set(range(0, 60))
    REGEX_SPEC = r'(\*|\*\d|\d\*|\d\d?):(\d\d|\d\*|\*\d|\*)(?=(\s|$))'
    REGEX = re.compile(REGEX_SPEC)

    def __init__(self, hours, minutes):
        self._repr = 'TimePattern("{}", "{}")'.format(hours, minutes)
        self._hour_set, self._minute_set = set(), set()
        if hours and minutes:
            self._init_hour_set(hours)
            self._init_minute_set(minutes)

    def __repr__(self):
        return self._repr

    @staticmethod
    def from_string(pattern):
        the_match = TimePattern.REGEX.match(pattern)
        if the_match is not None:
            hours, minutes, *_ = the_match.groups()
            if TimePattern.patterns_valid(hours, minutes):
                return TimePattern(hours, minutes)
        return TimePattern(None, None)

    @staticmethod
    def patterns_valid(hours, minutes):
        return (TimePattern.hours_valid(hours)
                and TimePattern.minutes_valid(minutes))

    @staticmethod
    def hours_valid(hours):
        if hours == '*':
            return True
        if len(hours) not in (1, 2):
            return False
        if hours[0] == '*':
            return hours[1].isdigit()
        if len(hours) == 2 and hours[1] == '*':
            return hours[0] in '012'
        if not hours.isdecimal():
            return False
        int_hours = int(hours)
        return 0 <= int_hours < 25

    @staticmethod
    def minutes_valid(minutes):
        if minutes == '*':
            return True
        if len(minutes) != 2:
            return False
        if minutes[0] == '*':
            return minutes[1].isdigit()
        if minutes[1] == '*':
            return minutes[0] in '012345'
        if not minutes.isdecimal():
            return False
        int_minutes = int(minutes)
        return 0 <= int_minutes < 60

    def union(self, other):
        self._hour_set.update(other._hour_set)
        self._minute_set.update(other._minute_set)

    def match(self, hours, minutes):
        return hours in self._hour_set and minutes in self._minute_set

    def _init_hour_set(self, pattern):
        if pattern == '*':
            self._hour_set = TimePattern.HOURS_24.copy()
        elif len(pattern) == 1:
            self._hour_set = set([int(pattern)])
        else:
            self._hour_set = set()
            for hour in range(0, 24):
                if self._number_match(hour, pattern):
                    self._hour_set.add(hour)

    def _init_minute_set(self, pattern):
        if pattern == '*':
            self._minute_set = TimePattern.MINUTES_60.copy()
        else:
            self._minute_set = set()
            for minute in range(0, 59):
                if TimePattern._number_match(minute, pattern):
                    self._minute_set.add(minute)

    @staticmethod
    def _number_match(number, pattern) -> bool:
        formatted = "{:02d}".format(number)
        return (formatted == pattern
                or (pattern[0] in ('*', formatted[0])
                    and pattern[1] in ('*', formatted[1])))
