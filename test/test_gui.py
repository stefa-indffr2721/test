import unittest
import sys
import os
from PyQt6.QtWidgets import QApplication
from gui import MainWindow, WorkerThread

app = QApplication(sys.argv)


class TestMainWindow(unittest.TestCase):

    def setUp(self):
        self.window = MainWindow()

    def tearDown(self):
        self.window.destroy()

    def test_create(self):
        """ проверка на то, что окно создаётся без ошибок """
        self.assertIsNotNone(self.window)

    def test_title(self):
        """ проверяем заголовок окна на соответствие """
        self.assertEqual(self.window.windowTitle(), "ASCII-Art")

    def test_fields_empty(self):
        """ проверка, что по умолчанию все поля пустые """
        self.assertEqual(self.window.field_input.text(), "")
        self.assertEqual(self.window.field_output.text(), "")

    def test_checkboxes_off(self):
        """ проверка, что галочки не стоят """
        self.assertFalse(self.window.checkbox_ansi.isChecked())
        self.assertFalse(self.window.checkbox_video.isChecked())

    def test_button_enabled(self):
        """ кнопка запуска должна быть активна по умолчанию """
        self.assertTrue(self.window.button_run.isEnabled())

    def test_on_finished(self):
        """ проверка, что кнопка разблокируется после завершения процесса """
        self.window.button_run.setEnabled(False)
        self.window.on_finished()
        self.assertTrue(self.window.button_run.isEnabled())

    def test_on_finished_text(self):
        """ проверка, что текст кнопки восстанавливается после вып-я потока """
        self.window.button_run.setText("Выполняется...")
        self.window.on_finished()
        self.assertEqual(self.window.button_run.text(), "Запустить")

    def test_run_image(self):
        """ проверка, что run_image не падает при работе с реальным файлом """
        self.window.run_image("2.png", 10, 10, " @", "", False)

    def test_run_image_ansi(self):
        """ проверка, что run_image не падает в ansi режиме """
        self.window.run_image("2.png", 10, 10, " @", "", True)

    def test_run_image_to_file(self):
        """ проверка, что run_image не падает при сохранении в файл """
        temp = "temp_gui_test.txt"
        self.window.run_image("2.png", 10, 10, " @", temp, False)
        if os.path.exists(temp):
            os.remove(temp)

    def test_run_video(self):
        """ проверка, что run_video не падает при работе с реальным файлом """
        self.window.run_video("1h.mp4", 20, 10, " @", False)

    def test_run_video_ansi(self):
        """ проверка, что run_video не падает в ansi режиме """
        self.window.run_video("1h.mp4", 20, 10, " @", True)


class TestWorkerThread(unittest.TestCase):

    def test_run_success(self):
        """ проверка, что поток запускает функцию и отправляет сигнал finished """
        result = []

        def task():
            result.append(1)

        def on_finished():
            result.append(2)

        worker = WorkerThread(task, [])
        worker.finished.connect(on_finished)
        worker.run()
        self.assertEqual(result, [1, 2])

    def test_run_error(self):
        """ проверяем что поток ловит ошибку и отправляет сигнал error """
        errors = []

        def task():
            raise RuntimeError("тест ошибки")

        def on_error(message):
            errors.append(message)

        worker = WorkerThread(task, [])
        worker.error.connect(on_error)
        worker.run()
        self.assertEqual(errors, ["тест ошибки"])


if __name__ == "__main__":
    unittest.main()