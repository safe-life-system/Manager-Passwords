"""
auth_window_ui.py

Чистый UI для окна входа/регистрации менеджера паролей.
Файл не содержит backend-логики: не ходит в БД, не проверяет пароль,
не создаёт пользователя и не выполняет вход.

Использование:
    from auth_window_ui import Ui_AuthWindow

    class AuthWindow(Ui_AuthWindow, QMainWindow):
        def __init__(self):
            super().__init__()
            self.setupUi(self)

            self.login_button.clicked.connect(self.your_login_method)
            self.registration_button.clicked.connect(self.your_registration_method)
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize, QMetaObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class Ui_AuthWindow:
    """
    UI-класс в стиле Qt Designer.

    Важно:
    - setupUi только создаёт виджеты и стили;
    - кнопки ничего сами не делают;
    - логику входа/регистрации подключай в наследуемом классе.
    """

    def setupUi(self, MainWindow: QMainWindow) -> None:
        MainWindow.setObjectName("AuthWindow")
        MainWindow.resize(520, 660)
        MainWindow.setMinimumSize(QSize(460, 560))
        MainWindow.setWindowTitle("Manager Password")

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.root_layout = QVBoxLayout(self.centralwidget)
        self.root_layout.setObjectName("root_layout")
        self.root_layout.setContentsMargins(26, 26, 26, 26)
        self.root_layout.setSpacing(0)

        self.auth_card = QFrame(self.centralwidget)
        self.auth_card.setObjectName("auth_card")
        self.auth_card.setFrameShape(QFrame.Shape.NoFrame)
        self.auth_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.card_layout = QVBoxLayout(self.auth_card)
        self.card_layout.setObjectName("card_layout")
        self.card_layout.setContentsMargins(42, 34, 42, 30)
        self.card_layout.setSpacing(0)

        # Header
        self.app_name = QLabel(self.auth_card)
        self.app_name.setObjectName("app_name")
        self.app_name.setText("Manager Password")
        self.app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(self.auth_card)
        self.title_label.setObjectName("title_label")
        self.title_label.setText("Вход в хранилище")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel(self.auth_card)
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setText("Введите данные аккаунта или зарегистрируйте новый профиль")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)

        self.card_layout.addWidget(self.app_name)
        self.card_layout.addSpacing(8)
        self.card_layout.addWidget(self.title_label)
        self.card_layout.addSpacing(8)
        self.card_layout.addWidget(self.subtitle_label)
        self.card_layout.addSpacing(34)

        # Form
        self.form_container = QWidget(self.auth_card)
        self.form_container.setObjectName("form_container")
        self.form_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.form_layout = QVBoxLayout(self.form_container)
        self.form_layout.setObjectName("form_layout")
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(10)

        self.login_label = QLabel(self.form_container)
        self.login_label.setObjectName("field_label")
        self.login_label.setText("Логин")

        self.user_login = QLineEdit(self.form_container)
        self.user_login.setObjectName("user_login")
        self.user_login.setMinimumHeight(42)
        self.user_login.setClearButtonEnabled(True)
        self.user_login.setPlaceholderText("Введите логин")

        self.password_label = QLabel(self.form_container)
        self.password_label.setObjectName("field_label")
        self.password_label.setText("Пароль")

        self.user_password = QLineEdit(self.form_container)
        self.user_password.setObjectName("user_password")
        self.user_password.setMinimumHeight(42)
        self.user_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_password.setClearButtonEnabled(True)
        self.user_password.setPlaceholderText("Введите пароль")

        self.password_repeat_label = QLabel(self.form_container)
        self.password_repeat_label.setObjectName("field_label")
        self.password_repeat_label.setText("Повтор пароля")

        self.user_password_repeat = QLineEdit(self.form_container)
        self.user_password_repeat.setObjectName("user_password_repeat")
        self.user_password_repeat.setMinimumHeight(42)
        self.user_password_repeat.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_password_repeat.setClearButtonEnabled(True)
        self.user_password_repeat.setPlaceholderText("Повторите пароль при регистрации")

        self.options_row = QWidget(self.form_container)
        self.options_row.setObjectName("options_row")
        self.options_layout = QHBoxLayout(self.options_row)
        self.options_layout.setContentsMargins(0, 2, 0, 0)
        self.options_layout.setSpacing(10)

        self.show_passwords = QCheckBox(self.options_row)
        self.show_passwords.setObjectName("show_passwords")
        self.show_passwords.setText("Показать пароль")

        self.remember_login = QCheckBox(self.options_row)
        self.remember_login.setObjectName("remember_login")
        self.remember_login.setText("Запомнить логин")

        self.options_layout.addWidget(self.show_passwords)
        self.options_layout.addStretch(1)
        self.options_layout.addWidget(self.remember_login)

        self.status_label = QLabel(self.form_container)
        self.status_label.setObjectName("status_label")
        self.status_label.setText("")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.form_layout.addWidget(self.login_label)
        self.form_layout.addWidget(self.user_login)
        self.form_layout.addSpacing(12)
        self.form_layout.addWidget(self.password_label)
        self.form_layout.addWidget(self.user_password)
        self.form_layout.addSpacing(12)
        self.form_layout.addWidget(self.password_repeat_label)
        self.form_layout.addWidget(self.user_password_repeat)
        self.form_layout.addSpacing(10)
        self.form_layout.addWidget(self.options_row)
        self.form_layout.addSpacing(8)
        self.form_layout.addWidget(self.status_label)

        self.card_layout.addWidget(self.form_container)
        self.card_layout.addSpacing(30)

        # Buttons
        self.buttons_row = QWidget(self.auth_card)
        self.buttons_row.setObjectName("buttons_row")
        self.buttons_layout = QHBoxLayout(self.buttons_row)
        self.buttons_layout.setObjectName("buttons_layout")
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(14)

        self.login_button = QPushButton(self.buttons_row)
        self.login_button.setObjectName("login_button")
        self.login_button.setMinimumHeight(46)
        self.login_button.setText("Войти")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.registration_button = QPushButton(self.buttons_row)
        self.registration_button.setObjectName("registration_button")
        self.registration_button.setMinimumHeight(46)
        self.registration_button.setText("Регистрация")
        self.registration_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.buttons_layout.addWidget(self.login_button)
        self.buttons_layout.addWidget(self.registration_button)

        self.card_layout.addWidget(self.buttons_row)

        self.card_layout.addItem(
            QSpacerItem(
                20,
                30,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding,
            )
        )

        self.hint_label = QLabel(self.auth_card)
        self.hint_label.setObjectName("hint_label")
        self.hint_label.setText("Совет: используйте мастер-пароль, который не применяется на других сайтах.")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setWordWrap(True)
        self.card_layout.addWidget(self.hint_label)

        self.root_layout.addWidget(self.auth_card)

        # Алиасы, если тебе удобнее короткие имена в коде.
        # Можно использовать либо self.user_login, либо self.login.
        self.login = self.user_login
        self.password = self.user_password
        self.password_repeat = self.user_password_repeat
        self.btn_login = self.login_button
        self.btn_registration = self.registration_button

        self._apply_fonts()
        self._apply_styles()

        QMetaObject.connectSlotsByName(MainWindow)

    def _apply_fonts(self) -> None:
        base_font = QFont()
        base_font.setFamily("Segoe UI")
        base_font.setPointSize(10)

        title_font = QFont()
        title_font.setFamily("Segoe UI")
        title_font.setPointSize(18)
        title_font.setBold(True)

        app_font = QFont()
        app_font.setFamily("Segoe UI")
        app_font.setPointSize(10)
        app_font.setBold(True)

        field_font = QFont()
        field_font.setFamily("Segoe UI")
        field_font.setPointSize(11)

        button_font = QFont()
        button_font.setFamily("Segoe UI")
        button_font.setPointSize(11)
        button_font.setBold(True)

        self.centralwidget.setFont(base_font)
        self.app_name.setFont(app_font)
        self.title_label.setFont(title_font)

        for label in (
            self.login_label,
            self.password_label,
            self.password_repeat_label,
        ):
            label.setFont(field_font)

        self.login_button.setFont(button_font)
        self.registration_button.setFont(button_font)

    def _apply_styles(self) -> None:
        self.centralwidget.setStyleSheet(
            """
            QWidget#centralwidget {
                background: #111318;
            }

            QFrame#auth_card {
                background: #171a20;
                border: 1px solid #2a3140;
                border-radius: 14px;
            }

            QLabel#app_name {
                color: #7aa2ff;
                letter-spacing: 1px;
            }

            QLabel#title_label {
                color: #f3f6ff;
            }

            QLabel#subtitle_label {
                color: #9aa7bd;
                font-size: 13px;
            }

            QLabel#field_label {
                color: #e6ecff;
                font-size: 15px;
            }

            QLabel#status_label {
                color: #ff8f8f;
                font-size: 13px;
                min-height: 18px;
            }

            QLabel#hint_label {
                color: #7e899d;
                font-size: 12px;
            }

            QLineEdit {
                background: #20242b;
                color: #f4f7ff;
                border: 1px solid #343b49;
                border-radius: 7px;
                padding: 8px 12px;
                selection-background-color: #2b5da8;
                selection-color: #ffffff;
            }

            QLineEdit:hover {
                border: 1px solid #46556c;
                background: #232832;
            }

            QLineEdit:focus {
                border: 1px solid #3d8bfd;
                background: #1d222b;
            }

            QLineEdit::placeholder {
                color: #687489;
            }

            QCheckBox {
                color: #9aa7bd;
                spacing: 8px;
                font-size: 13px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid #3a4354;
                background: #20242b;
            }

            QCheckBox::indicator:hover {
                border: 1px solid #4f6fa8;
            }

            QCheckBox::indicator:checked {
                background: #2f6fdb;
                border: 1px solid #4f8cff;
            }

            QPushButton {
                background: #222838;
                color: #f3f6ff;
                border: 1px solid #364052;
                border-radius: 8px;
                padding: 8px 18px;
            }

            QPushButton:hover {
                background: #293247;
                border: 1px solid #4d638a;
            }

            QPushButton:pressed {
                background: #1d2433;
                border: 1px solid #2f6fdb;
            }

            QPushButton#login_button {
                background: #2454a6;
                border: 1px solid #3a78dd;
            }

            QPushButton#login_button:hover {
                background: #2d65c5;
                border: 1px solid #5c93ef;
            }

            QPushButton#login_button:pressed {
                background: #1f478d;
            }

            QPushButton#registration_button {
                background: #252b38;
                border: 1px solid #3b4658;
            }

            QPushButton#registration_button:hover {
                background: #30394b;
                border: 1px solid #5a6f91;
            }
            """
        )

    # Эти методы только меняют внешний вид/состояние виджетов.
    # Они не выполняют вход, регистрацию и не работают с базой.
    def get_login_text(self) -> str:
        return self.user_login.text().strip()

    def get_password_text(self) -> str:
        return self.user_password.text()

    def get_password_repeat_text(self) -> str:
        return self.user_password_repeat.text()

    def clear_fields(self) -> None:
        self.user_login.clear()
        self.user_password.clear()
        self.user_password_repeat.clear()
        self.status_label.clear()

    def set_status(self, text: str, error: bool = True) -> None:
        self.status_label.setText(text)
        color = "#ff8f8f" if error else "#8fe3a2"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px; min-height: 18px;")

    def set_passwords_visible(self, visible: bool) -> None:
        mode = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.user_password.setEchoMode(mode)
        self.user_password_repeat.setEchoMode(mode)

    def set_login_mode_view(self) -> None:
        """
        Визуальный режим входа: поле повтора пароля скрывается.
        Метод можно вызвать из своего класса, если хочешь переключать режимы.
        """
        self.title_label.setText("Вход в хранилище")
        self.subtitle_label.setText("Введите логин и мастер-пароль")
        self.password_repeat_label.setVisible(False)
        self.user_password_repeat.setVisible(False)
        self.login_button.setVisible(True)
        self.registration_button.setVisible(True)

    def set_registration_mode_view(self) -> None:
        """
        Визуальный режим регистрации: поле повтора пароля показывается.
        Метод можно вызвать из своего класса, если хочешь переключать режимы.
        """
        self.title_label.setText("Регистрация")
        self.subtitle_label.setText("Создайте логин и мастер-пароль для нового профиля")
        self.password_repeat_label.setVisible(True)
        self.user_password_repeat.setVisible(True)
        self.login_button.setVisible(True)
        self.registration_button.setVisible(True)


# Демо только для просмотра интерфейса.
# При импорте в твой проект этот код не запускается.
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    class DemoWindow(Ui_AuthWindow, QMainWindow):
        def __init__(self):
            super().__init__()
            self.setupUi(self)
            self.show_passwords.toggled.connect(self.set_passwords_visible)
            self.login_button.clicked.connect(lambda: self.set_status("Нажата кнопка входа. Здесь подключается твоя логика.", False))
            self.registration_button.clicked.connect(lambda: self.set_registration_mode_view())

    window = DemoWindow()
    window.show()

    sys.exit(app.exec())
