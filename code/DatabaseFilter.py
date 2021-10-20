import langid
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from settings import SERIOUS_GAMES_CATEGORIES_LIST

import mysql.connector.errors

from DatabaseManager import do_query, delete_app_from_database
from settings import MAX_FILTER_THREADS


def filter_name(app_id, app_name):
    if langid.classify(app_name)[0] == 'en':
        query = (
            "UPDATE APP SET name_filtered = TRUE WHERE app_id = %s"
        )
        do_query((app_id,), query)
    else:
        delete_app_from_database(app_id)

def filter_cat(app_id, category):
    if category not in SERIOUS_GAMES_CATEGORIES_LIST:
        delete_app_from_database(app_id)
        print(f'{app_id} not in serious category')

def filter_desc(app_id, app_description):
    if langid.classify(app_description)[0] == 'en':
        query = (
            "UPDATE APP SET reviews = 'filter' WHERE app_id = %s"
        )
        do_query((app_id,), query)
    else:
        delete_app_from_database(app_id)
        print(f'app {app_id} is not english!')


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
                "SELECT app_id, app_name FROM app WHERE app_name IS NOT NULL AND name_filtered IS FALSE LIMIT 1000 "
            )
            try:
                self.__app_list = do_query((), query)
            except mysql.connector.errors.DatabaseError:
                self.__app_list = []
                print('filter missin connection')
                time.sleep(1)
                continue
            self.__name_filtered = len(self.__app_list)
            if self.__name_filtered == 0:
                time.sleep(30)
            elif self.__name_filtered < 50:
                time.sleep(1)

            print(f'Filtering {self.__name_filtered} apps')

            with ThreadPoolExecutor(max_workers=MAX_FILTER_THREADS) as executor:
                for result_tuple in self.__app_list:
                    executor.submit(filter_name, result_tuple[0], result_tuple[1])
                    self.__app_list.remove(result_tuple)


            query = (
                "SELECT app_id, description FROM app WHERE description IS NOT NULL AND reviews IS NULL"
            )
            try:
                self.__app_list = do_query((), query)
            except mysql.connector.errors.DatabaseError:
                print('filter missin connection')
                continue

            with ThreadPoolExecutor(max_workers=MAX_FILTER_THREADS) as executor:
                for result_tuple in self.__app_list:
                    executor.submit(filter_desc, result_tuple[0], result_tuple[1])
                    self.__app_list.remove(result_tuple)

            query = (
                "SELECT app_id, category FROM app WHERE description IS NOT NULL"
            )
            try:
                self.__app_list = do_query((), query)
            except mysql.connector.errors.DatabaseError:
                print('filter missin connection')
                continue

            with ThreadPoolExecutor(max_workers=MAX_FILTER_THREADS) as executor:
                for result_tuple in self.__app_list:
                    executor.submit(filter_cat, result_tuple[0], result_tuple[1])
                    self.__app_list.remove(result_tuple)
            self.__app_list = None
