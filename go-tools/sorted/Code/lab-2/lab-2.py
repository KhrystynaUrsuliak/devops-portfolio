import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QDialog, QLineEdit, QRadioButton, QMessageBox, QButtonGroup, QFileDialog
)
from PyQt5.QtGui import QTextCursor
import regex as re

class DeleteDialog(QDialog):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setWindowTitle("Знищити")
        self.setFixedSize(500, 220)

        self.label = QLabel("Текст пошуку (маска):")
        self.search_input = QLineEdit()

        self.from_start = QRadioButton("З початку")
        self.from_cursor = QRadioButton("Від курсора")
        self.from_start.setChecked(True)

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.from_start)
        self.radio_group.addButton(self.from_cursor)

        self.find_button = QPushButton("Знайти")
        self.delete_button = QPushButton("Знищити")
        self.skip_button = QPushButton("Пропустити")
        self.delete_all_button = QPushButton("Знищити все")
        self.close_button = QPushButton("Закрити вікно")

        self.find_button.clicked.connect(self.find_match)
        self.delete_button.clicked.connect(self.delete_current_match)
        self.skip_button.clicked.connect(self.skip_match)
        self.delete_all_button.clicked.connect(self.delete_all_matches)
        self.close_button.clicked.connect(self.close)

        self.delete_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.delete_all_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.from_start)
        layout.addWidget(self.from_cursor)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.find_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.skip_button)
        button_layout.addWidget(self.delete_all_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.current_pattern = None
        self.matches = []
        self.current_match_index = -1

    def mask_to_regex(self, mask):
        regex = ""
        i = 0
        while i < len(mask):
            if mask[i] == "[":
                i += 1
                num_str = ""
                while i < len(mask) and mask[i].isdigit():
                    num_str += mask[i]
                    i += 1
                if i < len(mask) and mask[i] == "]" and num_str:
                    regex += r"[+\-*/]{" + num_str + "}"
                    i += 1
                else:
                    regex += re.escape("[") + num_str
            else:
                regex += re.escape(mask[i])
                i += 1

        signs = r"\s\.,;:!?\(\)\"\'"

        return r"(?<=^|[" + signs + r"])" + regex + r"(?=$|[" + signs + r"])"

    def find_match(self):
        mask = self.search_input.text()
        if not mask:
            QMessageBox.warning(self, "Помилка", "Введіть маску для пошуку!")
            return

        self.current_pattern = self.mask_to_regex(mask)
        text = self.text_edit.toPlainText()

        start_pos = 0 if self.from_start.isChecked() else self.text_edit.textCursor().position()

        self.matches = [m for m in re.finditer(self.current_pattern, text[start_pos:])]
        self.current_match_index = 0

        if self.matches:
            self.highlight_current_match(start_pos)
            self.delete_button.setEnabled(True)
            self.skip_button.setEnabled(True)
            self.delete_all_button.setEnabled(True)
        else:
            QMessageBox.information(self, "Результат", "Нічого не знайдено.")
            self.delete_button.setEnabled(False)
            self.skip_button.setEnabled(False)
            self.delete_all_button.setEnabled(False)

    def highlight_current_match(self, offset):
        match = self.matches[self.current_match_index]
        cursor = self.text_edit.textCursor()
        cursor.setPosition(offset + match.start())
        cursor.setPosition(offset + match.end(), QTextCursor.KeepAnchor)
        self.text_edit.setTextCursor(cursor)

    def delete_current_match(self):
        cursor = self.text_edit.textCursor()
        cursor.removeSelectedText()
        self.find_match()

    def skip_match(self):
        self.current_match_index += 1
        if self.current_match_index < len(self.matches):
            offset = 0 if self.from_start.isChecked() else self.text_edit.textCursor().position()
            self.highlight_current_match(offset)
        else:
            QMessageBox.information(self, "Результат", "Більше нічого не знайдено.")
            self.delete_button.setEnabled(False)
            self.skip_button.setEnabled(False)

    def delete_all_matches(self):
        text = self.text_edit.toPlainText()
        new_text, count = re.subn(self.current_pattern, '', text)
        self.text_edit.setPlainText(new_text)
        QMessageBox.information(self, "Результат", f"Видалено {count} входжень.")
        self.delete_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.delete_all_button.setEnabled(False)

class Editor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Текстовий редактор")
        self.setGeometry(100, 100, 600, 400)

        self.text_edit = QTextEdit()
        self.load_button = QPushButton("Завантажити з файлу")
        self.delete_button = QPushButton("Відкрити Delete")

        self.load_button.clicked.connect(self.load_from_file)
        self.delete_button.clicked.connect(self.open_delete_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.load_button)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

    def load_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Виберіть файл", "", "Text Files (*.txt)")
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as file:
                self.text_edit.setPlainText(file.read())

    def open_delete_dialog(self):
        dialog = DeleteDialog(self.text_edit)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = Editor()
    editor.show()
    sys.exit(app.exec_())
