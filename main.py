import time
import web_wining_functions
from dataset_handling_functions import *

if __name__ == '__main__':
    start = time.time()
    databaseHandler = DatabaseHandler()
    databaseHandler.setup_connection_data()

    web_wining_functions.find_available_categories()

    oldDatasetHandler = OldDatasetHandler()
    oldDatasetHandler.load_old_dataset_into_db()
    end = time.time()
    print("The time of execution of above program is :", end - start)
