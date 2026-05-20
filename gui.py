import sys
import os.path
import time

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal

import handling
import converter
import console_writer
from file_writer import FileWriter
from ansi_writer import AnsiWriter
import video_reader

CHARSET = " .+*=#@"


class WorkerThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, task, args):
        super().__init__()
        self.task = task
        self.args = args

    def run(self):
        try:
            self.task(*self.args)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCII-Art")
        self.setFixedSize(420, 360)
        self.worker = None
        self.setup_ui()

    def setup_ui(self):

        self.label_input = QLabel("Входной файл:", self)
        self.label_input.move(20, 20)

        self.field_input = QLineEdit(self)
        self.field_input.move(20, 40)
        self.field_input.resize(290, 25)
        self.field_input.setPlaceholderText("путь к файлу...")

        self.button_browse_input = QPushButton("Обзор", self)
        self.button_browse_input.move(320, 40)
        self.button_browse_input.resize(80, 25)
        self.button_browse_input.clicked.connect(self.browse_input)

        self.label_width = QLabel("Ширина:", self)
        self.label_width.move(20, 80)

        self.field_width = QLineEdit(self)
        self.field_width.move(20, 100)
        self.field_width.resize(120, 25)
        self.field_width.setPlaceholderText("например 100")

        self.label_height = QLabel("Высота:", self)
        self.label_height.move(180, 80)

        self.field_height = QLineEdit(self)
        self.field_height.move(180, 100)
        self.field_height.resize(120, 25)
        self.field_height.setPlaceholderText("например 50")

        self.label_charset = QLabel("Файл с символами (необязательно):", self)
        self.label_charset.move(20, 140)

        self.field_charset = QLineEdit(self)
        self.field_charset.move(20, 160)
        self.field_charset.resize(290, 25)
        self.field_charset.setPlaceholderText("если пусто — используется стандартный набор")

        self.button_browse_charset = QPushButton("Обзор", self)
        self.button_browse_charset.move(320, 160)
        self.button_browse_charset.resize(80, 25)
        self.button_browse_charset.clicked.connect(self.browse_charset)

        self.label_output = QLabel("Выходной файл (необязательно):", self)
        self.label_output.move(20, 200)

        self.field_output = QLineEdit(self)
        self.field_output.move(20, 220)
        self.field_output.resize(290, 25)
        self.field_output.setPlaceholderText("если пусто — вывод в консоль")

        self.button_browse_output = QPushButton("Обзор", self)
        self.button_browse_output.move(320, 220)
        self.button_browse_output.resize(80, 25)
        self.button_browse_output.clicked.connect(self.browse_output)

        self.checkbox_ansi = QCheckBox("Цветной вывод (ANSI)", self)
        self.checkbox_ansi.move(20, 265)

        self.checkbox_video = QCheckBox("Режим видео", self)
        self.checkbox_video.move(220, 265)

        self.button_run = QPushButton("Запустить", self)
        self.button_run.move(20, 305)
        self.button_run.resize(380, 40)
        self.button_run.clicked.connect(self.run)

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "Файлы (*.png *.mp4 *.avi)")
        if path != "":
            self.field_input.setText(path)

    def browse_charset(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл с символами", "", "Текстовые файлы (*.txt)")
        if path != "":
            self.field_charset.setText(path)

    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Выберите куда сохранить", "", "Текстовые файлы (*.txt)")
        if path != "":
            self.field_output.setText(path)

    def run(self):
        input_path = self.field_input.text()
        output_path = self.field_output.text()
        charset_path = self.field_charset.text()
        ansi = self.checkbox_ansi.isChecked()
        video = self.checkbox_video.isChecked()

        if input_path == "":
            QMessageBox.warning(self, "Ошибка", "Укажите входной файл")
            return

        width = None
        height = None
        if self.field_width.text() != "":
            width = int(self.field_width.text())
        if self.field_height.text() != "":
            height = int(self.field_height.text())

        if width is None and height is None:
            QMessageBox.warning(self, "Ошибка", "Укажите ширину или высоту")
            return

        if video and output_path != "":
            QMessageBox.warning(self, "Ошибка", "Вывод видео в файл невозможен!")
            return

        if charset_path != "":
            if not os.path.exists(charset_path):
                QMessageBox.warning(self, "Ошибка", "Файл с символами не существует")
                return

        if input_path != "":
            if not os.path.exists(input_path):
                QMessageBox.warning(self, "Ошибка", "Входной файл не существует")
                return

        if charset_path != "":
            f = open(charset_path)
            charset = f.readline().replace("\n", "")
            f.close()
            if len(charset) == 0:
                QMessageBox.warning(self, "Ошибка", "Файл с символами пуст")
                return
        else:
            charset = CHARSET

        self.button_run.setEnabled(False)
        self.button_run.setText("Выполняется...")

        if video:
            self.worker = WorkerThread(self.run_video, [input_path, width, height, charset, ansi])
        else:
            self.worker = WorkerThread(self.run_image, [input_path, width, height, charset, output_path, ansi])

        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self):
        self.button_run.setEnabled(True)
        self.button_run.setText("Запустить")

    def on_error(self, message):
        self.button_run.setEnabled(True)
        self.button_run.setText("Запустить")
        QMessageBox.critical(self, "Ошибка", message)

    def run_image(self, input_path, width, height, charset, output_path, ansi):
        image = handling.prepare(input_path, width, height)
        image_ascii = converter.convert(image, charset)

        print("\033[H\033[J", end="")

        if output_path and ansi:
            raise Exception("Цветной вывод в файл невозможен!")
        elif ansi:
            writer = AnsiWriter()
            writer.write(image_ascii)
        elif output_path != "":
            writer = FileWriter(output_path)
            writer.write(image_ascii)
        else:
            writer = console_writer.ConsoleWriter()
            writer.write(image_ascii)

    def run_video(self, input_path, width, height, charset, ansi):
        KADR = 1
        frames, fps = video_reader.read_video(input_path, KADR)

        delay = 1.0 / fps * KADR

        processed_frames = []
        for frame_path in frames:
            image = handling.prepare(frame_path, width, height)
            image_ascii = converter.convert(image, charset)
            processed_frames.append(image_ascii)

        video_reader.delete_temp(frames)

        if ansi:
            writer = AnsiWriter()
        else:
            writer = console_writer.ConsoleWriter()

        print("\033[H\033[J", end="")
        for frame in processed_frames:
            print("\033[" + str(len(frame)) + "A", end="")
            writer.write(frame)
            time.sleep(delay)

        print("\033[H\033[J", end="")

    def closeEvent(self, event):
        print("\033[H\033[J", end="")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()