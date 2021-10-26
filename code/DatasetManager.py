import time
import langid
import pandas
import threading
from concurrent.futures import ThreadPoolExecutor
import DatabaseManager
from DatabaseManager import insert_id_into_preliminary_db as insert_preliminary_id
from settings import SERIOUS_GAMES_CATEGORIES_LIST, MAX_DATASET_THREADS, DEBUG, DATASET_DEBUG


def is_english(string):
    # Using langid package checks language of input string
    # Returns True if the string is english, False otherwise
    return langid.classify(string)[0] == 'en'


class DatasetManager:
    __apps_list = None
    __dataset_file = None
    __in_database_apps = None

    def __init__(self, dataset_file):
        threading.currentThread().name = 'Dataset Manager'
        if DEBUG and DATASET_DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager: Started')
        # Constructor reads the file and stores in memory a DataFrame
        # object (from pandas package) containing the list of the applications
        self.__in_database_apps = [app for tuples in DatabaseManager.get_apps_from_preliminary() for app in tuples]
        self.__in_database_apps.sort()
        self.__dataset_file = dataset_file
        self.read_file()

    def load_apps_into_db(self, filter_categories=SERIOUS_GAMES_CATEGORIES_LIST):
        # Method used to load in the database data of the application
        # Insertion of data in the db is made using multithreading in order to improve performance
        start_time = time.time()
        if DEBUG and DATASET_DEBUG:
            print(f'{threading.currentThread().getName()}  || Dataset Manager : Loading data from {self.__dataset_file}')

        # Using ThreadPoolExecutor the insertion in the database is parallelized
        # The maximum number of Threads for the given job can be modified in the settings file
        with ThreadPoolExecutor(max_workers=MAX_DATASET_THREADS) as executor:
            for app_index in range(len(self.__apps_list)):
                if self.__apps_list.loc[app_index, 'Category'] in filter_categories:
                    app_id = self.__apps_list.loc[app_index, 'App Id']
                    app_name = self.__apps_list.loc[app_index, 'App Name']
                    if not self.is_in_database(app_id):
                        executor.submit(self.__store_app_data, app_id, app_name)

        end_time = time.time()
        if DEBUG and DATASET_DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager : Data from {self.__dataset_file} loaded '
                  f'in {round(end_time - start_time, 1)} s')

    def is_in_database(self, app_id):
        if app_id in self.__in_database_apps:
            self.__in_database_apps.remove(app_id)
            if DEBUG and DATASET_DEBUG:
                print(f'{threading.currentThread()}  || Dataset Manager: {app_id} already present in database ')
            return True
        return False

    def __delete_column(self, column_name):
        # Method deleting from DataFrame app list a given column

        self.__apps_list.pop(column_name)

    def filter_key_columns(self, key_columns):
        # Methods deletes from DataFrame object the columns not included in the given set

        if DEBUG and DATASET_DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager: Filtering columns ')

        for column in self.__apps_list.columns.values:
            if column not in key_columns:
                self.__apps_list.pop(column)

    def __store_app_data(self, app_id, app_name):
        # Given a DataFrame row checks if the app has english name
        # and then inserts the id into preliminary table in the database
        if not is_english(app_name):
            return
        insert_preliminary_id(app_id, from_dataset_flag=True)

    def read_file(self):
        # Reads the file and stores in memory DataFrame object
        start_time = time.time()
        if DEBUG and DATASET_DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager : Reading dataset file')
        self.__apps_list = pandas.read_csv(self.__dataset_file)
        end_time = time.time()
        if DEBUG and DATASET_DEBUG:
            print(
                f'{threading.currentThread()}  || Dataset Manager : Reading of \'{self.__dataset_file}\' '
                f'completed in {round(end_time - start_time, 1)} s')

    def shutdown(self):
        # Explicitly delete the reference to DataFrame object in order to free memory

        if DEBUG and DATASET_DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager: execution terminated')
        self.__apps_list = None
