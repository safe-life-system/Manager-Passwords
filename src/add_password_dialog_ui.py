"""
add_password_dialog_ui_v2.py

Чистый UI-файл для диалогового окна добавления пароля.
Без backend-логики: не генерирует пароль сам, не сохраняет запись, не валидирует поля.

Отличие v2:
- добавлена кнопка "Показать" рядом с полем пароля;
- кнопка переключает отображение пароля: "Показать" / "Скрыть";
- метод set_password_text(...) только вставляет пароль в поле, а видимость пользователь включает кнопкой.

Использование:
    from PySide6.QtWidgets import QDialog
    from add_password_dialog_ui_v2 import Ui_DialogAddPassword

    class DialogAddPassword(Ui_DialogAddPassword, QDialog):
        def __init__(self):
            super().__init__()
            self.setupUi(self)

            self.generate_password.toggled.connect(self.set_generator_controls_visible)
            self.button_generate_password.clicked.connect(self.your_generate_method)
            self.ok_button.clicked.connect(self.your_save_method)
            self.cancel_button.clicked.connect(self.reject)
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize, QMetaObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_DialogAddPassword:
    """
    Чистый UI-слой для окна добавления/редактирования записи пароля.
    Ничего не сохраняет и не обрабатывает сам — только создаёт интерфейс.
    """

    def setupUi(self, Dialog: QDialog) -> None:
        Dialog.setObjectName("DialogAddPassword")
        Dialog.resize(660, 430)
        Dialog.setMinimumSize(QSize(600, 400))
        Dialog.setWindowTitle("Add Password")
        Dialog.setModal(True)

        self._password_visible = False

        self.root_layout = QVBoxLayout(Dialog)
        self.root_layout.setObjectName("root_layout")
        self.root_layout.setContentsMargins(20, 20, 20, 20)
        self.root_layout.setSpacing(0)

        self.dialog_card = QFrame(Dialog)
        self.dialog_card.setObjectName("dialog_card")
        self.dialog_card.setFrameShape(QFrame.Shape.NoFrame)
        self.dialog_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.card_layout = QVBoxLayout(self.dialog_card)
        self.card_layout.setObjectName("card_layout")
        self.card_layout.setContentsMargins(24, 20, 24, 20)
        self.card_layout.setSpacing(0)

        # Верхняя часть
        self.title_label = QLabel(self.dialog_card)
        self.title_label.setObjectName("title_label")
        self.title_label.setText("Добавление записи")

        self.subtitle_label = QLabel(self.dialog_card)
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setText("Заполните данные записи или сгенерируйте новый пароль")
        self.subtitle_label.setWordWrap(True)

        self.card_layout.addWidget(self.title_label)
        self.card_layout.addSpacing(4)
        self.card_layout.addWidget(self.subtitle_label)
        self.card_layout.addSpacing(18)

        # Блок генерации пароля
        self.generator_block = QWidget(self.dialog_card)
        self.generator_block.setObjectName("generator_block")
        self.generator_layout = QVBoxLayout(self.generator_block)
        self.generator_layout.setObjectName("generator_layout")
        self.generator_layout.setContentsMargins(0, 0, 0, 0)
        self.generator_layout.setSpacing(10)

        self.generate_password = QCheckBox(self.generator_block)
        self.generate_password.setObjectName("generate_password")
        self.generate_password.setText("Генерация пароля")

        self.generator_controls = QWidget(self.generator_block)
        self.generator_controls.setObjectName("generator_controls")
        self.generator_controls_layout = QHBoxLayout(self.generator_controls)
        self.generator_controls_layout.setObjectName("generator_controls_layout")
        self.generator_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.generator_controls_layout.setSpacing(10)

        self.count_password_generate = QSpinBox(self.generator_controls)
        self.count_password_generate.setObjectName("count_password_generate")
        self.count_password_generate.setMinimumHeight(34)
        self.count_password_generate.setMinimum(4)
        self.count_password_generate.setMaximum(128)
        self.count_password_generate.setValue(8)
        self.count_password_generate.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)

        self.button_generate_password = QPushButton(self.generator_controls)
        self.button_generate_password.setObjectName("button_generate_password")
        self.button_generate_password.setMinimumHeight(34)
        self.button_generate_password.setText("Сгенерировать")
        self.button_generate_password.setCursor(Qt.CursorShape.PointingHandCursor)

        self.generator_controls_layout.addWidget(self.count_password_generate, 0)
        self.generator_controls_layout.addWidget(self.button_generate_password, 1)
        self.generator_controls_layout.addStretch(3)

        self.generator_layout.addWidget(self.generate_password)
        self.generator_layout.addWidget(self.generator_controls)

        self.card_layout.addWidget(self.generator_block)
        self.card_layout.addSpacing(16)

        # Форма
        self.form_widget = QWidget(self.dialog_card)
        self.form_widget.setObjectName("form_widget")
        self.form_layout = QGridLayout(self.form_widget)
        self.form_layout.setObjectName("form_layout")
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setHorizontalSpacing(14)
        self.form_layout.setVerticalSpacing(12)

        self.label_name_data_entry = QLabel(self.form_widget)
        self.label_name_data_entry.setObjectName("field_label")
        self.label_name_data_entry.setText("Имя записи")

        self.name_data_entry = QLineEdit(self.form_widget)
        self.name_data_entry.setObjectName("name_data_entry")
        self.name_data_entry.setMinimumHeight(36)
        self.name_data_entry.setPlaceholderText("Например: GitHub, Telegram, Почта")

        self.label_site = QLabel(self.form_widget)
        self.label_site.setObjectName("field_label")
        self.label_site.setText("Сайт")

        self.site = QLineEdit(self.form_widget)
        self.site.setObjectName("site")
        self.site.setMinimumHeight(36)
        self.site.setPlaceholderText("example.com или ссылка")

        self.label_login = QLabel(self.form_widget)
        self.label_login.setObjectName("field_label")
        self.label_login.setText("Логин")

        self.login = QLineEdit(self.form_widget)
        self.login.setObjectName("login")
        self.login.setMinimumHeight(36)
        self.login.setPlaceholderText("Введите логин")

        self.label_email = QLabel(self.form_widget)
        self.label_email.setObjectName("field_label")
        self.label_email.setText("Почта")

        self.email = QLineEdit(self.form_widget)
        self.email.setObjectName("email")
        self.email.setMinimumHeight(36)
        self.email.setPlaceholderText("Введите почту")

        self.label_password = QLabel(self.form_widget)
        self.label_password.setObjectName("field_label")
        self.label_password.setText("Пароль")

        self.password_row = QWidget(self.form_widget)
        self.password_row.setObjectName("password_row")
        self.password_row_layout = QHBoxLayout(self.password_row)
        self.password_row_layout.setObjectName("password_row_layout")
        self.password_row_layout.setContentsMargins(0, 0, 0, 0)
        self.password_row_layout.setSpacing(10)

        self.password = QLineEdit(self.password_row)
        self.password.setObjectName("password")
        self.password.setMinimumHeight(36)
        self.password.setPlaceholderText("Введите пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_password_button = QPushButton(self.password_row)
        self.show_password_button.setObjectName("show_password_button")
        self.show_password_button.setMinimumHeight(36)
        self.show_password_button.setMinimumWidth(100)
        self.show_password_button.setText("Показать")
        self.show_password_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_password_button.clicked.connect(self.toggle_password_visibility)

        self.password_row_layout.addWidget(self.password, 1)
        self.password_row_layout.addWidget(self.show_password_button, 0)

        self.form_layout.addWidget(self.label_name_data_entry, 0, 0)
        self.form_layout.addWidget(self.name_data_entry, 0, 1)

        self.form_layout.addWidget(self.label_site, 1, 0)
        self.form_layout.addWidget(self.site, 1, 1)

        self.form_layout.addWidget(self.label_login, 2, 0)
        self.form_layout.addWidget(self.login, 2, 1)

        self.form_layout.addWidget(self.label_email, 3, 0)
        self.form_layout.addWidget(self.email, 3, 1)

        self.form_layout.addWidget(self.label_password, 4, 0)
        self.form_layout.addWidget(self.password_row, 4, 1)

        self.form_layout.setColumnStretch(0, 0)
        self.form_layout.setColumnStretch(1, 1)

        self.card_layout.addWidget(self.form_widget)
        self.card_layout.addSpacing(14)

        self.status_label = QLabel(self.dialog_card)
        self.status_label.setObjectName("status_label")
        self.status_label.setText("")
        self.status_label.setWordWrap(True)
        self.card_layout.addWidget(self.status_label)
        self.card_layout.addSpacing(12)

        # Кнопки
        self.buttons_row = QWidget(self.dialog_card)
        self.buttons_row.setObjectName("buttons_row")
        self.buttons_layout = QHBoxLayout(self.buttons_row)
        self.buttons_layout.setObjectName("buttons_layout")
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(10)

        self.buttons_layout.addItem(
            QSpacerItem(
                20,
                20,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum,
            )
        )

        self.ok_button = QPushButton(self.buttons_row)
        self.ok_button.setObjectName("ok_button")
        self.ok_button.setText("OK")
        self.ok_button.setMinimumHeight(38)
        self.ok_button.setMinimumWidth(96)
        self.ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_button.setDefault(True)

        self.cancel_button = QPushButton(self.buttons_row)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setText("Cancel")
        self.cancel_button.setMinimumHeight(38)
        self.cancel_button.setMinimumWidth(96)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)

        self.card_layout.addWidget(self.buttons_row)

        self.root_layout.addWidget(self.dialog_card)

        # Совместимость / удобные алиасы
        self.btn_ok = self.ok_button
        self.btn_cancel = self.cancel_button
        self.length_password_generate = self.count_password_generate
        self.button_show_password = self.show_password_button

        self._apply_fonts()
        self._apply_styles()

        # Стартовое состояние: блок генерации скрывается, пока чекбокс не включен
        self.set_generator_controls_visible(False)

        QMetaObject.connectSlotsByName(Dialog)

    def _apply_fonts(self) -> None:
        base_font = QFont()
        base_font.setFamily("Segoe UI")
        base_font.setPointSize(10)

        title_font = QFont()
        title_font.setFamily("Segoe UI")
        title_font.setPointSize(16)
        title_font.setBold(True)

        field_font = QFont()
        field_font.setFamily("Segoe UI")
        field_font.setPointSize(11)

        button_font = QFont()
        button_font.setFamily("Segoe UI")
        button_font.setPointSize(10)
        button_font.setBold(True)

        self.dialog_card.setFont(base_font)
        self.title_label.setFont(title_font)

        for label in (
            self.label_name_data_entry,
            self.label_site,
            self.label_login,
            self.label_email,
            self.label_password,
        ):
            label.setFont(field_font)

        self.ok_button.setFont(button_font)
        self.cancel_button.setFont(button_font)
        self.button_generate_password.setFont(button_font)
        self.show_password_button.setFont(button_font)

    def _apply_styles(self) -> None:
        self.dialog_card.setStyleSheet(
            """
            QFrame#dialog_card {
                background: #171a20;
                border: 1px solid #2a3140;
                border-radius: 14px;
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
                font-size: 14px;
            }

            QLabel#status_label {
                color: #ff8f8f;
                font-size: 13px;
                min-height: 18px;
            }

            QLineEdit, QSpinBox {
                background: #20242b;
                color: #f4f7ff;
                border: 1px solid #343b49;
                border-radius: 7px;
                padding: 6px 10px;
                selection-background-color: #2b5da8;
                selection-color: #ffffff;
            }

            QLineEdit:hover, QSpinBox:hover {
                border: 1px solid #46556c;
                background: #232832;
            }

            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #3d8bfd;
                background: #1d222b;
            }

            QLineEdit::placeholder {
                color: #687489;
            }

            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                border: none;
                background: transparent;
            }

            QCheckBox {
                color: #e6ecff;
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
                background: #252b38;
                color: #f3f6ff;
                border: 1px solid #3b4658;
                border-radius: 8px;
                padding: 8px 18px;
            }

            QPushButton:hover {
                background: #30394b;
                border: 1px solid #5a6f91;
            }

            QPushButton:pressed {
                background: #232a38;
                border: 1px solid #2f6fdb;
            }

            QPushButton#ok_button {
                background: #2454a6;
                border: 1px solid #3a78dd;
            }

            QPushButton#ok_button:hover {
                background: #2d65c5;
                border: 1px solid #5c93ef;
            }

            QPushButton#ok_button:pressed {
                background: #1f478d;
            }

            QPushButton#button_generate_password,
            QPushButton#show_password_button {
                background: #222838;
                border: 1px solid #364052;
            }

            QPushButton#button_generate_password:hover,
            QPushButton#show_password_button:hover {
                background: #293247;
                border: 1px solid #4d638a;
            }
            """
        )

    # ---------------------------
    # Готовые UI-методы
    # ---------------------------

    def set_generator_controls_visible(self, visible: bool) -> None:
        """
        Показывает или скрывает строку со SpinBox и кнопкой генерации.
        Удобно подключать к чекбоксу:
            self.generate_password.toggled.connect(self.set_generator_controls_visible)
        """
        self.generator_controls.setVisible(visible)

    def set_password_visible(self, visible: bool) -> None:
        """
        Показывает/скрывает текст в поле пароля.
        Также меняет текст кнопки "Показать" / "Скрыть".
        """
        self._password_visible = visible
        mode = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.password.setEchoMode(mode)
        self.show_password_button.setText("Скрыть" if visible else "Показать")

    def toggle_password_visibility(self) -> None:
        """
        Переключает видимость пароля.
        Этот метод уже подключён к кнопке show_password_button внутри UI.
        """
        self.set_password_visible(not self._password_visible)

    def clear_fields(self) -> None:
        """
        Очищает все поля формы и статусную строку.
        Пароль снова скрывается.
        """
        self.name_data_entry.clear()
        self.site.clear()
        self.login.clear()
        self.email.clear()
        self.password.clear()
        self.status_label.clear()
        self.set_password_visible(False)

    def get_form_data(self) -> dict:
        """
        Возвращает данные из формы в виде словаря.
        Ничего не сохраняет — просто снимает значения из полей.
        """
        return {
            "name_data_entry": self.name_data_entry.text().strip(),
            "site": self.site.text().strip(),
            "login": self.login.text().strip(),
            "email": self.email.text().strip(),
            "password": self.password.text(),
            "generate_password": self.generate_password.isChecked(),
            "count_password_generate": self.count_password_generate.value(),
        }

    def set_password_text(self, password_text: str, show_after_set: bool = False) -> None:
        """
        Устанавливает текст в поле пароля.

        show_after_set=False:
            пароль вставится, но останется скрытым.

        show_after_set=True:
            пароль вставится и сразу станет видимым.
            Это удобно после генерации, чтобы пользователь сразу увидел результат.
        """
        self.password.setText(password_text)
        if show_after_set:
            self.set_password_visible(True)

    def set_status(self, text: str, error: bool = True) -> None:
        """
        Показывает сообщение под формой.
        error=True  -> красный текст
        error=False -> зелёный текст
        """
        self.status_label.setText(text)
        color = "#ff8f8f" if error else "#8fe3a2"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px; min-height: 18px;")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    class DemoDialog(Ui_DialogAddPassword, QDialog):
        def __init__(self):
            super().__init__()
            self.setupUi(self)
            self.generate_password.toggled.connect(self.set_generator_controls_visible)
            self.button_generate_password.clicked.connect(self._demo_generate)
            self.ok_button.clicked.connect(self._demo_ok)
            self.cancel_button.clicked.connect(self.reject)

        def _demo_generate(self):
            count = self.count_password_generate.value()
            self.set_password_text("A" * count, show_after_set=True)
            self.set_status("Демо: пароль подставлен в поле и показан.", error=False)

        def _demo_ok(self):
            data = self.get_form_data()
            self.set_status(f"Демо: данные собраны. Имя записи: {data['name_data_entry'] or '—'}", error=False)

    dialog = DemoDialog()
    dialog.show()

    sys.exit(app.exec())
