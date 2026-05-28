import png_opener
from typing import Optional


def prepare(path_to_image: str, width: Optional[int], height: Optional[int]) -> list:
    """Читает PNG-файл и возвращает двумерный массив пикселей с масштабированием.

    Args:
        path_to_image: путь к PNG-файлу на диске.
        width: желаемая ширина результата в пикселях.
               Если None и height задан — вычисляется автоматически
               с сохранением пропорций.
        height: желаемая высота результата в пикселях.
                Если None и width задан — вычисляется автоматически
                с сохранением пропорций.

    Returns:
        двумерный список кортежей (gray, r, g, b), где gray — яркость
        от 0 до 255, r, g, b — цветовые компоненты от 0 до 255.
        Размер списка соответствует запрошенным width и height,
        либо исходному размеру изображения если оба параметра None.

    Raises:
        SystemExit: если файл не является корректным PNG.
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
    """Масштабирует двумерный массив пикселей методом ближайшего соседа.

    Если оба параметра width и height равны None, возвращает массив
    без изменений. Если задан только один из параметров — второй
    вычисляется автоматически с сохранением пропорций.

    Args:
        pixels_2d: исходный двумерный массив кортежей (gray, r, g, b).
        width_fact: фактическая ширина исходного изображения в пикселях.
        height_fact: фактическая высота исходного изображения в пикселях.
        width: целевая ширина результата в пикселях, или None.
        height: целевая высота результата в пикселях, или None.

    Returns:
        двумерный список кортежей (gray, r, g, b) размером width × height,
        либо исходный pixels_2d если оба параметра None.
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