import web_mining_functions
from DatasetManager import DatasetManager
from OldDatasetManager import *
from settings import KAGGLE_DATASET_PATH
from word_mining_functions import *

if __name__ == '__main__':
    start = time.time()
    databaseManager = DatabaseManager()
    databaseManager.setup_connection_data()

    datasetManager = DatasetManager(KAGGLE_DATASET_PATH)
    datasetManager.load_apps_into_db()

    web_mining_functions.find_available_categories()

    oldDatasetHandler = OldDatasetManager()
    oldDatasetHandler.load_old_dataset_into_db()
    end = time.time()
    print("The time of execution of above program is :", end - start)

    filenames_pages_serious_games = {'wikipage' : 'https://en.wikipedia.org/wiki/Serious_game',
                                     'paper' : 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5222787/pdf/fpsyt-07-00215.pdf'}
    for filename, path in filenames_pages_serious_games.items():
        find_serious_games_words(filename, path)
