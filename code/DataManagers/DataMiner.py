import http
import time
import mysql
import numpy as np
import regex as re
import urllib.error
from bs4 import BeautifulSoup
from mysutils.text import clean_text
import google_play_scraper.exceptions
from DataModel.Application import Application
from concurrent.futures import ThreadPoolExecutor
from DataManagers.DatabaseManager import do_query
from DataManagers.NewDatasetManager import is_english
from WEBFunctions.web_mining_functions import find_web_page
from DataManagers.DatabaseManager import insert_app_into_db, insert_id_into_preliminary_db as insert_preliminary, \
    update_status_preliminary, delete_app_from_database, delete_app_from_labeled_app, insert_developer, \
    mark_as_non_existing
from DataManagers.settings import MAX_RETRIEVE_APP_DATA_THREADS, SERIOUS_GAMES_CATEGORIES_LIST, ADULT_RATINGS, \
    LAST_UPDATE


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
    """
    Getting data from Google Play Store about the application having the given id.
    Uses google_play_scraper module returning a json object containing all data.
    In case the app does not exists anymore it also deletes all data about it if eventually present
    in the database. This is done to prevent from classification being done using outdated applications and also
    from having no more existing apps in the results.
    :param app_id: Application id of the app to search on Google Play.
    :return: Application object. None if the app does not exist or a network error occurred.
    """
    try:
        # Creating object Application
        application = Application(app_id, True)
    except google_play_scraper.exceptions.NotFoundError:
        print(f"{app_id} - NOT FOUND")
        update_status_preliminary(app_id)
        delete_app_from_database(app_id)
        delete_app_from_labeled_app(app_id)
        mark_as_non_existing(app_id)
        # Explicit assignment of None to Application object
        application = None
    except (urllib.error.HTTPError, urllib.error.URLError, http.client.RemoteDisconnected, ConnectionResetError):
        # Connection errors, probably related to high number of requests to the server.
        # None is returned and a new try to retrieve data will be made later
        application = None
    return application


def clean_description(description):
    """
    Before inserting the app in the database all unnecessary tags, links, punctuation has to be removed.
    Non-ASCII characters and not meaningful hyphens are removed. Finally using clean_text method from mysmallutils
    module description are already preprocessed for training and classification purposes.
    :param description: string containing the description of the application.
    :return: string containing the description given in input after being cleaned.
    """
    # remove all non-ascii characters
    clear_description = str(description.encode('ascii', errors='ignore').decode())
    # remove useless hyphens (multiple hyphens, hyphens at the begging or at the end of a word)
    clear_description = re.sub(r'(--)+', ' ', clear_description)
    clear_description = re.sub(r'( -)+', ' ', clear_description)
    clear_description = re.sub(r'(- )+', ' ', clear_description)
    # clean_text function removes punctuation, removes urls and transform lowers the string
    # because for the task there is no need to distinguish between lower and upper cases
    return clean_text(clear_description)


def check_app(app, from_dataset):
    """
    Given the Application object the method checks if the application satisfies all prerequisites for being inserted in
    the database for later processing. The checks are done ordered from the cheapest to most costly in terms of
    performance.
    :param app: Application object containing all data about the application considered
    :param from_dataset: boolean value, when True indicates the app was present in one of datasets (so language check
                         for the name has been already done)
    :return: Couple of boolean values. The first indicates the application can be inserted in the database while the
             second if the similar application of the considered one can be inserted in preliminary table.
    """
    if not app or app.category not in SERIOUS_GAMES_CATEGORIES_LIST:
        return False, False
    if app.score == 0 and app.min_installs < 500:
        return False, True
    if app.updated < LAST_UPDATE:
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


def load_app_into_database(app_list, offset, batch_size, threads):
    for i in np.arange(offset, batch_size):
        app_data = app_list[i]

        app_id = app_data[0]
        from_dataset = app_data[1]
        application = get_app_data(app_id)
        if not application:
            continue
        insert_app, insert_similar = check_app(application, from_dataset)

        if insert_app:
            application.description = clean_description(application.description)
            application.teacher_approved = is_teacher_approved_app(app_id)

            if len(application.description) > 2:
                insert_app_into_db(application)
                if is_english(application.developer):
                    insert_developer(application.developer_id, application.developer)

            else:
                insert_app = False

        if not insert_app:
            delete_app_from_database(app_id)
            delete_app_from_labeled_app(app_id)

        if insert_similar:
            if application.similar_apps:
                for similar_id in application.similar_apps:
                    insert_preliminary(similar_id)
            if application.more_by_developer:
                for developer_app in application.more_by_developer:
                    insert_preliminary(developer_app)

        update_status_preliminary(app_id)
    threads.pop()


class DataMiner:
    __apps_id_list = []

    def __init__(self):
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

        except mysql.connector.errors.DatabaseError:
            self.__increment_connection_counter()
            if self.__failed_connections < 5:
                time.sleep(30)
                return
            elif self.__failed_connections >= 5:
                self.__running = False

    def fill_database(self):
        while self.__running:
            if not len(self.__apps_id_list):
                self.__retrieve_incomplete_data()
            if not self.__running:
                return

            batch_size = int(len(self.__apps_id_list) / MAX_RETRIEVE_APP_DATA_THREADS)
            num_workers = int(len(self.__apps_id_list) // batch_size + 1)
            offset = 0

            threads_status = []
            status = False
            i = 0
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                while offset < len(self.__apps_id_list):
                    threads_status.append(status)
                    executor.submit(load_app_into_database, self.__apps_id_list, offset, batch_size,
                                    threads_status)
                    offset = offset + batch_size
                    print('thread ' + str(i))
                    i = i + 1
                #for app in self.__apps_id_list:
                    #executor.submit(self.load_appz_into_database, app[0], app[1])

            while False in threads_status:
                time.sleep(3)

            self.__apps_id_list = []


