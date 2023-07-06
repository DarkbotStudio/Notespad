import os.path
import subprocess
import sys
import requests
import base64
import webbrowser
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QStatusBar, QMessageBox, QFileDialog, QDialog, \
    QLabel, QVBoxLayout, QComboBox, QPushButton, QTabWidget
from PySide6.QtGui import QIcon, QAction, Qt
import json

languages = None
language = None
version = "1.0.2"
config_file_path = "config.json"
config = {
    "language": "English",
    "notify_new_version": True
}

with open("languages.json", 'r', encoding='utf-8') as file4:
    languages = json.load(file4)

if not os.path.exists(config_file_path):
    with open(config_file_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

with open(config_file_path, 'r', encoding='utf-8') as file:
    config = json.load(file)
    language = config["language"]

if config["language"] not in languages.keys():
    config["language"] = 'English'
    with open(config_file_path, 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)


def check_version(current_version):
    # URL для получения содержимого файла с версиями
    url = "https://api.github.com/repos/DarkbotStudio/Notespad-versions/contents/versions.json"

    # Выполняем GET-запрос к GitHub API
    response = requests.get(url)

    # Проверяем статус ответа
    if response.status_code == 200:
        # Получаем данные из ответа
        data = response.json()

        # Декодируем содержимое файла из Base64
        content = data["content"]
        file_content = base64.b64decode(content).decode("utf-8")

        # Загружаем JSON из содержимого файла
        versions_data = json.loads(file_content)

        # Получаем последнюю версию
        versions = versions_data["versions"]
        latest_version = versions[-1]

        # Используем последнюю версию по своему усмотрению
        if str(latest_version) == str(current_version):
            pass
        elif not str(latest_version) == str(current_version) and not config['notify_new_version'] == False:
            # Создание всплывающего окна
            message_box = QMessageBox()
            message_box.setWindowTitle(languages[language]["update"]["available"])
            message_box.setText(languages[language]["update"]["new_version"])
            message_box.setIcon(QMessageBox.Information)

            # Добавление кнопок
            download_button = message_box.addButton(languages[language]["update"]["download"], QMessageBox.AcceptRole)
            never_remind_button = message_box.addButton(languages[language]["update"]["no_reminder"], QMessageBox.RejectRole)
            remind_next_time_button = message_box.addButton(languages[language]["update"]["remind_next_time"], QMessageBox.ActionRole)

            # Установка кнопки по умолчанию
            message_box.setDefaultButton(remind_next_time_button)

            # Отображение всплывающего окна и ожидание нажатия кнопки
            message_box.exec()

            # Обработка нажатия кнопок
            if message_box.clickedButton() == download_button:
                webbrowser.open("https://github.com/DarkbotStudio/Notespad", True)
            elif message_box.clickedButton() == never_remind_button:
                 config['notify_new_version'] = False
                 with open("config.json", "w", encoding="utf-8") as file:
                     json.dump(config, file, ensure_ascii=False, indent=4)
            elif message_box.clickedButton() == remind_next_time_button:
                pass

    else:
        pass

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

        ok_button = QPushButton(languages[language]["menu"]["save"])
        ok_button.clicked.connect(lambda: self.save_settings(language_combo.currentText()))
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def save_settings(self, selected_language):
        # Сохранить выбранный язык в файл "config.json"
        try:
            config["language"] = selected_language
            with open("config.json", "w", encoding="utf-8") as file:
                json.dump(config, file, ensure_ascii=False, indent=4)
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

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.create_actions()
        self.create_menu()

    def create_actions(self):
        self.new_tab_action = QAction(QIcon("icons/new_tab.png"), languages[language]['menu']['new_tab'], self)
        self.new_tab_action.setStatusTip(languages[language]['menu']['status_new_tab'])
        self.new_tab_action.triggered.connect(self.create_tab)
        self.new_tab_action.setShortcut("Ctrl+T")

        self.close_tab_action = QAction(QIcon("icons/close_tab.png"), languages[language]['menu']['close_tab'], self)
        self.close_tab_action.setStatusTip(languages[language]['menu']['status_close_tab'])
        self.close_tab_action.triggered.connect(self.close_tab)
        self.close_tab_action.setShortcut("Ctrl+W")

        self.new_action = QAction(QIcon("icons/new.ico"), languages[language]['menu']['new'], self)
        self.new_action.setStatusTip(languages[language]['menu']['status_file'])
        self.new_action.triggered.connect(self.new_note)
        self.new_action.setShortcut("Ctrl+N")

        self.open_action = QAction(QIcon("icons/open.png"), languages[language]['menu']['open'], self)
        self.open_action.setStatusTip(languages[language]['menu']['status_open'])
        self.open_action.triggered.connect(self.open_note)
        self.open_action.setShortcut("Ctrl+O")

        self.save_action = QAction(QIcon("icons/save.jpg"), languages[language]['menu']['save'], self)
        self.save_action.setStatusTip(languages[language]['menu']['status_save'])
        self.save_action.triggered.connect(self.save_note)
        self.save_action.setShortcut("Ctrl+S")

        self.save_as_action = QAction(QIcon("icons/save_as.png"), languages[language]['menu']['save_as'], self)
        self.save_as_action.setStatusTip(languages[language]['menu']['status_save_as'])
        self.save_as_action.triggered.connect(self.save_note_as)
        self.save_as_action.setShortcut("Ctrl+Shift+S")

        self.about_action = QAction(QIcon("icons/about.ico"), languages[language]['menu']['about'], self)
        self.about_action.setStatusTip(languages[language]['menu']['about'])
        self.about_action.triggered.connect(self.show_about_dialog)
        self.about_action.setShortcut("Ctrl+I")

        self.settings_action = QAction(QIcon("icons/settings.png"), languages[language]['menu']['settings'], self)
        self.settings_action.setStatusTip(languages[language]['menu']['status_settings'])
        self.settings_action.triggered.connect(self.open_settings)
        self.settings_action.setShortcut("Ctrl+P")

        self.exit_action = QAction(QIcon("icons/exit.png"), languages[language]['menu']['exit'], self)
        self.exit_action.setStatusTip(languages[language]['menu']['status_exit'])
        self.exit_action.triggered.connect(self.exit_action1)
        self.exit_action.setShortcut("Ctrl+Q")

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

        tab_menu = menubar.addMenu(languages[language]['menu']['tabs'])
        tab_menu.addAction(self.new_tab_action)
        tab_menu.addAction(self.close_tab_action)

        about_menu = menubar.addMenu(languages[language]['menu']['about'])
        about_menu.addAction(self.about_action)

    def new_note(self):
        self.create_tab()

    def create_tab(self):
        text_edit = QTextEdit()
        self.tab_widget.addTab(text_edit, "Untitled")

    def open_note(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, languages[language]['menu']['explorer_open_file'], "",
                                                   languages[language]['menu']['explorer_extentions'], options=options)

        if file_name:
            with open(file_name, "r") as file:
                text = file.read()

            self.create_tab()
            text_edit = self.tab_widget.currentWidget()
            text_edit.setPlainText(text)

            self.current_file = file_name
            self.setWindowTitle(f"Notespad - {file_name}")

    def save_note(self):
        if self.current_file:
            text_edit = self.tab_widget.currentWidget()
            text = text_edit.toPlainText()

            with open(self.current_file, "w") as file:
                file.write(text)
        else:
            self.save_note_as()

    def save_note_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, languages[language]['menu']['explorer_save_file'], "",
                                                   languages[language]['menu']['explorer_extentions'], options=options)

        if file_name:
            text_edit = self.tab_widget.currentWidget()
            text = text_edit.toPlainText()

            with open(file_name, "w") as file:
                file.write(text)

            self.current_file = file_name
            self.setWindowTitle(f"Notespad - {file_name}")

    def show_about_dialog(self):
        message_box = QMessageBox()
        message_box.setWindowTitle(languages[language]['about']['title'])

        text = languages[language]['about']['text']

        message_box.setTextFormat(Qt.TextFormat.RichText)
        message_box.setText(text)

        message_box.exec()

    def create_tab(self):
        text_edit = QTextEdit()
        self.tab_widget.addTab(text_edit, "Untitled")

    def close_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.removeTab(current_index)

    def open_settings(self):
        settings_dialog = SettingsDialog(self).exec()

    def exit_action1(self):
        sys.exit(0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icons/icon.png"))  # Установка иконки для приложения
    notespad = Notespad()
    notespad.show()
    check_version(version)
    sys.exit(app.exec())