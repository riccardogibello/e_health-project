import langid
import pandas
import threading
from DataManagers import DatabaseManager
from DataManagers.settings import SERIOUS_GAMES_CATEGORIES_LIST
from DataManagers.DatabaseManager import insert_id_into_preliminary_db as insert_preliminary_id


def is_english(string):
    """
    Using langid package the method checks the language of the given text
    :param string: string.
    :return: True if the string is english, False if is any other language.
    """
    # Using langid package checks language of input string
    # Returns True if the string is english, False otherwise
    return langid.classify(string)[0] == 'en'


class DatasetManager:
    def __init__(self, dataset_file):
        #  setting the name of thread the manager executes in.
        threading.currentThread().name = 'Dataset Manager'

        # Constructor reads the file and stores in memory a DataFrame
        # object (from pandas package) containing the list of the applications
        self.__dataset_file = dataset_file
        self.__apps_list = None

        self.__in_database_apps = [app for tuples in DatabaseManager.get_apps_from_preliminary() for app in tuples]
        self.__in_database_apps.sort()
        self.__dataset_file = dataset_file
        self.read_file()

    def load_apps_into_db(self, filter_categories=SERIOUS_GAMES_CATEGORIES_LIST):
        """
        Method used to coordinate the loading into preliminary table from database of application
        ids taken from the dataset.
        :param filter_categories: list of categories to be inserted in the database, discarding the others.
        """
        for app_index in range(len(self.__apps_list)):
            app_id = self.__apps_list.loc[app_index, 'App Id']
            if self.__apps_list.loc[app_index, 'Category'] in filter_categories and not self.is_in_database(app_id):
                self.__store_app_data(app_id, self.__apps_list.loc[app_index, 'App Name'])

    def is_in_database(self, app_id):
        """
        Method checking if a given application id is already in the database.
        This is done considering the possibility to load data from different sources and prevents from making
        duplicates insertion queries to database.
        :param app_id: the application id to check.
        :return: True if application id is already present in database, False if not.
        """
        if app_id in self.__in_database_apps:
            self.__in_database_apps.remove(app_id)
            return True
        return False

    def __delete_column(self, column_name):
        """
        Method used to delete a column from Dataframe structure.
        :param column_name: name of the column to remove.
        """
        self.__apps_list.pop(column_name)

    def filter_key_columns(self, key_columns):
        """
        Deletes all unnecessary columns in the Dataframe.
        :param key_columns: list of names of columns to keep.
        """
        for column in self.__apps_list.columns.values:
            if column not in key_columns:
                self.__delete_column(column)

    @staticmethod
    def __store_app_data(app_id, app_name):
        """
        Method inserting in the database the name and the id of an application after checking it to be english.
        :param app_id: Id of the app to insert.
        :param app_name: Name of the app to insert.
        """
        if is_english(app_name):
            insert_preliminary_id(app_id, from_dataset_flag=True)

    def read_file(self):
        """
        Method for reading the dataset file and store data in Dataframe structure
        """
        self.__apps_list = pandas.read_csv(self.__dataset_file)
