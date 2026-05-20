import unittest
import png_opener


class TestPngOpener(unittest.TestCase):

    def test_grayscale_black(self):
        """ проверка перевод из черного rgb в степень серости(яркости) """
        self.assertEqual(png_opener.grayscale(0, 0, 0), 0)

    def test_grayscale_white(self):
        """ то же самое только для белого """
        self.assertEqual(png_opener.grayscale(255, 255, 255), 255)

    def test_predict_pixel_left(self):
        """ проверка на то что левый пиксель больше всего подходит """
        self.assertEqual(png_opener.predict_pixel(10, 100, 100), 10)

    def test_predict_pixel_up(self):
        """ то же самое, но для верхнего пикселя """
        self.assertEqual(png_opener.predict_pixel(100, 10, 100), 10)

    def test_predict_pixel_up_left(self):
        """ то же самое, но для верхне-левого пикселя """
        self.assertEqual(png_opener.predict_pixel(50, 50, 10), 50)

    def test_read_number(self):
        """ проверка перевода кортежа 4 байт в число """
        data = bytes([0, 0, 1, 0])
        self.assertEqual(png_opener.read_number(data, 0), 256)

    def test_remove_filters_type_0(self):
        """ проверяет что фильтр 0 не меняет данные """
        raw = bytes([0, 10, 20, 30])
        result = png_opener.remove_filters(raw, width=3, bytes_per_pixel=1)
        self.assertEqual(result, [10, 20, 30])

    def test_remove_filters_type_1(self):
        """ проверяет фильтр с учетом левого пикселя """
        raw = bytes([1, 10, 10, 10])
        result = png_opener.remove_filters(raw, width=3, bytes_per_pixel=1)
        self.assertEqual(result, [10, 20, 30])

    def test_remove_filters_type_2(self):
        """ проверяет фильтр с учетом предыдущей строки """
        raw = bytes([0, 10, 10, 10, 2, 1, 1, 1])
        result = png_opener.remove_filters(raw, width=3, bytes_per_pixel=1)
        self.assertEqual(result, [10, 10, 10, 11, 11, 11])


if __name__ == "__main__":
    unittest.main()