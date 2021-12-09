import multiprocessing
import time
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from AlternativeGUI.WindowComponents.WaitingWindow import WaitingWindow
from DataManagers.DataMiner import DataMiner
from DataManagers.DatabaseManager import do_query
from DataManagers.DatasetManager import DatasetManager
from DataManagers.OldDatasetManager import OldDatasetManager
from Utilities.Classifiers.LogRegClassifier import LogRegClassifier
from DataManagers.settings import KAGGLE_DATASET_PATH
import dataframe_image as dfi


def create_dictionary_data_retrieval_statistics(p_apps):
    values = [0, 0, 0]
    dict_ = {'category': ['currently loaded', 'checked', 'taken from dataset'], 'values': values}
    for app in p_apps:
        check = app[0]
        from_dataset = app[1]
        if check:
            values[1] = values[1] + 1
        if from_dataset:
            values[2] = values[2] + 1
        values[0] = values[0] + 1

    return pd.DataFrame(dict_)


def execute_new_dataset_manager():
    new_dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    new_dataset_manager.load_apps_into_db()


def execute_old_dataset_manager():
    old_dataset_manager = OldDatasetManager()
    old_dataset_manager.load_old_dataset_into_db()


def execute_classification():
    classifier = LogRegClassifier()
    for i in range(10):
        classifier.train_model(final=False)
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

    def launch_data_miner(self):
        if self.__data_miner_process:
            return
        self.keep_on_updating = True

        execute_data_miner()

        self.keep_on_updating = False
        self.signal.emit('Idle.')

    def update_data_retrieval_page(self, gui_manager):
        window = gui_manager.window
        time.sleep(3)

        while self.keep_on_updating:
            time.sleep(1)
            print('updating')
            if isinstance(window, WaitingWindow):
                query = 'SELECT `check`, from_dataset FROM preliminary'
                apps_from_dataset = do_query((), query)

                dataframe = create_dictionary_data_retrieval_statistics(apps_from_dataset)

                dfi.export(dataframe, './data/output_data/retrieval_data_statistics.png')

                self.update_signal.emit('Idle.')

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

    def do_classification_dataset(self):
        if self.__classification_process:
            return
        self.__classification_process = multiprocessing.Process(target=execute_classification)
        self.__classification_process.start()

    def close_application(self):
        if self.__data_miner_process:
            self.__data_miner_process.terminate()
        if self.__dataset_process:
            self.__dataset_process.terminate()
