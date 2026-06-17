"""
csv_dialogs_ui.py

Чистые UI-классы для диалоговых окон импорта и экспорта CSV.
Файл не содержит backend-логики:
- не импортирует CSV сам;
- не экспортирует CSV сам;
- не открывает QFileDialog сам;
- не читает и не пишет файлы.

Он только создаёт интерфейс в стиле остальных окон проекта.

Классы:
    Ui_DialogImportPasswords
    Ui_DialogExportPasswords
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize, QMetaObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class _BaseCsvDialogUi:
    """
    Базовый UI для CSV-диалогов.
    Напрямую этот класс обычно не наследуй.
    Используй Ui_DialogImportPasswords или Ui_DialogExportPasswords.
    """

    def _setup_csv_ui(self, Dialog: QDialog, mode: str) -> None:
        if mode not in {"import", "export"}:
            raise ValueError("mode должен быть 'import' или 'export'")

        self.csv_mode = mode

        Dialog.setObjectName("DialogCsvFile")
        Dialog.resize(620, 300)
        Dialog.setMinimumSize(QSize(560, 260))
        Dialog.setModal(True)

        if mode == "import":
            Dialog.setWindowTitle("Import CSV")
            title = "Импорт CSV"
            subtitle = "Выберите CSV-файл, из которого нужно загрузить записи"
            field_placeholder = "Путь к CSV-файлу для импорта"
            ok_text = "Импорт"
        else:
            Dialog.setWindowTitle("Export CSV")
            title = "Экспорт CSV"
            subtitle = "Выберите имя и место сохранения CSV-файла"
            field_placeholder = "Путь для сохранения CSV-файла"
            ok_text = "Экспорт"

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
        self.card_layout.setContentsMargins(24, 22, 24, 20)
        self.card_layout.setSpacing(0)

        self.title_label = QLabel(self.dialog_card)
        self.title_label.setObjectName("title_label")
        self.title_label.setText(title)

        self.subtitle_label = QLabel(self.dialog_card)
        self.subtitle_label.setObjectName("subtitle_label")
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setWordWrap(True)

        self.card_layout.addWidget(self.title_label)
        self.card_layout.addSpacing(4)
        self.card_layout.addWidget(self.subtitle_label)
        self.card_layout.addSpacing(26)

        self.file_row = QWidget(self.dialog_card)
        self.file_row.setObjectName("file_row")
        self.file_row_layout = QHBoxLayout(self.file_row)
        self.file_row_layout.setObjectName("file_row_layout")
        self.file_row_layout.setContentsMargins(0, 0, 0, 0)
        self.file_row_layout.setSpacing(12)

        self.label_file_name_csv = QLabel(self.file_row)
        self.label_file_name_csv.setObjectName("field_label")
        self.label_file_name_csv.setText("Имя файла CSV")
        self.label_file_name_csv.setMinimumWidth(120)

        self.file_name_csv = QLineEdit(self.file_row)
        self.file_name_csv.setObjectName("file_name_csv")
        self.file_name_csv.setMinimumHeight(38)
        self.file_name_csv.setPlaceholderText(field_placeholder)
        self.file_name_csv.setClearButtonEnabled(True)

        self.browse_button = QPushButton(self.file_row)
        self.browse_button.setObjectName("browse_button")
        self.browse_button.setText("...")
        self.browse_button.setMinimumHeight(38)
        self.browse_button.setMinimumWidth(48)
        self.browse_button.setMaximumWidth(56)
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.file_row_layout.addWidget(self.label_file_name_csv)
        self.file_row_layout.addWidget(self.file_name_csv, 1)
        self.file_row_layout.addWidget(self.browse_button)

        self.card_layout.addWidget(self.file_row)
        self.card_layout.addSpacing(14)

        self.status_label = QLabel(self.dialog_card)
        self.status_label.setObjectName("status_label")
        self.status_label.setText("")
        self.status_label.setWordWrap(True)
        self.card_layout.addWidget(self.status_label)

        self.card_layout.addItem(
            QSpacerItem(
                20,
                28,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding,
            )
        )

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
        self.ok_button.setText(ok_text)
        self.ok_button.setMinimumHeight(38)
        self.ok_button.setMinimumWidth(104)
        self.ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_button.setDefault(True)

        self.cancel_button = QPushButton(self.buttons_row)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setText("Cancel")
        self.cancel_button.setMinimumHeight(38)
        self.cancel_button.setMinimumWidth(104)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)

        self.card_layout.addWidget(self.buttons_row)
        self.root_layout.addWidget(self.dialog_card)

        # Алиасы для удобства и совместимости со старым кодом
        self.csv_file_name = self.file_name_csv
        self.name_file_csv = self.file_name_csv
        self.file_path = self.file_name_csv

        self.button_select_file = self.browse_button
        self.select_file_button = self.browse_button

        self.btn_ok = self.ok_button
        self.btn_cancel = self.cancel_button

        self._apply_fonts()
        self._apply_styles()

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
        self.label_file_name_csv.setFont(field_font)
        self.ok_button.setFont(button_font)
        self.cancel_button.setFont(button_font)
        self.browse_button.setFont(button_font)

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

            QLineEdit {
                background: #20242b;
                color: #f4f7ff;
                border: 1px solid #343b49;
                border-radius: 7px;
                padding: 6px 10px;
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

            QPushButton#browse_button {
                background: #222838;
                border: 1px solid #364052;
                padding-left: 0px;
                padding-right: 0px;
            }

            QPushButton#browse_button:hover {
                background: #293247;
                border: 1px solid #4d638a;
            }
            """
        )

    def get_file_path(self) -> str:
        """
        Возвращает путь из поля file_name_csv.
        Пробелы в начале и конце удаляются.
        """
        return self.file_name_csv.text().strip()

    def set_file_path(self, path: str) -> None:
        """
        Устанавливает путь в поле file_name_csv.
        Удобно вызывать после выбора файла через QFileDialog в твоём коде.
        """
        self.file_name_csv.setText(path)

    def clear_fields(self) -> None:
        """
        Очищает поле пути и статусную строку.
        """
        self.file_name_csv.clear()
        self.status_label.clear()

    def set_status(self, text: str, error: bool = True) -> None:
        """
        Показывает сообщение под полем.
        error=True  -> красный текст
        error=False -> зелёный текст
        """
        self.status_label.setText(text)
        color = "#ff8f8f" if error else "#8fe3a2"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 13px; min-height: 18px;")

    def set_import_mode_view(self) -> None:
        """
        Переключает тексты окна в режим импорта.
        Логику импорта не выполняет.
        """
        self.csv_mode = "import"
        self.title_label.setText("Импорт CSV")
        self.subtitle_label.setText("Выберите CSV-файл, из которого нужно загрузить записи")
        self.file_name_csv.setPlaceholderText("Путь к CSV-файлу для импорта")
        self.ok_button.setText("Импорт")

    def set_export_mode_view(self) -> None:
        """
        Переключает тексты окна в режим экспорта.
        Логику экспорта не выполняет.
        """
        self.csv_mode = "export"
        self.title_label.setText("Экспорт CSV")
        self.subtitle_label.setText("Выберите имя и место сохранения CSV-файла")
        self.file_name_csv.setPlaceholderText("Путь для сохранения CSV-файла")
        self.ok_button.setText("Экспорт")


class Ui_DialogImportPasswords(_BaseCsvDialogUi):
    """
    UI для окна импорта CSV.
    """

    def setupUi(self, Dialog: QDialog) -> None:
        self._setup_csv_ui(Dialog, mode="import")


class Ui_DialogExportPasswords(_BaseCsvDialogUi):
    """
    UI для окна экспорта CSV.
    """

    def setupUi(self, Dialog: QDialog) -> None:
        self._setup_csv_ui(Dialog, mode="export")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    class DemoImportDialog(Ui_DialogImportPasswords, QDialog):
        def __init__(self):
            super().__init__()
            self.setupUi(self)
            self.browse_button.clicked.connect(lambda: self.set_file_path("C:/example/import.csv"))
            self.ok_button.clicked.connect(lambda: self.set_status("Демо: импорт CSV запускается в твоём коде.", error=False))
            self.cancel_button.clicked.connect(self.reject)

    dialog = DemoImportDialog()
    dialog.show()
    sys.exit(app.exec())
