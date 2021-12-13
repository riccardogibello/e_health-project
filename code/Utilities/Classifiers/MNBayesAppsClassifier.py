import math
import random

from DataManagers.DatabaseManager import do_query as query, clear_table
from Utilities.Classifiers.MNBayesModel import MNBayesClassifierModel
from DataManagers.settings import NUM_MODELS, DEBUG

def get_training():
    """
    This method extracts from database information about applications contained in the training set.
    These will be used for training the model and then for classification of all applications.
    :return: list of tuples containing the description of the app and how the app is classified
    """
    serious = query(None,
                    "SELECT A.description, LA.human_classified, A.app_id "
                    "FROM app as A, labeled_app as LA "
                    "WHERE A.app_id = LA.app_id AND LA.human_classified IS TRUE")
    non_serious = query(None,
                        "SELECT A.description, LA.human_classified, A.app_id "
                        "FROM app as A, labeled_app as LA "
                        "WHERE A.app_id = LA.app_id AND LA.human_classified IS FALSE")
    return serious, non_serious

def get_apps_descriptions():
    result_tuples = query(None, "SELECT app.app_id, description FROM app")
    apps = {}
    for tuple in result_tuples:
        apps[tuple[0]] = tuple[1]
    return apps


class MNBayesAppsClassifier:
    def __init__(self):
        self.training_serious, self.training_non_serious = get_training()
        self.model_list = []
        self.create_models()

    def create_single_model(self):
        training_subset = self.create_balanced_subset()
        model = MNBayesClassifierModel(training_subset)
        self.model_list.append(model)

    def create_balanced_subset(self):
        subset = self.training_serious.copy()
        random.shuffle(self.training_non_serious)
        subset += random.sample(self.training_non_serious, len(self.training_serious))
        #subset += self.training_non_serious
        return subset

    def create_models(self):
        for i in range(NUM_MODELS):
            self.create_single_model()

    def train_models(self):
        for model in self.model_list:
            model.train_model()

    def classify_apps(self):
        if DEBUG:
            print("NAIVE BAYES CLASSIFIER: Classification started")

        description_dict = get_apps_descriptions()
        clear_table('selected_app')

        for app in description_dict:
            results = [self.model_list[i].classify_app(app) for i in range(len(self.model_list))]
            if results.count(True) > results.count(False):
                query((app,), "INSERT INTO selected_app SELECT * FROM app WHERE %s = app.app_id")








