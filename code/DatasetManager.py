import time

import langid
import pandas
import threading

from concurrent.futures import ThreadPoolExecutor
from DatabaseManager import insert_id_into_preliminary_db as insert_preliminary_id
from settings import SERIOUS_GAMES_CATEGORIES_LIST, MAX_DATASET_THREADS, DEBUG


def is_english(string):
    # Using langid package checks language of input string
    # Returns True if the string is english, False otherwise
    return langid.classify(string)[0] == 'en'


class DatasetManager:
    __apps_list = None
    __dataset_file = None

    def __init__(self, dataset_file):
        if DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager : Started')
        # Constructor reads the file and stores in memory a DataFrame
        # object (from pandas package) containing the list of the applications

        self.__dataset_file = dataset_file
        self.read_file()

    def load_apps_into_db(self, filter_categories=SERIOUS_GAMES_CATEGORIES_LIST):
        # Method used to load in the database data of the application
        # Insertion of data in the db is made using multithreading in order to improve performance
        start_time = time.time()
        if DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager : Loading data from {self.__dataset_file}')

        # Using ThreadPoolExecutor the insertion in the database is parallelized
        # The maximum number of Threads for the given job can be modified in the settings file
        with ThreadPoolExecutor(max_workers=MAX_DATASET_THREADS) as executor:
            for app_index in range(len(self.__apps_list)):
                if self.__apps_list.loc[app_index, 'Category'] in filter_categories:
                    executor.submit(self.__store_app_data, self.__apps_list.loc[app_index])
        end_time = time.time()
        if DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager : Data from {self.__dataset_file} loaded '
                  f'in {round(end_time - start_time, 1)} s')

    def __delete_column(self, column_name):
        # Method deleting from DataFrame app list a given column

        self.__apps_list.pop(column_name)

    def filter_key_columns(self, key_columns):
        # Methods deletes from DataFrame object the columns not included in the given set

        if DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager: Filtering columns ')

        for column in self.__apps_list.columns.values:
            if column not in key_columns:
                self.__apps_list.pop(column)

    def __store_app_data(self, data_frame_row):
        # Given a DataFrame row checks if the app has english name
        # and then inserts the id into preliminary table in the database

        if not is_english(data_frame_row['App Name']):
            return

        insert_preliminary_id(data_frame_row['App Id'], from_dataset_flag=True)

    def read_file(self):
        # Reads the file and stores in memory DataFrame object
        start_time = time.time()
        if DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager : Reading dataset file')
        self.__apps_list = pandas.read_csv(self.__dataset_file)
        end_time = time.time()
        if DEBUG:
            print(
                f'{threading.currentThread()}  || Dataset Manager : Reading of \'{self.__dataset_file}\' '
                f'completed in {round(end_time - start_time, 1)} s')

    def shutdown(self):
        # Explicitly delete the reference to DataFrame object in order to free memory

        if DEBUG:
            print(f'{threading.currentThread()}  || Dataset Manager: execution terminated')
        self.__apps_list = None
