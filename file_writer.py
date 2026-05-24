from abstract_writer import AbstractWriter


class FileWriter(AbstractWriter):

    def __init__(self, filepath: str) -> None:
        """Принимает путь к файлу для записи."""
        self.filepath = filepath

    def write(self, ascii_2d: list) -> None:
        """Записывает ASCII-арт в текстовый файл."""
        result = ""
        for row in ascii_2d:
            line = ""
            for pixel in row:
                char = pixel[0]
                line = line + char * 2
            result += line + "\n"

        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(result)