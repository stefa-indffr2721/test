from abc import ABC, abstractmethod


class AbstractWriter(ABC):
    @abstractmethod
    def write(self, data: list) -> None:
        """Записывает ASCII-арт в целевой вывод.

        Args:
            data: двумерный список кортежей (символ, r, g, b),
                  где каждый кортеж представляет один пиксель ASCII-арта.
        """
        pass