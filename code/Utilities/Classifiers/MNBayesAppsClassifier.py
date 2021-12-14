import math
import random

from DataManagers.DatabaseManager import do_query as query, clear_table
from Utilities.Classifiers.MNBayesModel import MNBayesClassifierModel
from DataManagers.settings import NUM_MODELS, DEBUG, TEST_SET_DIMENSION
from DataModel.PerformanceMetrics import PerformanceMetrics
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score


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
        self.__performance = PerformanceMetrics(0, 0, 0, 0)
        self.testing_set = None
        self.select_apps_for_testing()
        self.model_list = []
        self.create_models()

    def select_apps_for_testing(self):
        testing_serious = random.sample(self.training_serious, int(len(self.training_serious) * TEST_SET_DIMENSION))
        testing_non_serious = random.sample(self.training_non_serious, int(len(self.training_non_serious) *
                                                                           TEST_SET_DIMENSION))

        new_training_serious = [app for app in self.training_serious if (app not in testing_serious)]
        new_training_non_serious = [app for app in self.training_non_serious if (app not in testing_non_serious)]
        self.training_serious = new_training_serious
        self.training_non_serious = new_training_non_serious
        self.testing_set = testing_serious + testing_non_serious

    def create_single_model(self, assigned_id):
        training_subset = self.create_balanced_subset()
        model = MNBayesClassifierModel(assigned_id, training_subset)
        self.model_list.append(model)

    def create_balanced_subset(self):
        subset = self.training_serious.copy()
        random.shuffle(self.training_non_serious)
        subset += random.sample(self.training_non_serious, len(self.training_serious))
        return subset

    def create_models(self):
        clear_table('classification_performance')
        for i in range(NUM_MODELS):
            self.create_single_model(i + 1)

    def train_models(self):
        for model in self.model_list:
            model.train_model()

    def classify_apps(self):
        if DEBUG:
            print("NAIVE BAYES CLASSIFIER: Classification started")

        description_dict = get_apps_descriptions()
        clear_table('selected_app')

        #for app in description_dict:
        #    results = [self.model_list[i].classify_app(description_dict[app]) for i in range(len(self.model_list))]
        #    if results.count(True) > results.count(False):
        #        query((app,), "INSERT INTO selected_app SELECT * FROM app WHERE %s = app.app_id")
        for app in description_dict:
            if self.is_serious_game(description_dict[app]):
                query((app,), "INSERT INTO selected_app SELECT * FROM app WHERE %s = app.app_id")

    def is_serious_game(self, app_description):
        results = [self.model_list[i].classify_app(app_description) for i in range(len(self.model_list))]
        return results.count(True) > results.count(False)

    def evaluate_classifier(self):
        classified_serious = [app for app in self.testing_set if self.is_serious_game(app[0])]
        classified_non_serious = [app for app in self.testing_set if app not in classified_serious]

        tp = [app for app in classified_serious if app[1]]
        tn = [app for app in classified_non_serious if not app[1]]
        fp = [app for app in classified_serious if not app[1]]
        fn = [app for app in classified_non_serious if app[1]]

        y_true = []
        y_pred = []
        for app in self.testing_set:
            y_true.append(app[1])
            y_pred.append(app in classified_serious)

        self.__performance = PerformanceMetrics(accuracy=accuracy_score(y_true, y_pred),
                                                recall=recall_score(y_true, y_pred),
                                                precision=precision_score(y_true, y_pred),
                                                f1=f1_score(y_true, y_pred))

        query((0, 1, self.__performance.recall, self.__performance.accuracy,
               self.__performance.precision, self.__performance.f1, len(tp), len(tn), len(fp), len(fn)),
              "INSERT INTO classification_performance(model_id, iteration, recall, accuracy, `precision`, "
              "f1_score, true_positive, true_negative, false_positive, false_negative) "
              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
