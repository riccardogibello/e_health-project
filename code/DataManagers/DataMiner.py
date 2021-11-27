import http
import http
import threading
import time
import urllib.error
from concurrent.futures import ThreadPoolExecutor

import google_play_scraper.exceptions
import mysql
import regex as re
from bs4 import BeautifulSoup
from mysutils.text import clean_text

import settings
from Application import Application
from DataManagers.DatabaseManager import do_query
from DataManagers.DatabaseManager import insert_app_into_db, insert_id_into_preliminary_db as insert_preliminary, \
    update_status_preliminary, delete_app_from_database, delete_app_from_labeled_app
from DataManagers.DatasetManager import is_english
from WEBFunctions.web_mining_functions import find_web_page
from settings import MAX_RETRIEVE_APP_DATA_THREADS, SERIOUS_GAMES_CATEGORIES_LIST, DEBUG, ADULT_RATINGS


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
        # Creating object Application
        application = Application(app_id, True)
    except google_play_scraper.exceptions.NotFoundError:
        # App not found on Google Play Market meaning it does not exist anymore so it must be deleted from
        # labeled_app because it can not be used for training of ML model and from app table because it is
        # useless to classify it. The id is not deleted from preliminary table in order to keep trace of checked apps
        # and not check more than once in case the app is still given as similar of another one.

        update_status_preliminary(app_id)
        delete_app_from_database(app_id)
        delete_app_from_labeled_app(app_id)

        if DEBUG:
            print(f'{threading.currentThread()}  || Data Miner : APP {app_id} not found')
        # Explicit elimination of Application object
        application = None

    except (urllib.error.HTTPError, urllib.error.URLError, http.client.RemoteDisconnected, ConnectionResetError):
        # Connection errors, probably related to high number of requests to the server.
        # None is returned and a new try to retrieve data will be made later
        application = None


    return application


def clean_description(description):
    # remove all non-ascii characters
    clear_description = str(description.encode('ascii', errors='ignore').decode())
    # remove useless hyphens (multiple hyphens, hyphens at the begging or at the end of a word)
    clear_description = re.sub(r'(--)+', ' ', clear_description)
    clear_description = re.sub(r'( -)+', ' ', clear_description)
    clear_description = re.sub(r'(- )+', ' ', clear_description)
    # clean_text function removes punctuation, removes urls and transform lowers the string
    # because there is no need to distinguish words between lower and upper cases
    return clean_text(clear_description)


class DataMiner:
    __apps_id_list = []
    b = 0

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
        test_query = (
            "SELECT A.app_id, B.from_dataset FROM app as A, preliminary as B WHERE A.app_id = B.app_id AND B.check IS FALSE"
        )
        try:
            self.__apps_id_list = do_query((), query)
            self.__reset_connection_counter()
            if not len(self.__apps_id_list):
                if not start:
                    self.__running = False
                    if DEBUG:
                        print(f'{threading.currentThread()}  || Data Miner : No new app found')

        except mysql.connector.errors.DatabaseError:
            self.__increment_connection_counter()
            if self.__failed_connections < 5:
                if DEBUG:
                    print(f'{threading.currentThread()} || Data Miner : Database communication error - '
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
            if not len(self.__apps_id_list):
                self.__retrieve_incomplete_data()
            if not self.__running:
                return

            with ThreadPoolExecutor(max_workers=MAX_RETRIEVE_APP_DATA_THREADS) as executor:
                for application in self.__apps_id_list:
                    executor.submit(self.load_app_into_database, application[0], application[1])
            self.__apps_id_list = []

    def load_chunk(self, chunk):
        for application in chunk:
            self.load_app_into_database(application[0], application[1])

    def split_list_in_chunks(self, num_chunks=MAX_RETRIEVE_APP_DATA_THREADS):
        chunk_dim = int(len(self.__apps_id_list) / num_chunks) + 1
        chunks = [self.__apps_id_list[x:x + chunk_dim] for x in range(0, len(self.__apps_id_list), chunk_dim)]
        return chunks

    def load_app_into_database(self, app_id, from_dataset):
        application = get_app_data(app_id)
        if not application:
            return
        insert_app, insert_similar = self.check_app(application, from_dataset)

        if insert_app:
            application.description = clean_description(application.description)
            try:
                application.teacher_approved = is_teacher_approved_app(app_id)
            except urllib.error.URLError:
                return

            if len(application.description) > 2:
                insert_app_into_db(application)
        if not insert_app:
            delete_app_from_database(app_id)

        if insert_similar:
            if application.similar_apps:
                for similar_id in application.similar_apps:
                    insert_preliminary(similar_id)
            if application.more_by_developer:
                for developer_app in application.more_by_developer:
                    insert_preliminary(developer_app)

        update_status_preliminary(app_id)

    def shutdown(self):
        self.__running = False

    def check_app(self, app, from_dataset):
        if not app or app.category not in SERIOUS_GAMES_CATEGORIES_LIST:
            return False, False
        if app.score <= 0 and app.min_installs < 500:
            return False, True
        if app.updated < settings.LAST_UPDATE:
            return False, True
        if app.content_rating_description:
            return False, True
        if app.content_rating in ADULT_RATINGS:
            return False, False
        if not (from_dataset or is_english(app.title)):
            return False, False
        if not is_english(app.description):
            return False, False
        return True, True
