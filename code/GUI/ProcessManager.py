import multiprocessing

from DataManagers.DataMiner import DataMiner
from DataManagers.DatasetManager import DatasetManager
from DataManagers.OldDatasetManager import OldDatasetManager
from Utilities.Classifiers.LogRegClassifier import LogRegClassifier
from Utilities.Classifiers.MNBayesClassifier import MNBayesClassifier
from Utilities.Classifiers.MNBayesAppsClassifier import MNBayesAppsClassifier
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
    #classifier = LogRegClassifier()
    #for i in range(10):
    #    print(f"TRAINING {i}")
    #    classifier.train_model(final=False)
    #    classifier.update_dictionary()
    #path = classifier.train_model(final=True)
    #classifier.load_model(path)
    #classifier.classify_apps()

    #classifier = MNBayesClassifier()
    #classifier.build_model()
    #classifier.classify_apps()

    classifier = MNBayesAppsClassifier()
    classifier.train_models()
    #classifier.classify_apps()



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
        self.__old_dataset_process = multiprocessing.Process(name= 'Dataset Loader', target=execute_old_dataset_manager)
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
