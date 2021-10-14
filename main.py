import time
import web_wining_functions
from DatasetManager import DatasetManager
from dataset_handling_functions import *
from settings import KAGGLE_DATASET_PATH

if __name__ == '__main__':
    start = time.time()
    databaseHandler = DatabaseHandler()
    databaseHandler.setup_connection_data()

    #datasetManager = DatasetManager(KAGGLE_DATASET_PATH)
    #datasetManager.load_apps_into_db()

    web_wining_functions.find_available_categories()

    oldDatasetHandler = OldDatasetHandler()
    oldDatasetHandler.load_old_dataset_into_db()
    end = time.time()
    print("The time of execution of above program is :", end - start)
