import unittest
import os
import main


class FakeArgs:
    set = None


class FakeVideoArgs:
    input = "1h.mp4"
    wight = 20
    height = 20
    set = None


class TestGetCharset(unittest.TestCase):

    def setUp(self):
        self.temp_file = "temp_charset_test.txt"

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_default(self):
        """ если файл с символами не указан, то возвращаем CHARSET """
        args = FakeArgs()
        args.set = None
        result = main.get_charset(args)
        self.assertEqual(result, main.CHARSET)

    def test_from_file(self):
        """ если файл с символами указан, то берем CHARSET из него"""
        with open(self.temp_file, "w") as f:
            f.write(" @\n")
        args = FakeArgs()
        args.set = self.temp_file
        result = main.get_charset(args)
        self.assertEqual(result, " @")

    def test_empty_file(self):
        """ если файл с набором символов пуст, то завершаем программу с ошибкой """
        with open(self.temp_file, "w") as f:
            f.write("")
        args = FakeArgs()
        args.set = self.temp_file
        with self.assertRaises(SystemExit):
            main.get_charset(args)


class TestPrintTo(unittest.TestCase):

    def setUp(self):
        self.temp_file = "temp_print_to_test.txt"
        self.image = [[("@", 255, 0, 0), (".", 0, 255, 0)]]

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_print_to_console(self):
        """ проверка, что print_to не падает при выводе в консоль """
        main.print_to(self.image, None, False)

    def test_print_to_file(self):
        """ проверка, что print_to сохраняет в файл """
        main.print_to(self.image, self.temp_file, False)
        self.assertTrue(os.path.exists(self.temp_file))

    def test_print_ansi(self):
        """ проверка, что print_to не падает при ansi выводе """
        main.print_to(self.image, None, True)


class TestPlayVideo(unittest.TestCase):

    def test_play_video(self):
        """ проверка, что play_video не падает при работе с реальным видеофайлом """
        main.play_video(FakeVideoArgs(), main.CHARSET)


if __name__ == "__main__":
    unittest.main()