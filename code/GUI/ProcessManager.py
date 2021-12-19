from datetime import datetime
import multiprocessing
import os.path
import pickle

from DataManagers.DataMiner import DataMiner
from DataManagers.DatasetManager import DatasetManager
from DataManagers.OldDatasetManager import OldDatasetManager
from Utilities.Classifiers.ApplicationsClassifier import ApplicationsClassifier
from DataManagers.settings import KAGGLE_DATASET_PATH


def execute_data_miner():
    miner = DataMiner()
    miner.fill_database()


def execute_new_dataset_manager():
    new_dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    new_dataset_manager.load_apps_into_db()


def execute_old_dataset_manager():
    old_dataset_manager = OldDatasetManager()
    old_dataset_manager.load_old_dataset_into_db()


def execute_classification():
    try:
        model_file = open('./data/models/ApplicationClassifier/Model.pckl', 'rb')
        classifier = pickle.load(model_file)
        model_file.close()
        classifier.check_validity()
    except (FileNotFoundError, ValueError) as e:
        #  FileNotFoundError - there is no saved model
        #  ValueError raised by check_validity method when the model is not valid
        classifier = ApplicationsClassifier()
        classifier.train_models()
        classifier.evaluate_classifier()
        save_model(classifier)
    classifier.classify_apps()


def save_model(model):
    model_dir = './data/models/ApplicationClassifier'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_file_path = './data/models/ApplicationClassifier/Model.pckl'
    if os.path.exists(model_file_path):
        os.remove(model_file_path)
    file_out = open(model_file_path, 'wb')
    pickle.dump(model, file_out)
    file_out.close()


class ProcessManager:
    def __init__(self):
        self.__data_miner_process = None
        self.__dataset_process = None
        self.__old_dataset_process = None
        self.__classification_process = None

    def launch_data_miner(self):
        if self.__data_miner_process:
            return
        self.__data_miner_process = multiprocessing.Process(target=execute_data_miner)
        self.__data_miner_process.start()

    def launch_old_dataset(self):
        if self.__old_dataset_process:
            return
        self.__old_dataset_process = multiprocessing.Process(name='Dataset Loader', target=execute_old_dataset_manager)
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
