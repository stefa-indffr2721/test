import unittest
from ansi_writer import AnsiWriter


class TestAnsiWriter(unittest.TestCase):

    def test_create(self):
        """ тест на то, что AnsiWriter cоздаётся без ошибок """
        writer = AnsiWriter()
        self.assertIsNotNone(writer)

    def test_write_empty(self):
        """ проверка на то не падает ли AnsiWriter при пустом массиве """
        writer = AnsiWriter()
        ascii_2d = []
        try:
            writer.write(ascii_2d)
            ok = True
        except:
            ok = False
        self.assertTrue(ok)

    def test_write_multiple_rows(self):
        """ проверка не падает ли writer при вводе нескольких строк """
        writer = AnsiWriter()
        ascii_2d = [
            [("@", 255, 0, 0), (".", 0, 255, 0)],
            [(" ", 0, 0, 255), ("#", 128, 128, 128)]
        ]
        try:
            writer.write(ascii_2d)
            ok = True
        except:
            ok = False
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()