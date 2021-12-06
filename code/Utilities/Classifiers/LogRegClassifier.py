import os
import pickle
import random
from datetime import datetime

import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.stats import zscore
from sklearn.model_selection import train_test_split
from DataManagers.DatabaseManager import clear_table
from DataManagers.DatabaseManager import do_query
from sklearn.utils import shuffle
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, recall_score, precision_score
from DataManagers.settings import SERIOUS_WORDS
from DataModel.PerformanceMetrics import PerformanceMetrics
from DataModel.Results import Results
from Utilities.Classifiers.FeatureExtractor import FeatureExtractor
from Utilities.ConfusionMatrixPrinter import save_confusion_matrix
from WEBFunctions.web_mining_functions import find_available_categories


def retrieve_app_features():
    query = "SELECT * FROM app_features"
    return do_query('', query)


def retrieve_app_features_with_labels():
    query = "SELECT af.app_id, af.serious_words_count, af.teacher_approved, af.score, af.rating, af.category_id, " \
            "la.human_classified FROM app_features AS af, labeled_app AS la WHERE af.app_id = la.app_id "
    return do_query('', query)


def retrieve_columns_names():
    query = "SELECT COLUMNS.COLUMN_NAME FROM information_schema.COLUMNS WHERE table_schema='projectdatabase' " \
            "and TABLE_NAME='app_features' ORDER BY ORDINAL_POSITION"
    result = do_query('', query)
    col_names = []
    for el in result:
        name = str(el[0])
        col_names.append(name)
    return col_names


def transform_labels(int_values):
    labels = []
    for value in int_values:
        if value == 0:
            labels.append('Non-Serious Game')
        if value == 1:
            labels.append('Serious Game')
    return labels


def set_environment(is_train):
    # Firstly, find all the available categories and fill the 'category' table
    find_available_categories()
    words = SERIOUS_WORDS  # this is a hand-crafted vocabulary of serious-games related words

    # Then find all the features of the training applications (the ones manually labeled)
    feature_extractor = FeatureExtractor(words)
    if is_train:
        feature_extractor.compute_training_features()
    else:
        feature_extractor.compute_features()


def select_x_t_ids_arrays(feature_dataframe):
    # The following selects only the features used in order to build the model
    x = zscore(feature_dataframe[['serious_words_count', 'teacher_approved', 'score_rating', 'category_id']].
               values)
    t = feature_dataframe['human_classified'].values == 1  # target array, in which there is True if
    # 'human_classified' == 1
    ids = feature_dataframe['app_id'].values  # this is done in order to preserve the correspondence
    # between results and correspondent apps

    x, t, ids = shuffle(x, t, ids, random_state=0)

    return x, t, ids


def extract_dataframe():
    dataset = retrieve_app_features_with_labels()  # this returns a list of training applications with the
    # related features
    columns_names = retrieve_columns_names()
    columns_names.append('human_classified')
    columns_names.remove('machine_classified')
    feature_dataset = DataFrame(columns=columns_names, data=dataset)

    feature_dataset['score_rating'] = feature_dataset['score'] * feature_dataset['rating']
    return feature_dataset


class LogRegClassifier:
    def __init__(self):
        self.x = []
        self.t = []
        self.ids = []
        self.trained_models_list = []
        self.performance_metrics_list = []
        self.results = []
        self.final_model = LogisticRegression(penalty='l2')

    def find_number_and_indexes_serious_games(self):
        n_serious_games = 0
        index = 0
        serious_games_indexes = []
        for target in self.t:
            if target:
                n_serious_games = n_serious_games + 1
                serious_games_indexes.append(index)
            index = index + 1

        return n_serious_games, serious_games_indexes

    def extract_serious_games_data(self, serious_games_indexes):
        x_serious = []
        t_serious = []
        ids_serious = []
        for index in serious_games_indexes:
            x_serious.append(self.x[index])
            t_serious.append(self.t[index])
            ids_serious.append(self.ids[index])
        return x_serious, t_serious, ids_serious

    def remove_from_x_t_ids_serious_games(self, serious_games_indexes):
        # now the serious games applications are removed from x, t, ids, in order to be able to pick randomly
        # at each iteration a number of non-serious applications
        x_tmp = self.x
        t_tmp = self.t
        ids_tmp = self.ids
        self.x = []
        self.t = []
        self.ids = []
        for index in range(len(x_tmp)):
            if index not in serious_games_indexes:
                self.x.append(x_tmp[index])
                self.t.append(t_tmp[index])
                self.ids.append(ids_tmp[index])

    def train_model(self, final):
        """
        The training is implemented through an alternative K-fold cross-validation. This choice is made mainly because:
            1. The serious/non-serious dataset of applications is unbalanced.
            2. It is possible to achieve better performances.
        
        1. Here, with 10 iterations every time, 10 models are created, using the Logistic Regression technique. 
        In particular, for each model, all the serious applications are used. Instead, for each model, a new random
        sample of non-serious applications is drawn from the training dataset. In this way, the algorithms does not 
        tend to give more importance to the non-serious classification.
        
        2. The algorithm is run 10 times. At the end of each time, 
        10 models with 10 different classification performances are built. This is represented in the model as follows:
            a.  List of different resulting models (this is needed for 11th run, in which only one and final model
                is built)
            b.  List of Results entities (one per each trained model), 
                which contain a list of ['id_app', 'true_label','predicted_label']
        
        In this way, at the end of each iteration the update of the dictionaries which are used in order to evaluate 
        if an app is serious or not starting from the name and description is performed.
        The dictionaries update is done as follows:
        """
        # TODO : describe the update

        set_environment(is_train=True)

        feature_dataframe = extract_dataframe()

        self.x, self.t, self.ids = select_x_t_ids_arrays(feature_dataframe)

        n_serious_games, serious_games_indexes = self.find_number_and_indexes_serious_games()

        # extract from the target all the indexes which contain a serious application

        x_serious, t_serious, ids_serious = self.extract_serious_games_data(serious_games_indexes)
        self.remove_from_x_t_ids_serious_games(serious_games_indexes)

        iterations = 10
        if final:
            iterations = 1  # this is done for the 11th iteration of the outer loop, which needs only one final model
            # and not 10 different ones

        for iteration in range(iterations):
            x_non_serious, t_non_serious, ids_non_serious = \
                self.randomly_pick_non_serious_games(serious_games_size=n_serious_games)

            # now the data selected of serious and non-serious applications are merged for this iteration
            x_total = x_serious + x_non_serious
            np.random.shuffle(x_total)
            t_total = t_serious + t_non_serious
            np.random.shuffle(t_total)
            ids_total = ids_serious + ids_non_serious
            np.random.shuffle(ids_total)

            # do a split in order to perform the trained model on unseen data
            x_train, x_test, y_train, y_test, ids_train, ids_test = train_test_split(x_total, t_total, ids_total,
                                                                                     test_size=0.20,
                                                                                     random_state=42)

            # save the model created
            self.trained_models_list.append(
                LogisticRegression(penalty='l2'))  # regularization is applied as default
            # fit the model created
            self.trained_models_list[iteration].fit(x_train, y_train)

            # evaluate the model on the training set
            y_pred_list_train = self.trained_models_list[iteration].predict(
                x_train)  # predict_proba to have the probability estimate as output
            if final:
                self.save_and_print_performances(y_pred_list_train, y_train, 'Train_',
                                                 save_model_performances=False)

            # evaluate the model on the test set
            y_pred_list_test = self.trained_models_list[iteration].predict(
                x_test)  # predict_proba to have the probability estimate as output
            if final:
                self.save_and_print_performances(y_pred_list_test, y_test, 'Test_',
                                                 save_model_performances=True)

            # now save the results of the test set.
            # So, a list of ['id_app', 'true_label', 'predicted_label'] is provided.
            self.results.append(Results(y_test, y_pred_list_test, ids_test))
            if iterations == 1:
                now = datetime.now().strftime('%b%d_%H-%M-%S')
                exp_dir = os.path.join('./data/models/LogisticRegressionAppClassifier', 'Final_Model_' + str(now))
                if not os.path.exists(exp_dir):
                    os.makedirs(exp_dir)
                exp_file_path = os.path.join(exp_dir, 'Model.pckl')
                if os.path.exists(exp_file_path):
                    os.remove(exp_file_path)
                f_out = open(exp_file_path, 'wb')
                pickle.dump(self.trained_models_list[0], f_out)
                return exp_file_path

    def load_model(self, path):
        self.trained_models_list = []
        f_in = open(path, 'rb')
        self.trained_models_list.append(pickle.load(f_in))

    def save_and_print_performances(self, y_pred, y, model_name, save_model_performances):
        cm = confusion_matrix(y_true=transform_labels(y),
                              y_pred=transform_labels(y_pred),
                              labels=['Serious Game', 'Non-Serious Game'])
        # the confusion matrix is made of ([TN, FP], [FN, TP])

        cm_df = pd.DataFrame(cm, index=['Serious Game', 'Non-Serious Game'],
                             columns=['Serious Game', 'Non-Serious Game'])

        if save_model_performances:
            # these performances are saved in order to change the words weights in the serious and non serious
            # vocabularies used to classify the apps
            self.performance_metrics_list.append(PerformanceMetrics(accuracy=accuracy_score(y, y_pred),
                                                                    precision=precision_score(y, y_pred),
                                                                    recall=recall_score(y, y_pred),
                                                                    f1=f1_score(y, y_pred)))

        save_confusion_matrix(5, 3, 3, 2, cm_df, './data/output_data/' + str(model_name) + '_Model.png')

    def classify_apps(self):
        clear_table('selected_app')
        set_environment(is_train=False)

        dataset = retrieve_app_features()
        columns_names = retrieve_columns_names()
        feature_dataset = DataFrame(columns=columns_names, data=dataset)
        feature_dataset.drop('machine_classified', axis=1)
        feature_dataset['score_rating'] = feature_dataset['score'] * feature_dataset['rating']

        # The following line is added at debugging time to avoid having all teacher-approved applications = 0
        # (error in computation of z-score)
        # TODO : remove the following line after debug
        # feature_dataset.at[0, 'teacher_approved'] = 1

        x = zscore(feature_dataset[['serious_words_count', 'teacher_approved', 'score_rating', 'category_id']].values)

        i = 0
        app_id_list = feature_dataset[['app_id']].values
        y = self.trained_models_list[0].predict(x)
        for label_predicted in y:
            if label_predicted:
                app_id = str(app_id_list[i][0])
                do_query((app_id,), "INSERT INTO selected_app SELECT * FROM app WHERE %s = app.app_id")
                do_query([app_id], "UPDATE app_features SET machine_classified = TRUE WHERE %s = app_id")
            i = i + 1

    def randomly_pick_non_serious_games(self, serious_games_size):
        x_non_serious = []
        t_non_serious = []
        ids_non_serious = []

        for i in range(serious_games_size):
            index = random.randint(0, len(self.x) - 1)
            x_non_serious.append(self.x[index])
            t_non_serious.append(self.t[index])
            ids_non_serious.append(self.ids[index])

        return x_non_serious, t_non_serious, ids_non_serious
