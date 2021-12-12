from datetime import datetime
from threading import Thread
from selenium.common.exceptions import WebDriverException
from DataManagers.DatabaseManager import do_query
import time
import numpy as np
from selenium import webdriver

from DataManagers.WordsMiner import sanitize_and_tokenize
from DataModel.Library import Library
from DataModel.Publication import Publication
from Utilities.Classifiers.LogRegClassifier import LogRegClassifier
from Utilities.Classifiers.PaperClassifiers.FrequentistPaperClassifier import PaperClassifier
from Utilities.Classifiers.PaperClassifiers.NBayesPaperClassifier import NBayesPaperClassifier
from Utilities.Scrapers.NatureScraper import NatureScraper
from Utilities.Scrapers.PubMedScraper import PubMedScraper


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
    try:
        f_in = open('./data/input_data/last_analyzed.txt', 'r')
        last_analyzed_index = int(f_in.readlines()[0])
    except FileNotFoundError:
        last_analyzed_index = 0
    start = int(input("Insert the starting value of your interval:\n"))
    if start <= last_analyzed_index:
        start = last_analyzed_index
    end = int(input("Insert the ending value of your interval:\n"))
    end = end + 1
    url = "https://play.google.com/store/apps/details?id="
    end_url = '&hl=en&gl=US'

    query = "SELECT * FROM app_features"
    list_app_features = do_query('', query)

    indexes_range = np.arange(start, end)
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
    # label_apps()
    library = Library()
    # p = NatureScraper(library)
    p = PubMedScraper(library)

    '''string = 'Children with developmental disabilities may need support with motor skills such as balance improvement, cognitive skills such as vocabulary learning, or social skills such as adequate interpretation of emotional expressions. Digital interactive games could support the standard treatments. We aimed to review clinical studies which investigated the application of serious games in children with developmental disabilities.'
    word_list = sanitize_and_tokenize(text=string, max_n_gram=2)
    print(word_list)'''


    '''start = time.time()
    classifier = NBayesPaperClassifier(True)
    end = time.time()

    print(str(end - start))'''

    '''classifier = LogRegClassifier()
    for i in range(10):
        classifier.train_model(final=False)
        # TODO : update
    path = classifier.train_model(final=True)
    classifier.load_model(path)
    classifier.classify_apps()'''

    # ===============================================================
    # DEBUGGING PART
    '''paper_classifier = PaperClassifier()
    query = 'SELECT paper_title, abstract FROM paper LIMIT 1'
    result = do_query('', query)
    paper = Publication(result[0][0], result[0][1], '')
    class_given = paper_classifier.classify_paper(paper)
    print('The paper was classified as ' + class_given + '\n')
    print('===============================================================\n')
    print('TITLE : ' + str(result[0][0]) + '\n')
    print('===============================================================\n')
    print('ABSTRACT : ' + str(result[0][1]) + '\n')
    print('===============================================================\n')'''
