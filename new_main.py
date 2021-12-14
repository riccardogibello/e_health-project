import sys
from multiprocessing.pool import ThreadPool
from PyQt5.QtWidgets import QApplication
from AlternativeGUI.GUIManager import GUIManager
from AlternativeGUI.ProcessHandler import ProcessHandler
from DataManagers.OldDatasetManager import *
from DataManagers.DataMiner import DataMiner


def launch_data_miner():
    miner = DataMiner()
    miner.fill_database()


def launch_new_dataset_manager():
    pass
    # new_dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    # new_dataset_manager.load_apps_into_db()


def launch_old_dataset_manager():
    old_dataset_manager = OldDatasetManager()
    old_dataset_manager.load_old_dataset_into_db()


def launch_words_miner():
    pass
    # word_miner.find_serious_games_words()


def create_process_manager_thread():
    return ProcessHandler()


if __name__ == '__main__':
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(create_process_manager_thread)
    proc_man = async_result.get()

    app = QApplication(sys.argv)
    gui_manager = GUIManager(process_manager=proc_man)

    app.exec()

    proc_man.close_application()
