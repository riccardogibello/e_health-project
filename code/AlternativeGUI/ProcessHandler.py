import multiprocessing
import time
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from AlternativeGUI.WindowComponents.WaitingWindow import WaitingWindow
from DataManagers.DataMiner import DataMiner
from DataManagers.DatabaseManager import do_query, clear_table
from DataManagers.NewDatasetManager import DatasetManager
from DataManagers.OldDatasetManager import OldDatasetManager
from Utilities.Classifiers.LogRegClassifier import LogRegClassifier
from DataManagers.settings import KAGGLE_DATASET_PATH


def create_dictionary_load_data_statistics(p_apps):
    occurrence_list = []
    dict_ = {'occurrence': occurrence_list}
    for i in range(len(p_apps)):
        occurrence_list.append(1)

    return pd.DataFrame(dict_)


def execute_new_dataset_manager():
    new_dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    new_dataset_manager.load_apps_into_db()


def execute_old_dataset_manager():
    old_dataset_manager = OldDatasetManager()
    old_dataset_manager.load_old_dataset_into_db()


def execute_classification():
    classifier = LogRegClassifier()
    for i in range(50):
        print(f"TRAINING {i}")
        classifier.train_model(final=False)
        classifier.update_dictionary()
        # TODO : update
    path = classifier.train_model(final=True)
    classifier.load_model(path)
    classifier.classify_apps()


def execute_data_miner():
    miner = DataMiner()

    miner.fill_database()


class ProcessHandler(QObject):
    signal = QtCore.pyqtSignal(object)
    update_signal = QtCore.pyqtSignal(object)
    keep_on_updating = True

    def __init__(self):
        super().__init__()
        self.__data_miner_process = None
        self.__dataset_process = None
        self.__old_dataset_process = None
        self.__classification_process = None
        self.terminated_process = False

    def launch_data_miner(self):
        self.terminated_process = False
        if self.__data_miner_process:
            return
        self.keep_on_updating = True

        self.__data_miner_process = multiprocessing.Process(target=execute_data_miner)
        self.__data_miner_process.start()
        self.__data_miner_process.join()

        if not self.terminated_process:
            self.signal.emit('Idle.')
        self.terminated_process = False

    def update_data_retrieval_page(self, gui_manager, thread):
        window = gui_manager.window
        time.sleep(3)

        while self.keep_on_updating and thread.is_alive():
            time.sleep(3)

            if isinstance(window, WaitingWindow):
                query = 'SELECT `check`, from_dataset FROM preliminary'
                apps_from_dataset = do_query((), query)
                window.apps_from_dataset = apps_from_dataset
                self.update_signal.emit('Idle.')

    def load_datasets(self):
        self.terminated_process = False
        clear_table('preliminary')
        if self.__old_dataset_process or self.__dataset_process:
            return

        self.keep_on_updating = True

        self.__old_dataset_process = multiprocessing.Process(target=execute_old_dataset_manager)
        self.__old_dataset_process.start()
        self.__dataset_process = multiprocessing.Process(target=execute_new_dataset_manager)
        self.__dataset_process.start()
        self.__dataset_process.join()
        self.__old_dataset_process.join()

        self.keep_on_updating = False
        if not self.terminated_process:
            self.signal.emit('Idle.')
        self.terminated_process = False

    def update_load_data_page(self, gui_manager, thread):
        window = gui_manager.window
        time.sleep(3)

        while self.keep_on_updating and thread.is_alive():
            time.sleep(1)

            if isinstance(window, WaitingWindow):
                query = 'SELECT app_id FROM preliminary'
                apps_from_dataset = do_query((), query)
                window.apps_from_dataset = apps_from_dataset
                self.update_signal.emit('Idle.')
        print('end update_load_data_page')

    def do_classification_dataset(self):
        self.terminated_process = False
        if self.__classification_process:
            return
        self.__classification_process = multiprocessing.Process(target=execute_classification)
        self.__classification_process.start()

    def close_application(self):
        self.terminated_process = True
        if self.__data_miner_process:
            self.__data_miner_process.terminate()
        if self.__old_dataset_process:
            self.__old_dataset_process.terminate()
        if self.__dataset_process:
            self.__dataset_process.terminate()
        if self.__classification_process:
            self.__classification_process.terminate()
        print('closed')
