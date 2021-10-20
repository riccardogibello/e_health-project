import web_mining_functions
from DatasetManager import DatasetManager
from OldDatasetManager import *
from DatabaseFilter import DatabaseFilter
from settings import KAGGLE_DATASET_PATH
from DataMiner import DataMiner
from word_mining_functions import *
from threading import Thread
import multiprocessing


def launch_DataMiner():
    miner = DataMiner()
    # miner.shutdown()
    miner.fill_database()


def launch_DatabaseFilter():
    database_filter = DatabaseFilter()
    database_filter.filter_apps_name()


def launch_DatasetManager():
    dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    dataset_manager.load_apps_into_db()


if __name__ == '__main__':
    start = time.time()
    databaseManager = DatabaseManager()
    databaseManager.setup_connection_data()

    #dataset_thread = Thread(target=launch_DatasetManager)
    database_filter_thread = multiprocessing.Process(name='Filter', target=launch_DatabaseFilter)
    data_miner_thread = Thread(name='Miner', target=launch_DataMiner)

    #dataset_thread.start()
    database_filter_thread.start()
    data_miner_thread.start()

    #web_mining_functions.find_available_categories()

    #oldDatasetHandler = OldDatasetManager()
    #oldDatasetHandler.load_old_dataset_into_db()

    end = time.time()
    print("The time of execution of above program is :", end - start)

    #filenames_pages_serious_games = {'wikipage': 'https://en.wikipedia.org/wiki/Serious_game',
                                    # 'paper': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5222787/pdf/fpsyt-07-00215.pdf'}
    #for filename, path in filenames_pages_serious_games.items():
        #find_serious_games_words(filename, path)

    data_miner_thread.join()
    #dataset_thread.join()
    database_filter_thread.join()
