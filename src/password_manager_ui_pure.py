# -*- coding: utf-8 -*-
"""
Чистый UI для менеджера паролей на PySide6.

Файл намеренно не содержит бизнес-логики:
- не читает базу данных;
- не импортирует/экспортирует CSV;
- не удаляет записи;
- не открывает окна добавления/редактирования;
- не копирует значения в буфер сам.

UI только создаёт виджеты, стили, таблицу, визуальные кнопки действий
и отправляет сигналы, которые нужно подключить в наследуемом классе.

Основной сценарий подключения:
    class MainWindow(Ui_MainWindow, QMainWindow):
        def __init__(self, user_name_data):
            super().__init__()
            self.setupUi(self)
            ...
            self.set_passwords_model(self.proxy)

Важно:
    Не вызывай self.table_passwords.setModel(self.proxy) напрямую,
    если нужна колонка "Действия". Используй self.set_passwords_model(self.proxy).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import (
    QAbstractProxyModel,
    QEasingCurve,
    QModelIndex,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QAction, QBrush, QColor, QCursor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionViewItem,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class ActionColumnProxyModel(QAbstractProxyModel):
    """
    Обёртка над твоей моделью/прокси-моделью.

    Она добавляет ОДНУ виртуальную колонку "Действия" справа.
    Исходную модель не меняет.

    Если твоя модель отдаёт:
        0 ID
        1 Имя записи
        2 Сайт
        3 Логин
        4 Почта
        5 Пароль

    То в UI будет:
        0 ID, 1 Имя записи, 2 Сайт, 3 Логин, 4 Почта, 5 Пароль, 6 Действия
    """

    def __init__(self, parent: Optional[QObject] = None, action_header: str = "Действия"):
        super().__init__(parent)
        self.action_header = action_header

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() or self.sourceModel() is None:
            return 0
        return self.sourceModel().rowCount()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() or self.sourceModel() is None:
            return 0
        return self.sourceModel().columnCount() + 1

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if row < 0 or column < 0:
            return QModelIndex()
        if row >= self.rowCount() or column >= self.columnCount():
            return QModelIndex()
        return self.createIndex(row, column)

    def parent(self, child: QModelIndex = QModelIndex()) -> QModelIndex:
        return QModelIndex()

    def mapToSource(self, proxy_index: QModelIndex) -> QModelIndex:
        if not proxy_index.isValid() or self.sourceModel() is None:
            return QModelIndex()

        source_columns = self.sourceModel().columnCount()
        if proxy_index.column() >= source_columns:
            # Виртуальная колонка действий не существует в исходной модели.
            return QModelIndex()

        return self.sourceModel().index(proxy_index.row(), proxy_index.column())

    def mapFromSource(self, source_index: QModelIndex) -> QModelIndex:
        if not source_index.isValid():
            return QModelIndex()
        return self.index(source_index.row(), source_index.column())

    def data(self, proxy_index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not proxy_index.isValid() or self.sourceModel() is None:
            return None

        source_columns = self.sourceModel().columnCount()

        if proxy_index.column() >= source_columns:
            if role == Qt.ItemDataRole.DisplayRole:
                return ""
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
            return None

        return self.sourceModel().data(self.mapToSource(proxy_index), role)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if self.sourceModel() is None:
            return None

        if orientation == Qt.Orientation.Horizontal:
            source_columns = self.sourceModel().columnCount()
            if section >= source_columns:
                if role == Qt.ItemDataRole.DisplayRole:
                    return self.action_header
                if role == Qt.ItemDataRole.TextAlignmentRole:
                    return Qt.AlignmentFlag.AlignCenter
                return None

        return self.sourceModel().headerData(section, orientation, role)

    def flags(self, proxy_index: QModelIndex):
        if not proxy_index.isValid():
            return Qt.ItemFlag.NoItemFlags

        if self.sourceModel() is None:
            return Qt.ItemFlag.ItemIsEnabled

        source_columns = self.sourceModel().columnCount()
        if proxy_index.column() >= source_columns:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        return self.sourceModel().flags(self.mapToSource(proxy_index))

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        if self.sourceModel() is None:
            return
        if column < self.sourceModel().columnCount():
            self.sourceModel().sort(column, order)


@dataclass(frozen=True)
class ActionButtonSpec:
    key: str
    text: str
    width: int
    danger: bool = False


class PasswordActionDelegate(QStyledItemDelegate):
    """
    Делегат только рисует визуальные кнопки в колонке "Действия".
    Нажатия обрабатываются в PasswordTableView.mouseReleaseEvent.
    """

    def __init__(self, table: "PasswordTableView", parent: Optional[QObject] = None):
        super().__init__(parent)
        self.table = table

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        if index.column() != self.table.action_column:
            super().paint(painter, option, index)
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        bg_color = QColor("#111823")
        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = QColor("#223C66")
        elif option.state & QStyle.StateFlag.State_MouseOver:
            bg_color = QColor("#151F2E")

        painter.fillRect(option.rect, bg_color)

        for spec, rect in self.table.action_button_rects(option.rect, index.row()).items():
            if spec.danger:
                fill = QColor("#4A1D26")
                border = QColor("#B44758")
                text_color = QColor("#FFD8DD")
            else:
                fill = QColor("#172238")
                border = QColor("#2B3B59")
                text_color = QColor("#F4F7FF")

            painter.setPen(QPen(border, 1))
            painter.setBrush(QBrush(fill))
            painter.drawRoundedRect(rect, 7, 7)

            painter.setPen(text_color)
            font = painter.font()
            font.setPointSize(9)
            font.setBold(False)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, spec.text)

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        if index.column() == self.table.action_column:
            return QSize(self.table.action_column_width, 48)
        return super().sizeHint(option, index)


class PasswordMaskDelegate(QStyledItemDelegate):
    """
    Делегат для колонки пароля.
    Значение в модели не меняет. Меняет только отображение.
    """

    def __init__(self, table: "PasswordTableView", parent: Optional[QObject] = None):
        super().__init__(parent)
        self.table = table

    def displayText(self, value, locale) -> str:
        # Здесь намеренно не маскируем, потому что нужно знать row/record_id.
        # Маскировка делается в paint.
        return "" if value is None else str(value)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        if index.column() != self.table.PASSWORD_COLUMN:
            super().paint(painter, option, index)
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        bg_color = QColor("#111823")
        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = QColor("#223C66")
        elif option.state & QStyle.StateFlag.State_MouseOver:
            bg_color = QColor("#151F2E")

        painter.fillRect(option.rect, bg_color)

        record_id = self.table.record_id_for_row(index.row())
        raw_value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        text = "" if raw_value is None else str(raw_value)

        if record_id not in self.table.visible_password_record_ids:
            text = "••••••••"

        painter.setPen(QColor("#F4F7FF"))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        text_rect = option.rect.adjusted(12, 0, -12, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)

        painter.restore()


class PasswordTableView(QTableView):
    """
    Таблица паролей.

    Она не удаляет, не редактирует и не копирует сама.
    Она только сообщает наружу: "нажали такую-то кнопку по такой-то записи".
    """

    copy_login_clicked = Signal(int, object)       # row, record_id
    copy_password_clicked = Signal(int, object)    # row, record_id
    show_password_clicked = Signal(int, object, bool)  # row, record_id, is_visible
    edit_clicked = Signal(int, object)             # row, record_id
    delete_clicked = Signal(int, object)           # row, record_id
    action_clicked = Signal(str, int, object)      # action_key, row, record_id

    ID_COLUMN = 0
    RECORD_NAME_COLUMN = 1
    SITE_COLUMN = 2
    LOGIN_COLUMN = 3
    EMAIL_COLUMN = 4
    PASSWORD_COLUMN = 5

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._user_model = None
        self._action_model: Optional[ActionColumnProxyModel] = None
        self.action_column = 6
        self.action_column_width = 400
        self.visible_password_record_ids = set()

        # Пока пользователь сам не потянул колонки мышью,
        # таблица будет автоматически красиво заполнять доступную ширину.
        self._auto_fit_columns = True
        self._applying_column_layout = False

        self.base_actions = (
            ActionButtonSpec("copy_login", "Логин", 58),
            ActionButtonSpec("copy_password", "Пароль", 68),
            ActionButtonSpec("show_password", "Показать", 82),
            ActionButtonSpec("edit", "Изм.", 58),
            ActionButtonSpec("delete", "Удалить", 72, True),
        )

        self.setMouseTracking(True)
        self.setAlternatingRowColors(False)
        self.setShowGrid(True)
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSortingEnabled(False)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(52)
        self.verticalHeader().setMinimumSectionSize(52)

        header = self.horizontalHeader()
        header.setHighlightSections(False)
        header.setSectionsClickable(True)
        header.setSectionsMovable(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setMinimumSectionSize(90)
        header.setStretchLastSection(True)

        # Если пользователь сам потянул колонку — больше не сбрасываем ширину автоматически.
        header.sectionResized.connect(self._on_section_resized)

        self.setItemDelegateForColumn(self.PASSWORD_COLUMN, PasswordMaskDelegate(self, self))

    def set_user_model(self, model):
        """
        Главный метод для подключения твоей модели/прокси-модели.

        На вход передаётся твоя модель с 6 колонками.
        Внутри она заворачивается в ActionColumnProxyModel с 7-й колонкой действий.
        """
        self._user_model = model
        self.visible_password_record_ids.clear()

        self._action_model = ActionColumnProxyModel(self)
        self._action_model.setSourceModel(model)

        super().setModel(self._action_model)

        self.action_column = self._action_model.columnCount() - 1
        self.setItemDelegateForColumn(self.PASSWORD_COLUMN, PasswordMaskDelegate(self, self))
        self.setItemDelegateForColumn(self.action_column, PasswordActionDelegate(self, self))

        self.configure_columns()

    def user_model(self):
        """Возвращает исходную модель, которую ты передал в set_user_model."""
        return self._user_model

    def action_model(self):
        """Возвращает UI-обёртку с колонкой действий."""
        return self._action_model

    def _on_section_resized(self, logical_index: int, old_size: int, new_size: int):
        """
        Qt вызывает этот метод, когда меняется ширина колонки.

        Если ширину меняет наш автоподгонщик — ничего не делаем.
        Если ширину меняет пользователь мышью — отключаем автоподгонку,
        чтобы таблица не сбрасывала его настройки.
        """
        if self._applying_column_layout:
            return

        if logical_index not in (self.ID_COLUMN, self.action_column):
            self._auto_fit_columns = False


    def reset_column_widths(self):
        """
        Вернуть аккуратную ширину колонок по умолчанию.

        Можно вызвать вручную:
            self.table_passwords.reset_column_widths()
        """
        self._auto_fit_columns = True
        self.fit_columns_to_view()


    def fit_columns_to_view(self):
        """
        Расставляет стартовые ширины колонок так, чтобы таблица выглядела нормально:
        - без серой пустоты справа;
        - с фиксированной колонкой действий;
        - с нормальными пропорциями текстовых колонок.
        """
        model = self.model()
        if model is None:
            return

        if model.columnCount() <= self.PASSWORD_COLUMN:
            return

        visible_columns = [
            self.RECORD_NAME_COLUMN,
            self.SITE_COLUMN,
            self.LOGIN_COLUMN,
            self.EMAIL_COLUMN,
            self.PASSWORD_COLUMN,
        ]

        min_widths = {
            self.RECORD_NAME_COLUMN: 150,
            self.SITE_COLUMN: 220,
            self.LOGIN_COLUMN: 170,
            self.EMAIL_COLUMN: 210,
            self.PASSWORD_COLUMN: 140,
        }

        weights = {
            self.RECORD_NAME_COLUMN: 1.2,
            self.SITE_COLUMN: 1.7,
            self.LOGIN_COLUMN: 1.3,
            self.EMAIL_COLUMN: 1.6,
            self.PASSWORD_COLUMN: 1.0,
        }

        viewport_width = self.viewport().width()
        available_width = max(0, viewport_width - self.action_column_width)

        min_total = sum(min_widths.values())

        self._applying_column_layout = True
        try:
            if self.action_column < model.columnCount():
                self.setColumnWidth(self.action_column, self.action_column_width)

            if available_width <= min_total:
                for column in visible_columns:
                    self.setColumnWidth(column, min_widths[column])
                return

            extra = available_width - min_total
            weight_total = sum(weights.values())

            used_width = 0
            for column in visible_columns[:-1]:
                width = min_widths[column] + int(extra * weights[column] / weight_total)
                self.setColumnWidth(column, width)
                used_width += width

            # Последняя обычная колонка забирает остаток,
            # чтобы не появлялась пустая зона справа из-за округлений.
            last_column = visible_columns[-1]
            last_width = max(
                min_widths[last_column],
                available_width - used_width,
            )
            self.setColumnWidth(last_column, last_width)

        finally:
            self._applying_column_layout = False
    
    def configure_columns(self):
        """
        Настраивает колонки таблицы.

        Обычные колонки можно растягивать мышью.
        Колонка "Действия" фиксированная.
        При первом отображении таблица сама красиво заполняет ширину окна.
        """
        model = self.model()
        if model is None:
            return

        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionsMovable(False)
        header.setMinimumSectionSize(90)

        # ID нужен логике, но пользователю не нужен.
        if model.columnCount() > self.ID_COLUMN:
            self.setColumnHidden(self.ID_COLUMN, True)

        # ВАЖНО:
        # Пока мы сами настраиваем ширины, sectionResized не должен считать,
        # что это пользователь руками потянул колонку.
        self._applying_column_layout = True

        try:
            for column in range(model.columnCount()):
                if column == self.ID_COLUMN:
                    continue

                if column == self.action_column:
                    header.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
                    self.setColumnWidth(column, self.action_column_width)
                else:
                    header.setSectionResizeMode(column, QHeaderView.ResizeMode.Interactive)
        finally:
            self._applying_column_layout = False

        if self._auto_fit_columns:
            self.fit_columns_to_view()

        self.resizeRowsToContents()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Пока пользователь сам не менял ширину колонок,
        # окно будет красиво подгонять таблицу под размер.
        if self._auto_fit_columns:
            self.fit_columns_to_view()

    def action_specs_for_row(self, row: int):
        record_id = self.record_id_for_row(row)
        specs = []
        for spec in self.base_actions:
            if spec.key == "show_password":
                if record_id in self.visible_password_record_ids:
                    specs.append(ActionButtonSpec("show_password", "Скрыть", 82))
                else:
                    specs.append(spec)
            else:
                specs.append(spec)
        return tuple(specs)

    def action_button_rects(self, cell_rect: QRect, row: int):
        """Возвращает прямоугольники кнопок внутри ячейки действий."""
        gap = 8

        specs = self.action_specs_for_row(row)
        total_width = sum(spec.width for spec in specs) + gap * (len(specs) - 1)

        # Центруем кнопки внутри колонки "Действия".
        # Так они не будут липнуть к левой границе и не будут залезать вправо.
        x = cell_rect.left() + max(8, (cell_rect.width() - total_width) // 2)

        y = cell_rect.top() + 9
        height = max(30, cell_rect.height() - 18)

        result = {}
        for spec in specs:
            result[spec] = QRect(x, y, spec.width, height)
            x += spec.width + gap
        return result

    def mouseMoveEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and index.column() == self.action_column:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        else:
            self.unsetCursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid() and index.column() == self.action_column:
                clicked = self.action_key_at(index, event.pos())
                if clicked:
                    self.emit_action(clicked, index.row())
                    event.accept()
                    return

        super().mouseReleaseEvent(event)

    def action_key_at(self, index: QModelIndex, position: QPoint) -> Optional[str]:
        rect = self.visualRect(index)
        for spec, button_rect in self.action_button_rects(rect, index.row()).items():
            if button_rect.contains(position):
                return spec.key
        return None

    def emit_action(self, action_key: str, row: int):
        record_id = self.record_id_for_row(row)

        if action_key == "show_password":
            if record_id in self.visible_password_record_ids:
                self.visible_password_record_ids.remove(record_id)
                is_visible = False
            else:
                self.visible_password_record_ids.add(record_id)
                is_visible = True
            self.viewport().update()
            self.show_password_clicked.emit(row, record_id, is_visible)
            self.action_clicked.emit(action_key, row, record_id)
            return

        if action_key == "copy_login":
            self.copy_login_clicked.emit(row, record_id)
        elif action_key == "copy_password":
            self.copy_password_clicked.emit(row, record_id)
        elif action_key == "edit":
            self.edit_clicked.emit(row, record_id)
        elif action_key == "delete":
            self.delete_clicked.emit(row, record_id)

        self.action_clicked.emit(action_key, row, record_id)

    def value_at(self, row: int, column: int):
        """
        Берёт значение из UI-модели по видимой строке и колонке.
        Подходит для copy_login/copy_password.
        """
        model = self.model()
        if model is None:
            return None
        index = model.index(row, column)
        return model.data(index, Qt.ItemDataRole.DisplayRole)

    def record_id_for_row(self, row: int):
        return self.value_at(row, self.ID_COLUMN)

    def source_index_from_view_index(self, view_index: QModelIndex) -> QModelIndex:
        """
        Возвращает индекс исходной модели из индекса таблицы.

        Нужен, если у тебя есть старый код с context menu и mapToSource.
        Важно: table_passwords.model() теперь не self.proxy, а ActionColumnProxyModel.
        """
        if not view_index.isValid():
            return QModelIndex()

        model = self.model()
        if isinstance(model, ActionColumnProxyModel):
            return model.mapToSource(view_index)
        return view_index


class Ui_MainWindow(object):
    """
    UI-класс в стиле файлов, которые генерирует pyside6-uic.

    Все важные виджеты имеют старые имена:
        self.user_name
        self.search
        self.add_data
        self.csv_import
        self.csv_export
        self.lock_storage
        self.table_passwords
    """

    ID_COLUMN = PasswordTableView.ID_COLUMN
    RECORD_NAME_COLUMN = PasswordTableView.RECORD_NAME_COLUMN
    SITE_COLUMN = PasswordTableView.SITE_COLUMN
    LOGIN_COLUMN = PasswordTableView.LOGIN_COLUMN
    EMAIL_COLUMN = PasswordTableView.EMAIL_COLUMN
    PASSWORD_COLUMN = PasswordTableView.PASSWORD_COLUMN

    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1180, 720)
        MainWindow.setMinimumSize(900, 560)
        MainWindow.setWindowTitle("Password Manager")

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.root_layout = QVBoxLayout(self.centralwidget)
        self.root_layout.setContentsMargins(18, 18, 18, 18)
        self.root_layout.setSpacing(14)

        self.top_bar = QFrame(self.centralwidget)
        self.top_bar.setObjectName("top_bar")
        self.top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(16, 14, 16, 14)
        self.top_bar_layout.setSpacing(12)

        self.title_block = QVBoxLayout()
        self.title_block.setSpacing(2)

        self.app_title = QLabel("Менеджер паролей", self.top_bar)
        self.app_title.setObjectName("app_title")
        self.app_subtitle = QLabel("Локальное хранилище записей", self.top_bar)
        self.app_subtitle.setObjectName("app_subtitle")

        self.title_block.addWidget(self.app_title)
        self.title_block.addWidget(self.app_subtitle)
        self.top_bar_layout.addLayout(self.title_block)

        self.top_bar_layout.addItem(QSpacerItem(24, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.user_caption = QLabel("Пользователь", self.top_bar)
        self.user_caption.setObjectName("user_caption")
        self.top_bar_layout.addWidget(self.user_caption)

        self.user_name = QLabel("", self.top_bar)
        self.user_name.setObjectName("user_name")
        self.user_name.setMinimumWidth(120)
        self.user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.top_bar_layout.addWidget(self.user_name)

        self.root_layout.addWidget(self.top_bar)

        self.toolbar = QFrame(self.centralwidget)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(16, 12, 16, 12)
        self.toolbar_layout.setSpacing(10)

        self.search = QLineEdit(self.toolbar)
        self.search.setObjectName("search")
        self.search.setPlaceholderText("Поиск по названию, сайту, логину или почте")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumHeight(38)
        self.search.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toolbar_layout.addWidget(self.search)

        self.add_data = QPushButton("Добавить запись", self.toolbar)
        self.add_data.setObjectName("add_data")
        self.add_data.setMinimumHeight(38)
        self.toolbar_layout.addWidget(self.add_data)

        self.csv_import = QPushButton("Импорт CSV", self.toolbar)
        self.csv_import.setObjectName("csv_import")
        self.csv_import.setMinimumHeight(38)
        self.toolbar_layout.addWidget(self.csv_import)

        self.csv_export = QPushButton("Экспорт CSV", self.toolbar)
        self.csv_export.setObjectName("csv_export")
        self.csv_export.setMinimumHeight(38)
        self.toolbar_layout.addWidget(self.csv_export)

        self.lock_storage = QPushButton("Заблокировать", self.toolbar)
        self.lock_storage.setObjectName("lock_storage")
        self.lock_storage.setMinimumHeight(38)
        self.toolbar_layout.addWidget(self.lock_storage)

        self.root_layout.addWidget(self.toolbar)

        self.table_card = QFrame(self.centralwidget)
        self.table_card.setObjectName("table_card")
        self.table_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_card_layout = QVBoxLayout(self.table_card)
        self.table_card_layout.setContentsMargins(0, 0, 0, 0)
        self.table_card_layout.setSpacing(0)

        self.table_passwords = PasswordTableView(self.table_card)
        self.table_passwords.setObjectName("table_passwords")
        self.table_passwords.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_card_layout.addWidget(self.table_passwords)

        self.empty_state = QLabel("Записей пока нет. Нажми «Добавить запись», чтобы создать первую.", self.table_card)
        self.empty_state.setObjectName("empty_state")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setVisible(False)
        self.table_card_layout.addWidget(self.empty_state)

        self.root_layout.addWidget(self.table_card, 1)

        self.bottom_bar = QFrame(self.centralwidget)
        self.bottom_bar.setObjectName("bottom_bar")
        self.bottom_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_bar_layout.setContentsMargins(16, 10, 16, 10)
        self.bottom_bar_layout.setSpacing(8)

        self.status_label = QLabel("Всего записей: 0", self.bottom_bar)
        self.status_label.setObjectName("status_label")
        self.bottom_bar_layout.addWidget(self.status_label)

        self.bottom_bar_layout.addItem(QSpacerItem(24, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.hint_label = QLabel("Пароли скрыты. Для действий используй кнопки в строке или контекстное меню.", self.bottom_bar)
        self.hint_label.setObjectName("hint_label")
        self.bottom_bar_layout.addWidget(self.hint_label)

        self.root_layout.addWidget(self.bottom_bar)

        self.apply_style(MainWindow)
        self.apply_shadow(self.top_bar, blur=24, y_offset=4, alpha=70)
        self.apply_shadow(self.toolbar, blur=24, y_offset=4, alpha=60)
        self.apply_shadow(self.table_card, blur=28, y_offset=5, alpha=80)

    def apply_shadow(self, widget: QWidget, blur: int = 22, y_offset: int = 3, alpha: int = 60):
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, y_offset)
        shadow.setColor(QColor(0, 0, 0, alpha))
        widget.setGraphicsEffect(shadow)

    def set_passwords_model(self, model):
        """
        Подключает модель данных к таблице.

        Используй этот метод вместо self.table_passwords.setModel(...),
        если хочешь сохранить красивую колонку действий.
        """
        self.table_passwords.set_user_model(model)
        self.update_empty_state()
        self.update_status_label()

    def update_empty_state(self):
        model = self.table_passwords.model()
        rows = model.rowCount() if model is not None else 0
        has_rows = rows > 0
        self.table_passwords.setVisible(has_rows)
        self.empty_state.setVisible(not has_rows)

    def update_status_label(self):
        model = self.table_passwords.model()
        rows = model.rowCount() if model is not None else 0
        self.status_label.setText(f"Всего записей: {rows}")

    def refresh_table_ui(self):
        """
        Вызывай после фильтрации/обновления модели, если модель уже установлена.
        """
        self.table_passwords.configure_columns()
        self.update_empty_state()
        self.update_status_label()
        self.table_passwords.viewport().update()

    def apply_style(self, MainWindow: QMainWindow):
        MainWindow.setStyleSheet(
            """
            QMainWindow {
                background: #0B0F17;
                color: #F4F7FF;
                font-family: "Segoe UI", "Inter", "Arial";
                font-size: 10pt;
            }

            QWidget#centralwidget {
                background: #0B0F17;
                color: #F4F7FF;
            }

            QFrame#top_bar,
            QFrame#toolbar,
            QFrame#bottom_bar {
                background: #111823;
                border: 1px solid #1F2A3C;
                border-radius: 14px;
            }

            QFrame#table_card {
                background: #111823;
                border: 1px solid #1F2A3C;
                border-radius: 14px;
            }

            QLabel#app_title {
                color: #F4F7FF;
                font-size: 18pt;
                font-weight: 700;
            }

            QLabel#app_subtitle,
            QLabel#user_caption,
            QLabel#status_label,
            QLabel#hint_label {
                color: #9AA8BF;
                font-size: 9.5pt;
            }

            QLabel#user_name {
                background: #172238;
                color: #E7EEFF;
                border: 1px solid #2B3B59;
                border-radius: 10px;
                padding: 8px 12px;
                font-weight: 600;
            }

            QLabel#empty_state {
                background: #111823;
                color: #9AA8BF;
                font-size: 13pt;
                padding: 42px;
                border-radius: 14px;
            }

            QLineEdit#search {
                background: #0D1320;
                color: #F4F7FF;
                border: 1px solid #26344C;
                border-radius: 10px;
                padding: 8px 12px;
                selection-background-color: #2D5590;
            }

            QLineEdit#search:focus {
                border: 1px solid #5E8DFF;
                background: #10192B;
            }

            QPushButton {
                background: #172238;
                color: #F4F7FF;
                border: 1px solid #2B3B59;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #20304D;
                border: 1px solid #42618F;
            }

            QPushButton:pressed {
                background: #0F1728;
            }

            QPushButton#add_data {
                background: #23456F;
                border: 1px solid #4979B6;
            }

            QPushButton#add_data:hover {
                background: #2A5489;
            }

            QPushButton#lock_storage {
                background: #3A1E2D;
                border: 1px solid #79415A;
            }

            QPushButton#lock_storage:hover {
                background: #4A2739;
            }

            QTableView#table_passwords {
                background: #111823;
                alternate-background-color: #111823;
                color: #F4F7FF;
                border: none;
                border-radius: 14px;
                gridline-color: #1B2A40;
                selection-background-color: #223C66;
                selection-color: #FFFFFF;
                outline: 0;
            }

            QTableView#table_passwords::item {
                background: #111823;
                border-right: 1px solid #162235;
                border-bottom: 1px solid #0E1623;
                padding: 10px;
            }

            QTableView#table_passwords::item:selected {
                background: #223C66;
                color: #FFFFFF;
            }

            QHeaderView::section {
                background: #1A2333;
                color: #CFE0FF;
                border: none;
                border-right: 1px solid #2E3B52;
                border-bottom: 1px solid #2A364B;
                padding: 12px 10px;
                font-weight: 700;
            }

            QHeaderView::section:hover {
                background: #202B3E;
                border-right: 1px solid #5E8DFF;
            }

            QHeaderView::section:first {
                border-top-left-radius: 14px;
            }

            QScrollBar:vertical {
                background: #0D1320;
                width: 12px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #26344C;
                border-radius: 6px;
                min-height: 28px;
            }

            QScrollBar::handle:vertical:hover {
                background: #3A4F72;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                background: #0D1320;
                height: 12px;
                margin: 0px;
            }

            QScrollBar::handle:horizontal {
                background: #26344C;
                border-radius: 6px;
                min-width: 28px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #3A4F72;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            """
        )


if __name__ == "__main__":
    # Пустой предпросмотр UI без демо-записей.
    # Для реального проекта импортируй Ui_MainWindow и наследуйся от него.
    import sys
    from PySide6.QtCore import QAbstractTableModel

    class EmptyTableModel(QAbstractTableModel):
        headers = ["ID", "Имя записи", "Имя сайта/ссылка", "Логин", "Почта", "Пароль"]

        def rowCount(self, parent=QModelIndex()):
            return 0

        def columnCount(self, parent=QModelIndex()):
            return len(self.headers)

        def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
            if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
            return None

    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    ui.user_name.setText("user")
    ui.set_passwords_model(EmptyTableModel())
    window.show()
    sys.exit(app.exec())
