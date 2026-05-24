import png_opener
from typing import Optional


def prepare(path_to_image: str, width: Optional[int], height: Optional[int]) -> list:
    """
    Читает png файл и возвращает двумерный массив пикселей.
    Если указаны width или height, то масштабирует изображение.
    """
    (pixels, width_fact, height_fact) = png_opener.read_png(path_to_image)

    pixels_2d = []
    for y in range(height_fact):
        start = y * width_fact
        end = (y + 1) * width_fact
        row = pixels[start:end]
        pixels_2d.append(row)

    pixels_2d = resize(pixels_2d, width_fact, height_fact, width, height)

    return pixels_2d


def resize(pixels_2d: list, width_fact: int, height_fact: int, width: Optional[int], height: Optional[int]) -> list:
    """
    Масштабирует двумерный массив пикселей до нужного размера.
    Если width или height равны None — считает их автоматически сохраняя пропорции.
    Если оба None, то возвращает массив без изменений.
    """
    if width is None and height is None:
        return pixels_2d

    if width is None:
        width = round(height * width_fact / height_fact)
    if height is None:
        height = round(width * height_fact / width_fact)

    result = []
    for y in range(height):
        src_y = int(y / height * height_fact)
        row = []
        for x in range(width):
            src_x = int(x / width * width_fact)
            row.append(pixels_2d[src_y][src_x])
        result.append(row)
    return result