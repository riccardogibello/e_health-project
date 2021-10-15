import web_wining_functions
from DatasetManager import DatasetManager
from OldDatasetManager import *
from settings import KAGGLE_DATASET_PATH

if __name__ == '__main__':
    start = time.time()
    databaseManager = DatabaseManager()
    databaseManager.setup_connection_data()

    datasetManager = DatasetManager(KAGGLE_DATASET_PATH)
    datasetManager.load_apps_into_db()

    web_wining_functions.find_available_categories()

    oldDatasetHandler = OldDatasetManager()
    oldDatasetHandler.load_old_dataset_into_db()
    end = time.time()
    print("The time of execution of above program is :", end - start)
