from pandas import DataFrame
from scipy.stats import zscore
from sklearn.model_selection import train_test_split
from DatabaseManager import do_query
from sklearn.utils import shuffle
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score


def retrieve_app_features():
    query = "SELECT * FROM app_features"
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


class LogRegClassifier:
    def __init__(self):
        self.trained_model = LogisticRegression

    def train_model(self):
        print('========================================== TRAINING ==========================================')
        dataset = retrieve_app_features()
        columns_names = retrieve_columns_names()
        feature_dataset = DataFrame(columns=columns_names, data=dataset)
        feature_dataset['score_rating'] = feature_dataset['score'] * feature_dataset['rating']
        X = zscore(feature_dataset[['serious_words_count', 'teacher_approved', 'score_rating', 'category_id']].values)
        t = feature_dataset['human_classified'].values == 1

        X, t = shuffle(X, t, random_state=0)
        X_train, X_test, y_train, y_test = train_test_split(X, t, test_size=0.20, random_state=42)

        self.trained_model = LogisticRegression(penalty='l2')  # regularization is applied as default
        feat = X_train
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

        print('The confusion matrix of the model is:')
        print(confusion_matrix(y_train, y_pred_list))

        print('\n')
        print('The accuracy of the model is: ' + str(accuracy_score(y_train, y_pred_list)))

        print('The precision of the model is: ' + str(precision_score(y_train, y_pred_list)))

        print('The recall of the model is: ' + str(recall_score(y_train, y_pred_list)))

        print('The precision of the model is: ' + str(f1_score(y_train, y_pred_list)))

    def classify_apps(self):
        print('========================================== CLASSIFYING ==========================================')
        dataset = retrieve_app_features()
        columns_names = retrieve_columns_names()
        feature_dataset = DataFrame(columns=columns_names, data=dataset)
        app_id_list = feature_dataset[['app_id']].values
        X = zscore(feature_dataset[['serious_words_count', 'teacher_approved', 'score_rating', 'category_id']].values)

        i = 0
        y = self.trained_model.predict(X)
        for label_predicted in y:
            if label_predicted:
                query = "INSERT INTO app_tmp(app_id) VALUES (%s)"
                do_query([str(app_id_list[i][0])], query)
            i = i + 1

