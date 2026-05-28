import cv2
import os


def read_video(path: str, KADR: int) -> tuple[list, float]:
    """Читает видеофайл и сохраняет каждый KADR-й кадр как временный PNG.

    Args:
        path: путь к видеофайлу на диске.
        KADR: шаг выборки кадров. При KADR=1 сохраняется каждый кадр,
              при KADR=2 — каждый второй и т.д.

    Returns:
        кортеж (frames, fps), где:
        - frames — список путей к временным PNG-файлам вида
          "tempN.png", где N — номер кадра в исходном видео;
        - fps — частота кадров исходного видео в секунду.

    Raises:
        cv2.error: если файл не удалось открыть как видео.
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
    """Удаляет временные PNG-файлы кадров с диска.

    Args:
        frames: список путей к файлам, которые нужно удалить.
                Обычно это список, возвращённый функцией read_video().

    Raises:
        FileNotFoundError: если один из файлов не найден на диске.
        PermissionError: если нет прав на удаление файла.
    """
    for path in frames:
        os.remove(path)