from src.auth_window_ui import Ui_AuthWindow
#from src.main_window_interface import Ui_MainWindow
from src.password_manager_ui_pure import Ui_MainWindow
from src.dialog_add_password_interface import Ui_Add_password
from src.dialog_csv_import_interface import Ui_Dialog
from src.dialog_csv_export_interface import Export_Ui_Dialog
from PySide6.QtWidgets import QMainWindow, QDialog, QFileDialog, QCheckBox
from src.api import API
from src.table_model import PasswordsTabel, MultiIndexFilter
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, Slot
import logging
from src.create_context_menu import ContextMenu
from PySide6.QtCore import Qt
import json
import os

#Класс функциональности интерфейса регистрации и авторизации
class LogInApp(Ui_AuthWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.registration_button.clicked.connect(self.registration_method)
        self.login_button.clicked.connect(self.log_in_method)
        self.show_passwords.toggled.connect(self.set_passwords_visible)
        
    #Взаимодействие функции регистрации с интерфейсом через API
    def registration_method(self):
        if self.user_password.text() == self.user_password_repeat.text():
            if API.registration_api(self, user_name=self.get_login_text(), user_password=self.user_password.text()):
                self.swap_mainwindow()
            else:
                self.set_status("Пользователь уже зарегистрирован", error=True)
        else:
            self.set_status("Повторный пароль неверный", error=True)
    
    #Взаимодействие функции входа в программу с интерфейсом через API
    def log_in_method(self):
        if self.user_password.text() == self.user_password_repeat.text():
            if API.log_in_api(self, user_name=self.get_login_text(), user_password=self.user_password.text()):
                self.swap_mainwindow()
            else:
                self.set_status("Логин не верный или пользователя не существует", error=True)
        else:
            self.set_status("Повторный пароль неверный", error=True)
    
    #Функция перехода на основное окно
    def swap_mainwindow(self):
        API.set_password_cache_api(self, "PASSWORD_LOG_IN", self.user_password.text())
        self.close()
        self.window = MainWindow(self.get_login_text())
        API.keys_generation_api(self, API.get_password_cache_api(self,  name_service="PASSWORD_LOG_IN"))
        self.window.show()

#Класс функциональности интерфейса основного окна 
class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, user_name_data):
        super().__init__()
        self.setupUi(self)
        self.user_name_data = user_name_data
        self.user_name.setText(user_name_data)
        
        self.proxy = MultiIndexFilter(None)
        self.setMouseTracking(True)
        
        self.add_data.clicked.connect(self.open_dialog_add_password)
        self.csv_import.clicked.connect(self.open_dialog_import_passwords)
        self.csv_export.clicked.connect(self.open_dialog_export_passwords)
        self.search.textEdited.connect(self.search_passwords)
        
        self.table_passwords.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.table_passwords.delete_clicked.connect(self.del_password)
        self.table_passwords.copy_login_clicked.connect(self.copy_login_from_table)
        self.table_passwords.copy_password_clicked.connect(self.copy_password_from_table)
        
        self.update_table()
    
    #Запуск поиска
    def search_passwords(self):
        self.proxy.allowed_index = None
        self.proxy.invalidateFilter()
        self.set_passwords_model(self.proxy)
        all_data = []
        
        for row in range(self.table_passwords.model().rowCount()):
            row_data = []
            for column in range(self.table_passwords.model().columnCount()):
                item = self.table_passwords.model().data(self.table_passwords.model().index(row, column))
                row_data.append(item)
            all_data.append(row_data)
            
        index_passwords = API.search_passwords_api(self, self.search.text(), all_data)
        self.proxy.allowed_index = index_passwords
        self.proxy.invalidateFilter()
        self.set_passwords_model(self.proxy)
        
    #Открытие диалогового окна
    @Slot()
    def open_dialog_add_password(self):
        dialog_window = DialogAddPassword()
        dialog_window.saved_table_passwords.connect(self.update_table)
        dialog_window.exec()
    
    #Функция обнавления таблицы паролей
    @Slot(bool)
    def update_table(self):
        self.proxy.allowed_index = None
        self.proxy.invalidateFilter()
        data = API.data_passwords_api(self) or []
        header = ["ID","Имя записи", "Имя сайта/ссылка", "Логин", "Почта", "Пароль"]
            
        model_table = PasswordsTabel(data, header)
        self.proxy.setSourceModel(model_table)
        self.set_passwords_model(self.proxy)
    
    #Метод удаления записи
    def del_password(self, row, record_id):
        API.del_data_api(self, str(record_id))
        self.update_table()
    
    #Метод открытия окна импорта паролей из csv файла
    @Slot()
    def open_dialog_import_passwords(self):
        dialog_windows = DialogImportPasswords()
        dialog_windows.saved_table_passwords_csv.connect(self.update_table)
        dialog_windows.exec()
    
    #Метод открытия окна экспорта паролей в csv файл
    def open_dialog_export_passwords(self):
        dialog_windows = DialogExportPasswords()
        dialog_windows.exec()
    
    def copy_login_from_table(self, row, record_id):
        login = self.table_passwords.value_at(row, self.LOGIN_COLUMN)
        QApplication.clipboard().setText(str(login))
    
    def copy_password_from_table(self, row, record_id):
        password = self.table_passwords.value_at(row, self.PASSWORD_COLUMN)
        QApplication.clipboard().setText(str(password))
        

#Диалоговое окно добавления пароля
class DialogAddPassword(Ui_Add_password, QDialog):
    #Сигнал сохранения записи в базе данных
    saved_table_passwords = Signal(bool)
    
    def __init__(self):
        super().__init__()
        
        self.setupUi(self)
        self.len_password.hide()
        self.gen_password.hide()
        try:
            self.buttonBox.accepted.disconnect()
        except TypeError:
            pass
        self.buttonBox.accepted.connect(self.required_fields_validator)
        self.gen_check.checkStateChanged.connect(self.check_gen_checkbox)
        self.gen_password.clicked.connect(self.generation_password)
    
    #Валидатор обязательных полей
    @Slot()
    def required_fields_validator(self):
        if not self.password_input.text().split():
            self.password_input.setStyleSheet("border: 1px solid red;")
        else:
            enc_password_input = API.encryption_data_api(self, self.password_input.text(), API.get_password_cache_api(self, "PASSWORD_LOG_IN"))
            enc_email_input = API.encryption_data_api(self, self.email_input.text(), API.get_password_cache_api(self, "PASSWORD_LOG_IN"))
            API.add_password_api(self, self.name_input.text(), self.sit_input.text(), self.login_input.text(), enc_email_input, enc_password_input)
            self.saved_table_passwords.emit(True)
            self.accept()
            self.saved_table_passwords.emit(False)
    
    def check_gen_checkbox(self, state):
        if state == Qt.CheckState.Checked:
            self.len_password.show()
            self.gen_password.show()
        else:
            self.len_password.hide()
            self.gen_password.hide()
    
    def generation_password(self):
        gen_password = API.generation_password_api(self, int(self.len_password.text()))
        if gen_password:
            self.password_input.setText(gen_password)

#Класс диалогового окна импорта паролей
class DialogImportPasswords(Ui_Dialog, QDialog):
    #Сигнал сохранения записи в базе данных
    saved_table_passwords_csv = Signal(bool)
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        try:
            self.buttonBox.accepted.disconnect()
        except TypeError:
            pass
        self.button_dir.clicked.connect(self.open_dialog_file)
        self.buttonBox.accepted.connect(self.import_csv_passwords)
    
    #Метод открытия окна файлового менеджера    
    def open_dialog_file(self):
        csv_path = "C:/"
        with open("config\config.json", "r") as config:
            config_file = json.load(config)
        try:
            csv_path = config_file["path"]["default_csv_path"]
        except:
            config_file["path"]["default_csv_path"] = os.path.dirname(os.path.abspath(__file__))
            with open("config\config.json", "w") as config:
                json.dump(config_file, config, indent=4)
                
        csv_file, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файлы", csv_path, "CSV файлы (*.csv)")
        self.name_dir.setText(csv_file)
        with open("config\config.json", "w") as config:
            config_file["path"]["default_csv_path"] = os.path.dirname(os.path.abspath(csv_file))
            json.dump(config_file, config, indent=4)
    
    #Метод вызывающий функцию сериализации и сохроняющий все данные в таблице
    def import_csv_passwords(self):
        if self.name_dir.text():
            passwords_csv = API.import_csv_passwords_api(self, self.name_dir.text())
            for value in passwords_csv:
                API.add_password_api(self, name=value["name_sit"], name_sit=value["url"], login=value["username"], mail=API.encryption_data_api(self, value["username"], API.get_password_cache_api(self, "PASSWORD_LOG_IN")), password=API.encryption_data_api(self, value["password"], API.get_password_cache_api(self, "PASSWORD_LOG_IN")))
            self.saved_table_passwords_csv.emit(True)
            self.accept()
            self.saved_table_passwords_csv.emit(False)
        else:
            self.name_dir.setStyleSheet("border: 1px solid red;")

#Класс диалогового окна экспорта csv файла
class DialogExportPasswords(Export_Ui_Dialog, QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        try:
            self.buttonBox.accepted.disconnect()
        except TypeError:
            pass
        
        self.button_dir.clicked.connect(self.open_dialog_file)
        self.buttonBox.accepted.connect(self.export_csv_passwords)
    
    #Метод открытия окна файлового менеджера
    def open_dialog_file(self):
        csv_path = "C:/"
        
        with open("config\config.json", "r") as config:
            config_file = json.load(config)
        try:
            csv_path = config_file["path"]["default_csv_path"]
        except:
            config_file["path"]["default_csv_path"] = os.path.dirname(os.path.abspath(__file__))
            with open("config\config.json", "w") as config:
                json.dump(config_file, config, indent=4)
                 
        csv_file, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файлы", csv_path, "CSV файлы (*.csv)")
        self.name_dir.setText(csv_file)
        with open("config\config.json", "w") as config:
            config_file["path"]["default_csv_path"] = os.path.dirname(os.path.abspath(csv_file))
            json.dump(config_file, config, indent=4)
    
    #Метод вызова функции экспорта
    def export_csv_passwords(self):
        API.export_csv_passwords_api(self, self.name_dir.text())
        self.accept()