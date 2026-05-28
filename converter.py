def convert(pixels_2d: list, charset: str) -> list:
    """Переводит двумерный массив пикселей в ASCII-арт.

    Для каждого пикселя выбирает символ из charset пропорционально
    яркости: тёмные пиксели получают символы из начала строки,
    светлые — из конца.

    Args:
        pixels_2d: двумерный список кортежей (gray, r, g, b),
                   где gray — яркость от 0 до 255,
                   r, g, b — цветовые компоненты от 0 до 255.
        charset: строка символов, упорядоченных от тёмного к светлому,
                 длиной не менее 2 символов.

    Returns:
        двумерный список кортежей (символ, r, g, b) той же формы,
        что и входной pixels_2d.
    """
    dim = len(charset) - 1

    ascii_2d = []
    for row in pixels_2d:
        ascii_row = []
        for (gray, r, g, b) in row:
            char = charset[int(gray / 255 * dim)]
            ascii_row.append((char, r, g, b))
        ascii_2d.append(ascii_row)

    return ascii_2d