from abc import ABC, abstractmethod


class Runtime(ABC):
    @abstractmethod
    def get_fns(self) -> dict:
        pass
