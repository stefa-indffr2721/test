import sys
import zlib
from typing import Optional


def read_number(data: bytes, offset: int) -> int:
    """Читает 4 байта из data начиная с offset и возвращает число big-endian.

    Args:
        data: байтовая строка, из которой читается число.
        offset: позиция первого байта числа в data.

    Returns:
        целое число от 0 до 2^32−1.
    """
    b0 = data[offset]
    b1 = data[offset + 1]
    b2 = data[offset + 2]
    b3 = data[offset + 3]
    return b0 * 256**3 + b1 * 256**2 + b2 * 256 + b3


def predict_pixel(left: int, up: int, up_left: int) -> int:
    """Вычисляет предсказание пикселя по алгоритму Paeth из стандарта PNG.

    Возвращает тот из трёх соседних пикселей (left, up, up_left),
    который ближе всего к линейному предсказанию p = left + up − up_left.

    Args:
        left: значение пикселя слева от текущего.
        up: значение пикселя сверху от текущего.
        up_left: значение пикселя по диагонали (сверху-слева).

    Returns:
        предсказанное значение пикселя — одно из left, up или up_left.
    """
    p = left + up - up_left
    distance_a = abs(p - left)
    distance_b = abs(p - up)
    distance_c = abs(p - up_left)

    if distance_a <= distance_b and distance_a <= distance_c:
        return left
    elif distance_b <= distance_c:
        return up
    else:
        return up_left


def remove_filters(raw_data: bytes, width: int, bytes_per_pixel: int) -> list:
    """Убирает PNG-фильтры из сырых данных пикселей после декомпрессии.

    Каждая строка в raw_data начинается с байта типа фильтра (0–4),
    за которым следуют width * bytes_per_pixel байт данных пикселей.
    Функция применяет обратный фильтр к каждой строке согласно
    спецификации PNG.

    Args:
        raw_data: байты пиксельных данных с фильтрами,
                  полученные после zlib-декомпрессии IDAT-чанков.
        width: ширина изображения в пикселях.
        bytes_per_pixel: количество байт на один пиксель
                         (1 для серого, 2 для серого+альфа,
                          3 для RGB, 4 для RGBA и палитры).

    Returns:
        плоский список целых чисел от 0 до 255 —
        байты пикселей без фильтров, по строкам слева направо сверху вниз.
    """
    pixels_per_row = width * bytes_per_pixel
    result = []
    previous_row = [0] * pixels_per_row
    pos = 0

    while pos < len(raw_data):
        filter_type = raw_data[pos]
        pos += 1

        current_row = []
        for i in range(pixels_per_row):
            current_row.append(raw_data[pos + i])
        pos += pixels_per_row

        if filter_type == 0:
            pass

        elif filter_type == 1:
            for i in range(pixels_per_row):
                if i >= bytes_per_pixel:
                    left = current_row[i - bytes_per_pixel]
                else:
                    left = 0
                current_row[i] = (current_row[i] + left) % 256

        elif filter_type == 2:
            for i in range(pixels_per_row):
                current_row[i] = (current_row[i] + previous_row[i]) % 256

        elif filter_type == 3:
            for i in range(pixels_per_row):
                if i >= bytes_per_pixel:
                    left = current_row[i - bytes_per_pixel]
                else:
                    left = 0
                up = previous_row[i]
                current_row[i] = (current_row[i] + (left + up) // 2) % 256

        elif filter_type == 4:
            for i in range(pixels_per_row):
                if i >= bytes_per_pixel:
                    left = current_row[i - bytes_per_pixel]
                    up_left = previous_row[i - bytes_per_pixel]
                else:
                    left = 0
                    up_left = 0
                up = previous_row[i]
                predicted = predict_pixel(left, up, up_left)
                current_row[i] = (current_row[i] + predicted) % 256

        result.extend(current_row)
        previous_row = current_row

    return result


def grayscale(r: int, g: int, b: int) -> int:
    """Переводит RGB-цвет в значение яркости по формуле взвешенного среднего.

    Использует коэффициенты стандарта BT.601:
    gray = 0.299·R + 0.587·G + 0.114·B.

    Args:
        r: красная компонента цвета от 0 до 255.
        g: зелёная компонента цвета от 0 до 255.
        b: синяя компонента цвета от 0 до 255.

    Returns:
        яркость пикселя от 0 до 255.
    """
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    return round(gray)


def read_png(path: str) -> Optional[tuple]:
    """Читает PNG-файл и возвращает пиксели с размерами изображения.

    Поддерживает следующие типы цвета PNG:
    - 0: оттенки серого (1 байт на пиксель);
    - 2: RGB (3 байта на пиксель);
    - 3: индексированная палитра (1 байт на пиксель);
    - 4: оттенки серого с альфа-каналом (2 байта на пиксель);
    - 6: RGBA (4 байта на пиксель).

    Args:
        path: путь к PNG-файлу на диске.

    Returns:
        кортеж (pixels, width, height), где:
        - pixels — плоский список кортежей (gray, r, g, b),
          упорядоченных по строкам слева направо сверху вниз;
        - width — ширина изображения в пикселях;
        - height — высота изображения в пикселях.
        Возвращает None если файл использует interlace-режим
        или bit depth, отличный от 8.

    Raises:
        SystemExit: если файл не является корректным PNG,
                    использует interlaced-режим или bit depth != 8.
    """
    file = open(path, "rb")
    data = file.read()
    file.close()

    png_signature = b"\x89PNG\r\n\x1a\n"
    if data[:8] != png_signature:
        print("ошибка: это не png файл")
        sys.exit(1)

    chunks = []
    pos = 8
    while pos < len(data):
        length = read_number(data, pos)
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        chunks.append((chunk_type, chunk_data))
        pos = pos + 12 + length

    ihdr_data = None
    for chunk_type, chunk_data in chunks:
        if chunk_type == b"IHDR":
            ihdr_data = chunk_data
            break

    width = read_number(ihdr_data, 0)
    height = read_number(ihdr_data, 4)
    bit_depth = ihdr_data[8]
    color_type = ihdr_data[9]
    interlace = ihdr_data[12]

    if interlace != 0:
        print("ошибка: interlaced png не поддерживается")
        return None

    if bit_depth != 8:
        print("ошибка: поддерживается только bit depth = 8")
        return None

    palette = []
    for chunk_type, chunk_data in chunks:
        if chunk_type == b"PLTE":
            i = 0
            while i < len(chunk_data):
                r = chunk_data[i]
                g = chunk_data[i + 1]
                b = chunk_data[i + 2]
                palette.append((r, g, b))
                i += 3

    compressed_data = b""
    for chunk_type, chunk_data in chunks:
        if chunk_type == b"IDAT":
            compressed_data = compressed_data + chunk_data

    raw_pixels = zlib.decompress(compressed_data)

    if color_type == 0:
        bytes_per_pixel = 1
    elif color_type == 2:
        bytes_per_pixel = 3
    elif color_type == 3:
        bytes_per_pixel = 1
    elif color_type == 4:
        bytes_per_pixel = 2
    elif color_type == 6:
        bytes_per_pixel = 4

    flat_pixels = remove_filters(raw_pixels, width, bytes_per_pixel)

    pixels = []
    i = 0
    while i < len(flat_pixels):
        if color_type == 0:
            gray = flat_pixels[i]
            r, g, b = gray, gray, gray

        elif color_type == 2:
            r = flat_pixels[i]
            g = flat_pixels[i + 1]
            b = flat_pixels[i + 2]
            gray = grayscale(r, g, b)

        elif color_type == 3:
            index = flat_pixels[i]
            r, g, b = palette[index]
            gray = grayscale(r, g, b)

        elif color_type == 4:
            gray_value = flat_pixels[i]
            alpha = flat_pixels[i + 1]
            gray = round(gray_value * alpha / 255)
            r, g, b = gray, gray, gray

        elif color_type == 6:
            r = flat_pixels[i]
            g = flat_pixels[i + 1]
            b = flat_pixels[i + 2]
            alpha = flat_pixels[i + 3]
            gray_value = grayscale(r, g, b)
            gray = round(gray_value * alpha / 255)
            r = round(r * alpha / 255)
            g = round(g * alpha / 255)
            b = round(b * alpha / 255)

        pixels.append((gray, r, g, b))
        i += bytes_per_pixel

    return pixels, width, height