import unittest
import handling


class TestResize(unittest.TestCase):

    def make_pixels(self, width, height):
        pixels_2d = []
        for y in range(height):
            row = []
            for x in range(width):
                gray = (x + y) % 256
                row.append((gray, gray, gray, gray))
            pixels_2d.append(row)
        return pixels_2d

    def test_no_args(self):
        """ если ширина и высота не указаны, то возвращаем массив без изменений """
        pixels_2d = self.make_pixels(10, 5)
        result = handling.resize(pixels_2d, 10, 5, None, None)
        self.assertEqual(len(result), 5)
        self.assertEqual(len(result[0]), 10)

    def test_width_and_height(self):
        """ если ширина и высота указаны, то меняем размер """
        pixels_2d = self.make_pixels(100, 50)
        result = handling.resize(pixels_2d, 100, 50, 20, 10)
        self.assertEqual(len(result), 10)
        self.assertEqual(len(result[0]), 20)

    def test_only_width(self):
        """ если указана только ширина, то высоту считаем автоматически """
        pixels_2d = self.make_pixels(100, 50)
        result = handling.resize(pixels_2d, 100, 50, 50, None)
        self.assertEqual(len(result[0]), 50)
        self.assertEqual(len(result), 25)

    def test_only_height(self):
        """ если указана только высота, то ширину считаем автоматически """
        pixels_2d = self.make_pixels(100, 50)
        result = handling.resize(pixels_2d, 100, 50, None, 25)
        self.assertEqual(len(result), 25)
        self.assertEqual(len(result[0]), 50)

    def test_upscale(self):
        """ тест про увеличение размера арта"""
        pixels_2d = self.make_pixels(10, 5)
        result = handling.resize(pixels_2d, 10, 5, 20, 10)
        self.assertEqual(len(result), 10)
        self.assertEqual(len(result[0]), 20)


class TestPrepare(unittest.TestCase):

    def test_prepare_with_width(self):
        """ проверка, что prepare меняет ширину """
        result = handling.prepare("2.png", 10, None)
        self.assertEqual(len(result[0]), 10)

    def test_prepare_with_height(self):
        """ проверка, что prepare меняет высоту """
        result = handling.prepare("2.png", None, 5)
        self.assertEqual(len(result), 5)


if __name__ == "__main__":
    unittest.main()