import sys
import zlib


def read_number(data, offset):
    b0 = data[offset]
    b1 = data[offset + 1]
    b2 = data[offset + 2]
    b3 = data[offset + 3]
    return b0 * 256**3 + b1 * 256**2 + b2 * 256 + b3


def predict_pixel(left, up, up_left):
    p = left + up - up_left # плавное изменение яркости
    distance_a = abs(p - left)
    distance_b = abs(p - up)
    distance_c = abs(p - up_left)

    if distance_a <= distance_b and distance_a <= distance_c:
        return left
    elif distance_b <= distance_c:
        return up
    else:
        return up_left


def remove_filters(raw_data, width, bytes_per_pixel):
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


def grayscale(r, g, b):
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    return round(gray)


def read_png(path):
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
        bytes_per_pixel = 1  # яркость
    elif color_type == 2:
        bytes_per_pixel = 3  # rgb
    elif color_type == 3:
        bytes_per_pixel = 1  # индекс в палитре
    elif color_type == 4:
        bytes_per_pixel = 2  # яркость и прозрачность
    elif color_type == 6:
        bytes_per_pixel = 4  # rgb + прозрачность

    flat_pixels = remove_filters(raw_pixels, width, bytes_per_pixel)

    pixels = []
    i = 0
    while i < len(flat_pixels):
        if color_type == 0: # уже серый
            gray = flat_pixels[i]
            r, g, b = gray, gray, gray

        elif color_type == 2: # rgb
            r = flat_pixels[i]
            g = flat_pixels[i + 1]
            b = flat_pixels[i + 2]
            gray = grayscale(r, g, b)

        elif color_type == 3: # индекс в палитре -> rgb
            index = flat_pixels[i]
            r, g, b = palette[index]
            gray = grayscale(r, g, b)

        elif color_type == 4: # яркость и прозрачность, накладываем на чёрный фон
            gray_value = flat_pixels[i]
            alpha = flat_pixels[i + 1]
            gray = round(gray_value * alpha / 255)
            r, g, b = gray, gray, gray

        elif color_type == 6: # rgb + прозрачность
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