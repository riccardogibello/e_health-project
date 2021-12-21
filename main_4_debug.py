from threading import Thread
from selenium.common.exceptions import WebDriverException
from DataManagers.DatabaseManager import do_query
import time
import numpy as np
from selenium import webdriver
from DataModel.Library import Library
from Utilities.Classifiers.PaperClassifiers.NBayesPaperClassifier import NBayesPaperClassifier
from Utilities.Scrapers.NatureScraper import NatureScraper


def browse(url_to_open, how_long):
    driver = webdriver.Chrome()
    # Fetching the Url
    driver.start_client()
    driver.get(url_to_open)
    try:
        driver.maximize_window()
        time.sleep(how_long)
        driver.close()
    except WebDriverException:
        pass


def label_apps():
    """
    This was the first attempt to try to perform in a practical way the tedious task of labeling the applications.
    """
    try:
        f_in = open('./data/input_data/last_analyzed.txt', 'r')
        last_analyzed_index = int(f_in.readlines()[0])
    except FileNotFoundError:
        last_analyzed_index = 0
    start_ = int(input("Insert the starting value of your interval:\n"))
    if start_ <= last_analyzed_index:
        start_ = last_analyzed_index
    end_ = int(input("Insert the ending value of your interval:\n"))
    end_ = end_ + 1
    url = "https://play.google.com/store/apps/details?id="
    end_url = '&hl=en&gl=US'

    query = "SELECT * FROM app_features"
    list_app_features = do_query('', query)

    indexes_range = np.arange(start_, end_)
    for i in indexes_range:
        app_features = list_app_features[i]

        # Open url in a new page (“tab”) of the default browser, if possible
        thread = Thread(target=browse, args=[url + str(app_features[0] + end_url), 75])
        thread.start()

        print(' =========================== FEATURES OF ' + str(app_features[0]) + ' ===========================\n')
        print('     - serious words count : ' + str(app_features[1]) + '\n')
        print('     - teacher approved : ' + str(app_features[2]) + '\n')
        print('     - score : ' + str(app_features[3]) + '\n')
        print('     - rating : ' + str(app_features[4]) + '\n')
        is_serious = input('Is this a serious game? [0 = no / 1 = yes / "quit" = terminate program\n')

        if str(is_serious) == 'quit':
            f_out = open('./data/input_data/last_analyzed.txt', 'w')
            f_out.write(str(i))
            exit()
        if int(is_serious) == 0:
            query = "INSERT INTO labeled_app(app_id, human_classified)  VALUES (%s, %s)"
            do_query([str(app_features[0]), False], query)
        if int(is_serious) == 1:
            query = "INSERT INTO labeled_app(app_id, human_classified)  VALUES (%s, %s)"
            do_query([str(app_features[0]), True], query)

        last_analyzed_index = last_analyzed_index + 1


if __name__ == '__main__':
    '''library = Library()
    p = NatureScraper(library)

    start = time.time()
    classifier = NBayesPaperClassifier(False)
    end = time.time()

    print(str(end - start))'''
