from abc import ABC, abstractmethod


class AbstractWriter(ABC):
    @abstractmethod
    def write(self, data: list) -> None:
        """Записывает ASCII-арт, реализуется в дочерних классах."""
        pass