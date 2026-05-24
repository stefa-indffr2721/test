import cv2
import os


def read_video(path: str, KADR: int) -> tuple[list, float]:
    """
    Читает видео файл и сохраняет каждый KADR-й кадр как временный png.
    Возвращает список путей к временным файлам и fps видео.
    """
    video = cv2.VideoCapture(path)

    fps = video.get(cv2.CAP_PROP_FPS)

    frames = []

    frame_number = 0
    while True:
        success, frame = video.read()
        if not success:
            break

        if frame_number % KADR == 0:
            temp_path = "temp" + str(frame_number) + ".png"
            cv2.imwrite(temp_path, frame)
            frames.append(temp_path)

        frame_number += 1

    video.release()

    return frames, fps


def delete_temp(frames: list) -> None:
    """Удаляет временные png файлы кадров с диска."""
    for path in frames:
        os.remove(path)