from abc import ABC, abstractmethod
from typing import Any


class Clock(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def wait_until(self):
        pass

    @abstractmethod
    def pause_for(self, delay) -> None:
        pass


class Settings(ABC):
    def get_value(self, name: str, default: Any = None) -> Any:
        return self._config.get(name, default)


class TimePattern(ABC):
    @abstractmethod
    def match(self, hour, minute):
        pass


class LogConfig(ABC):
    pass


class Output(ABC):
    @abstractmethod
    def out(self, output) -> None:
        pass

    @abstractmethod
    def newline(self) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass
