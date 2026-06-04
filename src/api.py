import sys
import os

from keyring import get_password
sys.path.append(os.path.abspath('../src'))

import src.encryption
from src.log_in import LogIn
from src.db import DataBase
from src.generation_keys import Keys
from src.encryption import EncryptionText
from src.decryption import Decryption
from src.csv_import import PasswordCSV
from src.csv_export import PasswordCSVExport
from src.search import Search
from src.generation_password import GenerationPassword
from src.cache_pwd import CachePassword

#Класс API слоя между логикой и интерфейсом
class API:
    def __init__(self):
        pass
    
    #Вызов функции регистрации
    def registration_api(self, user_name:str, user_password:str):
        return LogIn(user_name, user_password).registration()
    
    #Вызов функции входа
    def log_in_api(self, user_name:str, user_password:str):
        return LogIn(user_name, user_password).log_in()
    
    #Вызов функции получения данных пользователя
    def data_user_api(self):
        return DataBase().retrieve_data_user()
    
    #Вызов функции получения данных паролей
    def data_passwords_api(self):
        return DataBase().retrieve_data_passwords()
    
    #Вызов функции создания таблицы паролей
    def add_password_api(self, name:str=None, name_sit:bytes=None, login:bytes=None, mail:bytes=None, password:bytes=None):
        return DataBase.create_passwords_db(self, name, name_sit, login, mail, password)
    
    #Вызов функции обновления таблицы паролей
    def uptade_password_api(self, id:int, name:str=None, name_sit:str=None, login:str=None, mail:bytes=None, password:bytes=None):
        return DataBase.update_password(self, id, name, name_sit, login, mail, password)
    
    #Вызов функции генерации ключей шифрования
    def keys_generation_api(self, password):
        Keys(password).run()
    
    #Вызов функции шифрования текста    
    def encryption_data_api(self, data:str, password:str):
        return EncryptionText(data, password).encryption_text()
    
    #Вызов функции дешифровки данных
    def decryption_data_api(self, data:bytes, password):
        return Decryption(data, password).decryption()
    
    #Вызов функции удаления данных
    def del_data_api(self, id:int):
        return DataBase.del_data(self, id)
    
    #Вызов функции сериализации данных из файла csv
    def import_csv_passwords_api(self, file_name):
        return PasswordCSV(file_name).processing_csv()
    
    #Вызов функции экспорта паролей в csv файл
    def export_csv_passwords_api(self, file_name):
        return PasswordCSVExport(file_name).write_file_csv()
    
    #Вызов функции поиска
    def search_passwords_api(self, key_name, array):
        return Search(key_name, array).multidimensional_array()
    
    #Вызов функции генирации пароля
    def generation_password_api(self, len_password):
        return GenerationPassword(len_password).generation_password()
    
    #Вызов функции помещения данных в кэш
    def set_password_cache_api(self, name_service, password):
        CachePassword(password=password, name_service=name_service).set_password()
    
    #Вызов функции выдачи данных из кэша
    def get_password_cache_api(self, name_service):
        return CachePassword(name_service=name_service).get_password()
    
    #Вызов удаления данных из кэша
    def del_password_api(self, name_service):
        CachePassword(name_service=name_service).del_password()
