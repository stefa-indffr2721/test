import sys
import os.path
import time
import re

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QPlainTextEdit,
)
from PyQt6.QtGui import QFont, QColor, QTextCursor, QTextCharFormat, QTextBlockFormat
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
import threading

import handling
import converter
from file_writer import FileWriter
import video_reader

CHARSET = " .+*=#@"
LINE_HEIGHT = 10

class TerminalWidget(QPlainTextEdit):
    _text_ready = pyqtSignal(str)
    frame_done = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("background-color: #1e1e1e; color: #d3d7cf; line-height: 1;")
        self._fmt = QTextCharFormat()
        self._text_ready.connect(self._do_send_text)

        block_fmt = QTextBlockFormat()
        block_fmt.setLineHeight(LINE_HEIGHT, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
        block_fmt.setTopMargin(0)
        block_fmt.setBottomMargin(0)
        cursor = self.textCursor()
        cursor.setBlockFormat(block_fmt)
        self.setTextCursor(cursor)
        self._block_fmt = block_fmt

    def send_text(self, text: str):
        self._text_ready.emit(text)

    @pyqtSlot(str)
    def _do_send_text(self, text: str):
        if text.startswith("\033[H\033[J"):
            text = text[len("\033[H\033[J"):]
        elif text.startswith("\033[H"):
            text = text[len("\033[H"):]

        if '\033' not in text:
            self.setPlainText(text)
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setBlockFormat(self._block_fmt)
            cursor.clearSelection()
            self.setTextCursor(cursor)
            if self.frame_done:
                self.frame_done.set()
            return

        self.clear()
        self._fmt = QTextCharFormat()

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        parts = re.split(r'(\x1b\[[0-9;]*m)', text)
        for part in parts:
            m = re.fullmatch(r'\x1b\[([0-9;]*)m', part)
            if m:
                codes = m.group(1).split(';') if m.group(1) else ['0']
                i = 0
                while i < len(codes):
                    code = codes[i]
                    if code in ('0', ''):
                        self._fmt = QTextCharFormat()
                    elif code == '38' and i + 1 < len(codes) and codes[i + 1] == '2':
                        if i + 4 < len(codes):
                            r, g, b = int(codes[i+2]), int(codes[i+3]), int(codes[i+4])
                            self._fmt.setForeground(QColor(r, g, b))
                            i += 4
                    i += 1
            else:
                cursor.insertText(part, self._fmt)

        self.setTextCursor(cursor)

        if self.frame_done:
            self.frame_done.set()


class WorkerThread(QThread):
    frame_signal = pyqtSignal(object)
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
        self.setFixedSize(420, 610)
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

        self.screen = TerminalWidget(self)
        self.screen.move(20, 360)
        self.screen.resize(380, 230)
        font = QFont("Courier New", 8, QFont.Weight.Bold)
        self.screen.setFont(font)
        self.screen.document().setDocumentMargin(0)
        self._frame_done = threading.Event()
        self.screen.frame_done = self._frame_done

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

        video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
        if input_path.lower().endswith(video_extensions) and not video:
            QMessageBox.warning(self, "Ошибка", "Входной файл — видео, но режим видео не включён!")
            return
        if not input_path.lower().endswith(video_extensions) and video:
            QMessageBox.warning(self, "Ошибка", "Входной файл — не видео, но режим видео включён!")
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

        self.screen.send_text("\033[H\033[J")

        if video:
            self.worker = WorkerThread(self.run_video, [input_path, width, height, charset, ansi, self._frame_done])
            self.worker.frame_signal.connect(self.render_frame)
        else:
            self.worker = WorkerThread(self.run_image, [input_path, width, height, charset, output_path, ansi])
            self.worker.frame_signal.connect(self.render_frame)

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

        if output_path and ansi:
            raise Exception("Цветной вывод в файл невозможен!")
        elif ansi:
            ansi_text = self.to_ansi(image_ascii)
            self.worker.frame_signal.emit(ansi_text)
        elif output_path != "":
            writer = FileWriter(output_path)
            writer.write(image_ascii)
        else:
            self.worker.frame_signal.emit(image_ascii)

    def run_video(self, input_path, width, height, charset, ansi, frame_done):
        KADR = 1
        frames, fps = video_reader.read_video(input_path, KADR)

        delay = 1.0 / fps * KADR

        processed_frames = []
        for frame_path in frames:
            image = handling.prepare(frame_path, width, height)
            image_ascii = converter.convert(image, charset)

            if ansi:
                frame = self.to_ansi(image_ascii)
            else:
                frame = image_ascii

            processed_frames.append(frame)

        video_reader.delete_temp(frames)

        for frame in processed_frames:
            frame_done.clear()
            self.worker.frame_signal.emit(frame)
            frame_done.wait(timeout=1.0)
            time.sleep(delay)

    def render_frame(self, frame):
        if isinstance(frame, str):
            self.screen.send_text("\033[H" + frame)
            return

        lines_out = []
        for row in frame:
            line = "".join((cell[0] * 2) for cell in row if isinstance(cell, tuple))
            lines_out.append(line)

        text = "\n".join(lines_out)
        self.screen.send_text("\033[H" + text)

    def to_ansi(self, image_ascii):
        out = []
        for row in image_ascii:
            line = ""
            for ch, r, g, b in row:
                line += f"\033[38;2;{r};{g};{b}m{ch}" * 2
            line += "\033[0m"
            out.append(line)
        return "\n".join(out)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()