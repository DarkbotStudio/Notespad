import os.path
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QStatusBar, QMessageBox, QFileDialog, QDialog, \
    QLabel, QVBoxLayout, QComboBox, QPushButton
from PySide6.QtGui import QIcon, QAction, Qt
import json

with open("languages.json", 'r', encoding='utf-8') as file4:
    languages = json.load(file4)

language = None


if not os.path.exists("language.txt"):
    language = 'English'
    with open('language.txt', 'w', encoding='utf-8') as file:
        file.write(language.strip())
with open('language.txt', 'r', encoding="utf-8") as file2:
    language = file2.read().strip()
    if language not in languages.keys():
        language = 'English'
        with open('language.txt', 'w', encoding='utf-8') as file3:
            file3.write(language.strip())

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(languages[language]['settings']['title'])
        self.setWindowIcon(QIcon("icons/settings.png"))

        layout = QVBoxLayout()
        self.setMinimumSize(200, 100)  # Установка минимального размера окна настроек

        language_label = QLabel(languages[language]['settings']['language'])
        layout.addWidget(language_label)

        language_combo = QComboBox()
        for key in languages.keys():
            language_combo.addItem(key)
        language_combo.setCurrentText(language)

        layout.addWidget(language_combo)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.save_settings(language_combo.currentText()))
        layout.addWidget(ok_button)

        self.setLayout(layout)


    def save_settings(self, selected_language):
        # Сохранить выбранный язык в файл "language.txt"
        try:
            with open("language.txt", "w", encoding="utf-8") as file:
                file.write(selected_language)
        except IOError:
            pass

        if language == selected_language:
            self.accept()
        else:
            QMessageBox.information(self, languages[selected_language]['settings']['restart_required'], languages[selected_language]['settings']['restart_message'])
            self.accept()
            app.closeAllWindows()
            python = sys.executable
            subprocess.call([python] + sys.argv)


class Notespad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notespad")
        self.resize(600, 500)
        self.setWindowIcon(QIcon("icons/icon.png"))  # Установка иконки окна
        self.current_file = None

        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.create_actions()
        self.create_menu()

    def create_actions(self):
        self.new_action = QAction(QIcon("icons/new.ico"), languages[language]['menu']['new'], self)
        self.new_action.setStatusTip(languages[language]['menu']['status_file'])
        self.new_action.triggered.connect(self.new_note)

        self.open_action = QAction(QIcon("icons/open.png"), languages[language]['menu']['open'], self)
        self.open_action.setStatusTip(languages[language]['menu']['status_open'])
        self.open_action.triggered.connect(self.open_note)

        self.save_action = QAction(QIcon("icons/save.jpg"), languages[language]['menu']['save'], self)
        self.save_action.setStatusTip(languages[language]['menu']['status_save'])
        self.save_action.triggered.connect(self.save_note)

        self.save_as_action = QAction(QIcon("icons/save_as.png"), languages[language]['menu']['save_as'], self)
        self.save_as_action.setStatusTip(languages[language]['menu']['status_save_as'])
        self.save_as_action.triggered.connect(self.save_note_as)

        self.about_action = QAction(QIcon("icons/about.ico"), languages[language]['menu']['about'], self)
        self.about_action.setStatusTip(languages[language]['menu']['about'])
        self.about_action.triggered.connect(self.show_about_dialog)

        self.settings_action = QAction(QIcon("icons/settings.png"), languages[language]['menu']['settings'], self)
        self.settings_action.setStatusTip(languages[language]['menu']['status_settings'])
        self.settings_action.triggered.connect(self.open_settings)

        self.exit_action = QAction(QIcon("icons/exit.png"), languages[language]['menu']['exit'], self)
        self.exit_action.setStatusTip(languages[language]['menu']['status_exit'])
        self.exit_action.triggered.connect(self.exit_action1)

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu(languages[language]['menu']['file'])
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addAction(self.exit_action)

        settings_menu = menubar.addMenu(languages[language]['menu']['settings'])
        settings_menu.addAction(self.settings_action)

        about_menu = menubar.addMenu(languages[language]['menu']['about'])
        about_menu.addAction(self.about_action)

    def new_note(self):
        self.text_edit.clear()
        self.current_file = None
        self.setWindowTitle("Notespad")

    def open_note(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, languages[language]['menu']['explorer_open_file'], "", languages[language]['menu']['explorer_extentions'], options=options)

        if file_name:
            with open(file_name, "r") as file:
                self.text_edit.setPlainText(file.read())

            self.current_file = file_name
            self.setWindowTitle(f"Notespad - {file_name}")

    def save_note(self):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_edit.toPlainText())
        else:
            self.save_note_as()

    def save_note_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, languages[language]['menu']['explorer_save_file'], "", languages[language]['menu']['explorer_extentions'], options=options)

        if file_name:
            with open(file_name, "w") as file:
                file.write(self.text_edit.toPlainText())

            self.current_file = file_name
            self.setWindowTitle(f"Notespad - {file_name}")

    def show_about_dialog(self):
        message_box = QMessageBox()
        message_box.setWindowTitle(languages[language]['about']['title'])

        text = languages[language]['about']['text']

        message_box.setTextFormat(Qt.TextFormat.RichText)
        message_box.setText(text)

        message_box.exec()

    def open_settings(self):
        settings_dialog = SettingsDialog(self).exec()

    def exit_action1(self):
        sys.exit(0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/icon.png"))  # Установка иконки для приложения
    notespad = Notespad()
    notespad.show()
    sys.exit(app.exec())
