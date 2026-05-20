import sys
import argparse
import time
import os.path

import handling
import converter
import console_writer
from file_writer import FileWriter
from ansi_writer import AnsiWriter
import video_reader

CHARSET = " .+*=#@"

def get_args():
    parser = argparse.ArgumentParser(prog="ASCII-Art")
    parser.add_argument("-i", "--input", type=str, default=None, help="входное изображение или видео")
    parser.add_argument("-w", "--wight",  type=int, default=None, help="ширина выходного изображения (в символах)")
    parser.add_argument("-H", "--height",  type=int, default=None, help="высота выходного изображения (в символах)")
    parser.add_argument("-s", "--set",  type=str, default=None, help="множество символов (файл)")
    parser.add_argument("-o", "--output", type=str, default=None, help="путь к выходному файлу, если не указано - то на консоль")
    parser.add_argument("-a", "--ansi", action="store_true", help="цветной вывод в терминал (ANSI)")
    parser.add_argument("-v", "--video", action="store_true", help="режим видео")

    args = parser.parse_args()

    if not args.output is None and args.video:
        print("Вывод видео в файл невозможен!")
        sys.exit(1)

    if args.set == "":
        parser.print_help()
        sys.exit(1)
    if not args.input is None:
        try:
            f = open(args.input)
            f.close()
        except FileNotFoundError:
            print("указанный входной файл не найден")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    return args


def print_to(image, path, ansi):
    if ansi and path:
        print("Цветной вывод в файл невозможен")
        sys.exit(1)
    if ansi:
        writer = AnsiWriter()
        writer.write(image)
    elif path is not None:
        writer = FileWriter(path)
        writer.write(image)
    else:
        writer = console_writer.ConsoleWriter()
        writer.write(image)


def get_charset(args):
    if not args.set is None:
        if not os.path.exists(str(args.set)):
            print("файл указанный как charset - не существует")
            sys.exit(1)

    if not args.set is None:
        with open(args.set) as f:
            charset = f.readline().replace("\n", "")
            if len(charset) == 0:
                print("файл указанный как charset - пуст")
                sys.exit(1)
    else:
        charset = CHARSET

    return charset


def play_video(args, charset):
    KADR = 1
    print("Читаем видео")
    frames, fps = video_reader.read_video(args.input, KADR)

    delay = 1.0 / fps * KADR

    print("Обработка кадров")
    processed_frames = []
    for frame_path in frames:
        image = handling.prepare(frame_path, args.wight, args.height)
        image_ascii = converter.convert(image, charset)
        processed_frames.append(image_ascii)

    video_reader.delete_temp(frames)

    print("ПОЕХАЛИИИИИИИ!!!!!")
    time.sleep(1)

    writer = AnsiWriter()
    for frame in processed_frames:
        print("\033[H\033[J", end="")
        print("\033[" + str(len(frame)) + "A", end="")
        writer.write(frame)
        time.sleep(delay)

    print("\033[H\033[J", end="")


def main():
    args = get_args()
    charset = get_charset(args)

    if args.video:
        play_video(args, charset)
    else:
        image = handling.prepare(args.input, args.wight, args.height)
        image_ASCII = converter.convert(image, charset)
        print_to(image_ASCII, args.output, args.ansi)


if __name__ == "__main__":
    main()