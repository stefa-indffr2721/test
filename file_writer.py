from abstract_writer import AbstractWriter


class FileWriter(AbstractWriter):

    def __init__(self, filepath: str) -> None:
        """Инициализирует writer с путём к файлу для записи.

        Args:
            filepath: путь к текстовому файлу, в который будет
                      сохранён ASCII-арт. Файл будет создан или
                      перезаписан при вызове write().
        """
        self.filepath = filepath

    def write(self, ascii_2d: list) -> None:
        """Записывает ASCII-арт в текстовый файл.

        Каждый символ дублируется для компенсации прямоугольной
        формы символов. Цветовые компоненты кортежей игнорируются.
        Строки разделяются символом новой строки.

        Args:
            ascii_2d: двумерный список строк, каждая строка —
                      список кортежей (символ, r, g, b).

        Raises:
            OSError: если файл не удалось открыть или записать.
        """
        result = ""
        for row in ascii_2d:
            line = ""
            for pixel in row:
                char = pixel[0]
                line = line + char * 2
            result += line + "\n"

        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(result)