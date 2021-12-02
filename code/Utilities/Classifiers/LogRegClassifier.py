from pandas import DataFrame
from scipy.stats import zscore
from sklearn.model_selection import train_test_split

import DataManagers.DatabaseManager
from DataManagers.DatabaseManager import do_query
from sklearn.utils import shuffle
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score


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


def print_performances(y_pred, y):
    print('The confusion matrix of the model is:')
    print(confusion_matrix(y, y_pred))

    print('\n')
    print('The accuracy of the model is: ' + str(accuracy_score(y, y_pred)))

    print('The precision of the model is: ' + str(precision_score(y, y_pred)))

    print('The recall of the model is: ' + str(recall_score(y, y_pred)))

    print('The precision of the model is: ' + str(f1_score(y, y_pred)))


class LogRegClassifier:
    def __init__(self):
        self.trained_model = LogisticRegression()

    def train_model(self):
        print('========================================== TRAINING ==========================================')
        dataset = retrieve_app_features_with_labels()
        columns_names = retrieve_columns_names()
        columns_names.append('human_classified')
        columns_names.remove('machine_classified')
        feature_dataset = DataFrame(columns=columns_names, data=dataset)
        feature_dataset['score_rating'] = feature_dataset['score'] * feature_dataset['rating']
        x = zscore(feature_dataset[['serious_words_count', 'teacher_approved', 'score_rating', 'category_id']].values)
        t = feature_dataset['human_classified'].values == 1

        x, t = shuffle(x, t, random_state=0)
        x_train, x_test, y_train, y_test = train_test_split(x, t, test_size=0.20, random_state=42)

        self.trained_model = LogisticRegression(penalty='l2')  # regularization is applied as default
        feat = x_train
        self.trained_model.fit(feat, y_train)

        i = 0
        app_id_list = feature_dataset[['app_id']].values
        y_pred_list = self.trained_model.predict(feat)
        for y_pred in y_pred_list:
            app_id = str(app_id_list[i][0])
            query = "UPDATE app_features SET machine_classified = %s WHERE app_id = %s"
            if y_pred:
                do_query([str(1), app_id], query)
            else:
                do_query([str(0), app_id], query)
            i = i + 1

        print_performances(y_pred_list, y_train)
        print('=================================================================================================')

        # TODO : uncomment the following line when ready to analyze the testing performances
        # self.test_model(x_test, y_test)

    def test_model(self, x_test, y_test):
        print('========================================== TESTING ==========================================')
        y_pred = self.trained_model.predict(x_test)
        print_performances(y_pred, y_test)
        print('=================================================================================================')

    def classify_apps(self):
        print('========================================== CLASSIFYING ==========================================')
        DataManagers.DatabaseManager.clear_table('selected_app')
        dataset = retrieve_app_features()
        columns_names = retrieve_columns_names()
        feature_dataset = DataFrame(columns=columns_names, data=dataset)
        feature_dataset.drop('machine_classified', axis=1)
        feature_dataset['score_rating'] = feature_dataset['score'] * feature_dataset['rating']
        x = zscore(feature_dataset[['serious_words_count', 'teacher_approved', 'score_rating', 'category_id']].values)

        i = 0
        app_id_list = feature_dataset[['app_id']].values
        y = self.trained_model.predict(x)
        for label_predicted in y:
            if label_predicted:
                app_id = str(app_id_list[i][0])
                do_query((app_id,), "INSERT INTO selected_app SELECT * FROM app WHERE %s = app.app_id")
                do_query([app_id], "UPDATE app_features SET machine_classified = TRUE WHERE %s = app_id")
            i = i + 1

        print('=================================================================================================')
