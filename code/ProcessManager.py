import multiprocessing

from DataMiner import DataMiner
from DatasetManager import DatasetManager
from OldDatasetManager import OldDatasetManager
from settings import KAGGLE_DATASET_PATH


def execute_data_miner():
    miner = DataMiner()
    miner.fill_database()


def execute_new_dataset_manager():
    new_dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    new_dataset_manager.load_apps_into_db()


def execute_old_dataset_manager():
    old_dataset_manager = OldDatasetManager()
    old_dataset_manager.load_old_dataset_into_db()


class ProcessManager:
    def __init__(self):
        self.__data_miner_process = None
        self.__dataset_process = None
        self.__old_dataset_process = None

    def launch_data_miner(self):
        if self.__data_miner_process:
            return
        self.__data_miner_process = multiprocessing.Process(target=execute_data_miner)
        self.__data_miner_process.start()

    def launch_old_dataset(self):
        if self.__old_dataset_process:
            return
        self.__old_dataset_process = multiprocessing.Process(target=execute_old_dataset_manager)
        self.__old_dataset_process.start()

    def launch_new_dataset(self):
        if self.__dataset_process:
            return
        self.__dataset_process = multiprocessing.Process(target=execute_new_dataset_manager)
        self.__dataset_process.start()

    def close_application(self):
        if self.__data_miner_process:
            self.__data_miner_process.terminate()
        if self.__dataset_process:
            self.__dataset_process.terminate()
