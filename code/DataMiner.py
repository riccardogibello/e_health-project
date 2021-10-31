import time
import google_play_scraper.exceptions
import mysql
from bs4 import BeautifulSoup

import settings
from DatabaseManager import insert_app_into_db, insert_id_into_preliminary_db as insert_preliminary, \
    update_status_preliminary, delete_id_from_preliminary_db
from DatasetManager import is_english
from DatabaseManager import do_query
from Application import Application
from concurrent.futures import ThreadPoolExecutor
from settings import MAX_RETRIEVE_APP_DATA_THREADS, SERIOUS_GAMES_CATEGORIES_LIST, DEBUG, MAX_CONNECTION_ATTEMPTS
import threading
from web_mining_functions import find_web_page


def is_teacher_approved_app(app_id):
    """
    This method checks if a specific app is tagged on the play store as 'teacher approved'
    by requesting directly the HTML page to the play store web application. The check
    is done by querying on the HTML page an element with class 'T75of LgkPtd'. If present
    it means that the application is approved by teachers and doctors.
    """
    path = 'https://play.google.com/store/apps/details?id='
    page = find_web_page(path + app_id + '&hl=en&gl=US')
    soup = BeautifulSoup(page, 'html.parser')
    approved_tag = soup.find("img", class_="T75of LgkPtd")
    return str(approved_tag).find('Approved by teachers for:') > 0


def get_app_data(app_id):
    try:
        application = Application(app_id, True)
    except google_play_scraper.exceptions.NotFoundError:
        delete_id_from_preliminary_db(app_id)
        application = None
        if DEBUG:
            print(f'{threading.currentThread()}  || Data Miner : APP {app_id} not found')

    return application


class DataMiner:
    __apps_id_list = []

    def __init__(self):
        threading.currentThread().name = 'Data Miner'
        if DEBUG:
            print(f'{threading.currentThread()}  || Data Miner : Started')
        self.__running = True
        start_attempts = 0
        self.__failed_connections = 0
        self.__retrieve_incomplete_data(True)
        while (not len(self.__apps_id_list)) and start_attempts < 5:
            start_attempts += 1
            time.sleep(30)
            self.__retrieve_incomplete_data()

    def __reset_connection_counter(self):
        self.__failed_connections = 0

    def __increment_connection_counter(self):
        self.__failed_connections += 1

    def __retrieve_incomplete_data(self, start=False):
        # Looks in the preliminary table for checked apps has not been checked yet
        # and save their IDs in self.__apps_id_list
        query = (
            "SELECT app_id, from_dataset FROM preliminary WHERE preliminary.`check` IS FALSE"
        )
        try:
            self.__apps_id_list = do_query((), query)
            self.__reset_connection_counter()
            if not len(self.__apps_id_list):
                if not start:
                    self.__running = False
                    if DEBUG:
                        print(f'{threading.currentThread()}  || Data Miner : No new app found - Execution terminated')

        except mysql.connector.errors.DatabaseError:
            self.__increment_connection_counter()
            if self.__failed_connections < 5:
                if DEBUG:
                    print(f'{threading.currentThread()} || Data Miner : Database communication error!! - '
                          f'Retry in 30 seconds')
                time.sleep(30)
                return
            elif self.__failed_connections >= 5:
                self.__running = False
                if DEBUG:
                    print(f'{threading.currentThread()} || Data Miner : Database communication error!!\n'
                          f'TOO MANY ATTEMPTS FAILED - Execution terminated')

    def fill_database(self):
        while self.__running:
            self.__retrieve_incomplete_data()
            if not self.__running:
                return

            with ThreadPoolExecutor(max_workers=MAX_RETRIEVE_APP_DATA_THREADS) as executor:
                for application in self.__apps_id_list:
                    self.__apps_id_list.remove(application)
                    executor.submit(self.load_app_into_database, application[0], application[1])
            self.__apps_id_list = []

    def load_app_into_database(self, app_id, from_dataset):
        application = get_app_data(app_id)

        if self.insertable_in_db(application, from_dataset):

            application.teacher_approved = is_teacher_approved_app(app_id)
            insert_app_into_db(application)

            for similar_id in application.similar_apps:
                insert_preliminary(similar_id)
            for developer_app in application.more_by_developer:
                insert_preliminary(developer_app)

        update_status_preliminary(app_id)

    def shutdown(self):
        self.__running = False

    def insertable_in_db(self, app, from_dataset):
        if not app or app.category not in SERIOUS_GAMES_CATEGORIES_LIST:
            return False
        if app.updated <= settings.LAST_UPDATE:
            return False
        if not (from_dataset or is_english(app.title)):
            return False
        if not is_english(app.description):
            return False
        return True
