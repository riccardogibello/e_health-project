import google_play_scraper.exceptions
import mysql

from DatabaseManager import do_query, delete_app_from_database
from Application import Application
from concurrent.futures import ThreadPoolExecutor
from settings import MAX_RETRIEVE_APP_DATA_THREADS, SERIOUS_GAMES_CATEGORIES_LIST, DEBUG
import threading


class DataMiner:
    __apps_id_list = None

    def __init__(self):
        if DEBUG:
            print(f'Data Miner started in thread : {threading.currentThread()}')
        self.execution = True
        self.__retrieve_incomplete_data()

    def __retrieve_incomplete_data(self):
        query = (
            "SELECT * FROM app WHERE description IS NULL LIMIT 1000"
        )
        try:
            self.__apps_id_list = do_query((), query)
        except mysql.connector.errors.DatabaseError:
            self.__apps_id_list = None
            return
        if len(self.__apps_id_list) == 0:
            self.execution = False
            print('Data Mining completed')

    def __get_app_data(self, app_id):
        try:
            application = Application(app_id, True)
        except google_play_scraper.exceptions.NotFoundError:
            delete_app_from_database(app_id)
            application = None
        return application

    def fill_database(self):
        with ThreadPoolExecutor(max_workers=MAX_RETRIEVE_APP_DATA_THREADS) as executor:
            while self.execution:
                self.__retrieve_incomplete_data()
                for application in self.__apps_id_list:
                    app_id = application[0]
                    self.__apps_id_list.remove(application)
                    executor.submit(self.load_app_into_database, app_id)
                self.__apps_id_list = []

    def load_app_into_database(self, app_id):
        application = self.__get_app_data(app_id)
        if not application:
            return

        update_query = (
            "UPDATE APP SET description = %s, app_name = %s, category = %s, rating = %s, score = %s, genres = %s WHERE app_id = %s"
        )

        query_values = [application.description,
                        application.title,
                        application.category,
                        application.ratings,
                        application.score,
                        application.genre_id,
                        application.app_id]

        do_query(tuple_data=query_values, query=update_query)
        application = None

    def shutdown(self):
        self.execution = False
