import unittest
import os
from file_writer import FileWriter


class TestFileWriter(unittest.TestCase):

    def setUp(self):
        self.temp_file = "temp_file_writer_test.txt"

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_create(self):
        """ тест на то, что FileWriter создаётся без ошибок """
        writer = FileWriter(self.temp_file)
        self.assertIsNotNone(writer)

    def test_write_empty(self):
        """ проверка на то не падает ли FileWriter при пустом массиве """
        writer = FileWriter(self.temp_file)
        ascii_2d = []
        try:
            writer.write(ascii_2d)
            ok = True
        except:
            ok = False
        self.assertTrue(ok)

    def test_write_multiple_rows(self):
        """ проверка не падает ли writer при вводе нескольких строк """
        writer = FileWriter(self.temp_file)
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