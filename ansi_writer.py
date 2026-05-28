from abstract_writer import AbstractWriter


class AnsiWriter(AbstractWriter):
    def write(self, ascii_2d: list) -> None:
        """Выводит ASCII-арт в терминал с цветом через ANSI escape-коды.

        Каждый символ выводится дважды подряд для компенсации
        прямоугольной формы символов. Цвет меняется только при
        переходе к пикселю с другим RGB, чтобы минимизировать
        количество escape-последовательностей.

        Args:
            ascii_2d: двумерный список строк, каждая строка —
                      список кортежей (символ, r, g, b).
        """
        for row in ascii_2d:
            line = ""
            prev_r, prev_g, prev_b = -1, -1, -1
            for (char, r, g, b) in row:
                if r != prev_r or g != prev_g or b != prev_b:
                    line = line + "\033[38;2;" + str(r) + ";" + str(g) + ";" + str(b) + "m"
                    prev_r, prev_g, prev_b = r, g, b
                line = line + char * 2
            line = line + "\033[0m"
            print(line)