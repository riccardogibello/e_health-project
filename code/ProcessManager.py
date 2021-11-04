import multiprocessing

from DataManagers.DataMiner import DataMiner
from DataManagers.DatabaseManager import clear_table
from DataManagers.DatasetManager import DatasetManager
from DataManagers.OldDatasetManager import OldDatasetManager
from DataManagers.WordsMiner import WordsMiner
from Utilities.FeatureExtractor import FeatureExtractor
from Utilities.LogRegClassifier import LogRegClassifier
from Utilities.MNBayesClassifier import MNBayesClassifier
from WEBFunctions.web_mining_functions import find_available_categories
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


def execute_classification():
    find_available_categories()
    words = ["strong educational potential",
             "educational potential"
             "educational-related needs",
             "educational needs"
             "teaching material",
             "teaching",
             "serious",
             "serious game",
             "serious purpose",
             "serious purpose scenario",
             "real life cases",
             "training",
             "education",
             "learning game",
             "learning",
             "increase awareness",
             "stimulate",
             "train",
             "inform",
             "teach",
             "influence",
             "edugames",
             "edu-games",
             "rules",
             "games for education",
             "educational game",
             "transmit educational knowledge",
             "transmit knowledge",
             "cognitive performance",
             "brain training",
             "educational multiplayer online game",
             "problem solving strategies",
             "problem solving",
             "solving strategies",
             "decision making",
             "decision-making",
             ]
    feature_extractor = FeatureExtractor(words)
    feature_extractor.compute_training_features()

    classifier = LogRegClassifier()
    classifier.train_model()
    feature_extractor.compute_features()
    classifier.classify_apps()


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
