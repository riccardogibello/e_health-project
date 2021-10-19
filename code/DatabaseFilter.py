import threading
import time

from DatabaseManager import do_query, delete_app_from_database
from concurrent.futures import ThreadPoolExecutor
import re
from settings import MAX_FILTER_THREADS


def detect_chinese(string):
    if not string:
        return None
    filtered_string = re.sub(r'([\u4e00-\u9fff]+)', '', string)
    return not filtered_string == string


def detect_russian(string):
    if not string:
        return None
    filtered_string = re.sub(r'[\u0400-\u04FF]', '', string)
    return not filtered_string == string


def detect_greek(string):
    if not string:
        return None
    filtered_string = re.sub(r'[\u0370-\u03FF]', '', string)
    return not filtered_string == string


def detect_arabic(string):
    if not string:
        return None
    filtered_string = re.sub(r'([\u0600-\u06FF])', '', string)
    filtered_string = re.sub(r'([\u0750-\u077F])', '', filtered_string)
    filtered_string = re.sub(r'([\ufb50-\ufc3f])', '', filtered_string)
    filtered_string = re.sub(r'([\ufe70-\ufefc])', '', filtered_string)
    return not filtered_string == string


def detect_korean(string):
    if not string:
        return None
    filtered_string = re.sub(r'([\uac00-\ud7a3])', '', string)
    filtered_string = re.sub(r'([\u1100-\u11ff])', '', filtered_string)
    filtered_string = re.sub(r'([\u3130-\u318f])', '', filtered_string)
    filtered_string = re.sub(r'([\ud7b0-\ud7ff])', '', filtered_string)
    return not filtered_string == string


def detect_katakana(string):
    if not string:
        return None
    filtered_string = re.sub(r'([\u30a0-\u30ff])', '', string)
    return not filtered_string == string


def detect_hiragana(string):
    if not string:
        return None
    filtered_string = re.sub(r'([\u3040-\u309f])', '', string)
    return not filtered_string == string


def detect_syrian(string):
    if not string:
        return None
    filtered_string = re.sub(r'([\u0700-\u074f])', '', string)
    return not filtered_string == string


def filter_name(app_id, app_name):
    if detect_chinese(app_name):
        print(f'DETECTED CHINESE APP : {app_name}')
        delete_app_from_database(app_id)
    elif detect_arabic(app_name):
        print(f'DETECTED ARABIC APP : {app_name}')
        delete_app_from_database(app_id)
    elif detect_russian(app_name):
        print(f'DETECTED RUSSIAN APP : {app_name}')
        delete_app_from_database(app_id)
    elif detect_korean(app_name):
        print(f'DETECTED KOREAN APP : {app_name}')
        delete_app_from_database(app_id)
    elif detect_katakana(app_name):
        print(f'DETECTED KATAKANA APP : {app_name}')
        delete_app_from_database(app_id)
    elif detect_hiragana(app_name):
        print(f'DETECTED HIRAGANA APP : {app_name}')
        delete_app_from_database(app_id)
    elif detect_greek(app_name):
        print(f'DETECTED GREEK APP : {app_name}')
        delete_app_from_database(app_id)
    elif detect_syrian(app_name):
        print(f'DETECTED SYRIAN APP : {app_name}')
        delete_app_from_database(app_id)


class DatabaseFilter:
    __running = True
    __app_list = None
    __name_filtered = 0

    def __init__(self):
        print(f'Database Filter started in thread : {threading.currentThread()}')

    def filter_apps_name(self):
        self.__running = True
        self.__name_filtered = 0
        while self.__running:
            query = (
                "SELECT app_id, app_name FROM app WHERE app_name IS NOT NULL"
            )
            self.__app_list = do_query((), query)
            list_length = len(self.__app_list)
            if self.__name_filtered == list_length:
                if list_length == 0:
                    time.sleep(60)
                    continue
                else:
                    self.__running = True
                    break
            self.__name_filtered = len(self.__app_list)

            with ThreadPoolExecutor(max_workers=MAX_FILTER_THREADS) as executor:
                for result_tuple in self.__app_list:
                    executor.submit(filter_name, result_tuple[0], result_tuple[1])
