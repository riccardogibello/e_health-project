import random
import pandas as pd
import dataframe_image as dfi
from pandas import DataFrame

from DataManagers.DatabaseManager import do_query as query, clear_table
from Utilities.Classifiers.MNBayesModel import MNBayesClassifierModel, calculate_app_distribution_from_labels
from DataManagers.settings import NUM_MODELS, TEST_SET_DIMENSION, SOFT_VOTING, SMOOTHING_COEFFICIENT, \
    NON_IMPROVING_ITERATIONS, WRONG_CLASSIFIED_INCREMENT, TRUE_CLASSIFIED_INCREMENT, MAX_ITERATIONS
from DataModel.PerformanceMetrics import PerformanceMetrics
from sklearn.metrics import confusion_matrix, accuracy_score as accuracy, f1_score as f1, recall_score as recall, \
    precision_score as precision, matthews_corrcoef as mcc
from Utilities.ConfusionMatrixPrinter import save_confusion_matrix


def get_training():
    """
    This method extracts from database the information about applications contained in the training set.
    This will be used for training the model and then for classification of all applications.
    :return: two lists of tuples containing the description of the app and how the app has been manually classified
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


def voting(results):
    """
    Method used for voting process in order to decide if an application is serious or not.
    :param results: list of results from the classification models.
    :return: boolean value: True if the application is a serious game.
    """
    if SOFT_VOTING:
        serious_probability = non_serious_probability = 0
        for result in results:
            serious_probability += result['serious']
            non_serious_probability += result['non-serious']
        return serious_probability > non_serious_probability
    else:
        results = [result['serious'] > result['non-serious'] for result in results]
        return results.count(True) > results.count(False)


def get_apps_descriptions():
    """
    Extracts from the database the description of all apps to classify and organizes them in
    a dictionary with the application id as Key.
    :return: a dictionary containing applications data.
    """
    result_tuples = query(None, "SELECT app.app_id, description FROM app")
    apps = {}
    for application_tuple in result_tuples:
        apps[application_tuple[0]] = application_tuple[1]
    return apps


class ApplicationsClassifier:
    def __init__(self):
        #  sets containing application data used for training
        self.training_serious, self.training_non_serious = get_training()
        #  performance of the classifier, by default 0 for all metrics.
        self.performance = PerformanceMetrics()
        #  testing set for computation of the performances. Casually picked up from all labeled apps
        self.testing_set = None
        self.select_apps_for_testing()
        #  list containing all models used for classification process
        self.model_list = []
        #  Setting are saved for later checking. If at the beginning of classification the models setting do not
        #  match with the settings file then the model is not valid and a new one will be trained.
        self.__settings = {'SMOOTHING_COEFFICIENT': SMOOTHING_COEFFICIENT,
                           'TEST_SET_DIMENSION': TEST_SET_DIMENSION,
                           'NUM_MODELS': NUM_MODELS,
                           'NON_IMPROVING_ITERATIONS': NON_IMPROVING_ITERATIONS,
                           'MAX_ITERATIONS': MAX_ITERATIONS,
                           'TRUE_CLASSIFIED_INCREMENT': TRUE_CLASSIFIED_INCREMENT,
                           'WRONG_CLASSIFIED_INCREMENT': WRONG_CLASSIFIED_INCREMENT,
                           'SOFT_VOTING': SOFT_VOTING}

        self.create_models()

    def select_apps_for_testing(self):
        """
        Given all labeled applications, already divided in serious and non serious, a random set of apps is picked up
        and used as test set. The number of testing apps in relation to all labeled apps is specified in settings file.
        """
        testing_serious = random.sample(self.training_serious, int(len(self.training_serious) * TEST_SET_DIMENSION))
        testing_non_serious = random.sample(self.training_non_serious, int(len(self.training_non_serious) *
                                                                           TEST_SET_DIMENSION))

        new_training_serious = [app for app in self.training_serious if (app not in testing_serious)]
        new_training_non_serious = [app for app in self.training_non_serious if (app not in testing_non_serious)]
        self.training_serious = new_training_serious
        self.training_non_serious = new_training_non_serious
        self.testing_set = testing_serious + testing_non_serious

    def create_single_model(self, assigned_id):
        """
        Method creating a single model and adding it to models list of the classifier.
        :param assigned_id: integer used to identify the model.
        """
        model = MNBayesClassifierModel(assigned_id, self.create_subset())
        self.model_list.append(model)

    def create_subset(self):
        """
        Creates the set of applications to be used as training set for an instance of classifier.
        :return: a set of applications.
        """
        #  serious set is also shuffled is done to guarantee more randomized choosing of validation set for each model
        random.shuffle(self.training_serious)
        subset = self.training_serious.copy()
        random.shuffle(self.training_non_serious)
        subset += self.training_non_serious.copy()

        return subset

    def create_models(self):
        """
        Creates the instances of classifier to be used for ensemble voting during classification phase.
        """
        for i in range(NUM_MODELS):
            self.create_single_model(i + 1)

    def train_models(self):
        """
        Coordinates the process of training of the models.
        """
        for model in self.model_list:
            model.train_model()

    def classify_apps(self):
        """
        Classifies all the apps from "app" table in the database.
        If a game is classified as serious it will be inserted in "selected_app" table.
        """
        description_dict = get_apps_descriptions()
        clear_table('selected_app')
        for app in description_dict:
            if self.is_serious_game(description_dict[app]):
                query((app,), "INSERT INTO selected_app SELECT * FROM app WHERE %s = app.app_id")

    def is_serious_game(self, app_description):
        """
        Method checking if an application is a serious game or not.
        :param app_description: the description of the game to classify.
        :return: results of the voting.
        """
        results = [self.model_list[i].classify_app(app_description) for i in range(len(self.model_list))]
        return voting(results)

    def evaluate_classifier(self):
        """
        Method evaluating the performances of the model on the validation set, saves them and
        finally exports the confusion matrix and metrics as png files.
        """
        classified_serious = [app for app in self.testing_set if self.is_serious_game(app[0])]

        y_true = []
        y_pred = []
        for app in self.testing_set:
            y_true.append(app[1])
            y_pred.append(app in classified_serious)

        tp, tn, fp, fn = calculate_app_distribution_from_labels(y_true, y_pred)

        self.performance = PerformanceMetrics(accuracy=accuracy(y_true, y_pred), recall=recall(y_true, y_pred),
                                              precision=precision(y_true, y_pred), f1=f1(y_true, y_pred),
                                              matthews_cc=mcc(y_true, y_pred), tp=tp, tn=tn, fp=fp, fn=fn)

        metrics = {'accuracy': self.performance.accuracy, 'recall': self.performance.recall,
                   'precision': self.performance.precision, 'f1 score': self.performance.f1}

        dataframe = DataFrame(metrics, index=['metrics'])
        dataframe = dataframe.style.set_properties(**{'background-color': 'black',
                                                      'color': 'green'})
        dfi.export(dataframe, 'data/output_data/model_metrics.png')

        y_true = ['serious' if label else 'non-serious' for label in y_true]
        y_pred = ['serious' if label else 'non-serious' for label in y_pred]

        cm = confusion_matrix(y_true=y_true, y_pred=y_pred, labels=['serious', 'non-serious'])
        cm_df = pd.DataFrame(cm, index=['serious', 'non-serious'], columns=['serious', 'non-serious'])
        save_confusion_matrix(fig_width=8, fig_height=6, heatmap_width=5, heatmap_height=3,
                              confusion_matrix_dataframe=cm_df, path='data/output_data/model_cf.png')

    def check_validity(self):
        """
        Checks the validity of the model. Used when the model is loaded from file and throws an exception if
        any of the parameters has changed meaning the model is no more usable. Process Manager will catch the exception
        and train a new model.
        """

        if self.__settings['SMOOTHING_COEFFICIENT'] != SMOOTHING_COEFFICIENT:
            raise ValueError("Invalid Model: SMOOTHING_COEFFICIENT modified")
        if self.__settings['TEST_SET_DIMENSION'] != TEST_SET_DIMENSION:
            raise ValueError("Invalid Model:  TEST_SET_DIMENSION modified")
        if self.__settings['NUM_MODELS'] != NUM_MODELS:
            raise ValueError("Invalid Model: NUM_MODELS modified")
        if self.__settings['NON_IMPROVING_ITERATIONS'] != NON_IMPROVING_ITERATIONS:
            raise ValueError("Invalid Model: NON_IMPROVING_ITERATIONS modified")
        if self.__settings['MAX_ITERATIONS'] != MAX_ITERATIONS:
            raise ValueError("Invalid Model: MAX_ITERATIONS modified")
        if self.__settings['TRUE_CLASSIFIED_INCREMENT'] != TRUE_CLASSIFIED_INCREMENT:
            raise ValueError("Invalid Model: TRUE_CLASSIFIED_INCREMENT modified")
        if self.__settings['WRONG_CLASSIFIED_INCREMENT'] != WRONG_CLASSIFIED_INCREMENT:
            raise ValueError("Invalid Model: WRONG_CLASSIFIED_INCREMENT modified")
        if self.__settings['SOFT_VOTING'] != SOFT_VOTING:
            raise ValueError("Invalid Model: SOFT_VOTING modified")

        #  Once here means settings match so last check is done on the applications in th
        serious_training, non_serious_training = get_training()
        training_apps = [app[2] for app in serious_training + non_serious_training]
        model_training_apps = [app[2] for app in self.training_serious + self.training_non_serious + self.testing_set]
        apps_union = set(training_apps).union(set(model_training_apps))

        if len(training_apps) != len(model_training_apps):
            raise ValueError("Invalid Model: training set changed!")
        if apps_union != set(training_apps):
            raise ValueError("Invalid Model: training set changed")
