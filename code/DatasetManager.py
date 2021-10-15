import pandas

from settings import KAGGLE_KEY_COLUMNS, SERIOUS_GAMES_CATEGORIES_LIST, MAX_DATASET_THREADS, DEBUG
from concurrent.futures import ThreadPoolExecutor
from DatabaseManager import do_query


class DatasetManager:
    def __init__(self, dataset_file):
        self.__dataset_file = dataset_file
        self.__apps_list = pandas.read_csv(self.__dataset_file)
        print(f'Dataset Manager for file \'{dataset_file}\' created')

    def __delete_column(self, column_name):
        self.__apps_list.pop(column_name)

    def get_app_list(self):
        return self.__apps_list

    def filter_key_columns(self, key_columns):
        for column in self.__apps_list.columns.values:
            if column not in key_columns:
                self.__apps_list.pop(column)

    def load_apps_into_db(self, filter_categories=SERIOUS_GAMES_CATEGORIES_LIST, filter_columns=True):
        if filter_columns:
            self.filter_key_columns(KAGGLE_KEY_COLUMNS)
        with ThreadPoolExecutor(max_workers=MAX_DATASET_THREADS) as executor:
            for app_index in range(len(self.__apps_list)):
                if self.__apps_list.loc[app_index, 'Category'] in filter_categories:
                    executor.submit(self.store_app_data, app_index)

    def store_app_data(self, app_index):
        print(app_index/len(self.__apps_list)*100)
        data_frame_row = self.__apps_list.loc[app_index]
        values = [data_frame_row['App Name'], data_frame_row['Category'], data_frame_row['App Id']]

        insert_stmt = (
            "INSERT INTO APP(app_name, category, app_id)"
            "VALUES (%s, %s, %s)"
        )

        do_query(values, insert_stmt)

    # conversion of old database to new to be created
