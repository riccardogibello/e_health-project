import web_mining_functions
from DatasetManager import DatasetManager
from FeatureExtractor import FeatureExtractor
from MNBayesClassifier import MNBayesClassifier
from OldDatasetManager import *
from settings import KAGGLE_DATASET_PATH
from DataMiner import DataMiner
from WordsMiner import *
import multiprocessing

word_miner = WordsMiner({'wikipage': 'https://en.wikipedia.org/wiki/Serious_game',
                         'paper_1': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5222787/pdf/fpsyt-07'
                                    '-00215.pdf',
                         'paper_2': 'https://www.hindawi.com/journals/ijcgt/2014/787968/'})


def launch_data_miner():
    miner = DataMiner()
    # miner.shutdown()
    miner.fill_database()


def launch_new_dataset_manager():
    new_dataset_manager = DatasetManager(KAGGLE_DATASET_PATH)
    new_dataset_manager.load_apps_into_db()


def launch_old_dataset_manager():
    old_dataset_manager = OldDatasetManager()
    old_dataset_manager.load_old_dataset_into_db()


def launch_words_miner():
    word_miner.find_serious_games_words()


if __name__ == '__main__':
    start = time.time()
    databaseManager = DatabaseManager()
    databaseManager.setup_connection_data()

    word_miner_thread = multiprocessing.Process(name='Words_Miner', target=launch_words_miner)
    word_miner_thread.start()

    web_mining_functions.find_available_categories()

    old_dataset_thread = multiprocessing.Process(name='Old_Dataset', target=launch_old_dataset_manager)
    old_dataset_thread.start()

    new_dataset_thread = multiprocessing.Process(name='Kaggle_Dataset', target=launch_new_dataset_manager)
    new_dataset_thread.start()

    data_miner_thread = multiprocessing.Process(name='Miner', target=launch_data_miner)
    data_miner_thread.start()

    word_miner_thread.join()
    old_dataset_thread.join()
    new_dataset_thread.join()
    data_miner_thread.join()

    # feature_extractor = FeatureExtractor(word_miner.global_occurrences.keys())
    words = ["strong educational potential", "educational-related needs", "teaching material",
             "serious purpose scenario", "real life cases",
             "training", "education", "learning games", "increase awareness", "stimulate", "train", "inform", "teach",
             "influence",
             "edugames", "rules", "games for education", "transmit educational knowledge", "cognitive performance",
             "brain training",
             "educational multiplayer online game", "problem solving strategies"]
    feature_extractor = FeatureExtractor(words)
    feature_extractor.compute_features()

    classifier = MNBayesClassifier(word_miner)

    end = time.time()
    print("The time of execution of above program is :", end - start)
