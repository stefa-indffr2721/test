import unittest
import os
import video_reader


class TestVideoReader(unittest.TestCase):

    def test_read_video(self):
        """ тест на то, что read_video читает видео и возвращает кадры и fps """
        frames, fps = video_reader.read_video("1h.mp4", 1)
        video_reader.delete_temp(frames)
        self.assertGreater(len(frames), 0)
        self.assertGreater(fps, 0)

    def test_delete_temp(self):
        """ тест на то, что delete_temp удаляет файлы """
        path = "temp_video_test.txt"
        open(path, "w").close()

        video_reader.delete_temp([path])

        self.assertFalse(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()