from abstract_writer import AbstractWriter


class ConsoleWriter(AbstractWriter):
    def write(self, ascii_2d: list) -> None:
        """Выводит ASCII-арт в консоль без цвета."""
        for row in ascii_2d:
            line = ""
            for (char, r, g, b) in row:
                line = line + char * 2
            print(line)