import random
from numpy import arange
from DataManagers.DatabaseManager import do_query, clear_table, multiple_query
from settings import *
import regex as re


def get_words():
    serious_words_file = open('data/input_data/words/serious_words.txt', 'r').readlines()
    serious_words = []
    non_serious_words_file = open('data/input_data/words/non_serious_words.txt', 'r').readlines()
    non_serious_words = []

    for word in serious_words_file:
        serious_words.append(re.sub(r"[\n]+", " ", word))
    for word in non_serious_words_file:
        non_serious_words.append(re.sub(r"[\n]+", " ", word))

    return serious_words, non_serious_words


class FeatureExtractor:
    serious_games_words = []  # this is a set of meaningful words related to serious games (manually extracted)
    indexes_to_analyze = []

    def __init__(self, words):
        self.serious_games_words, self.non_serious_game_words = get_words()

    def compute_training_features(self):
        clear_table('app_features')
        query = "SELECT * FROM app WHERE app_id IN (SELECT app_id FROM labeled_app)"
        app_details = do_query('', query)
        self.generate_feature(app_details)

    def compute_features(self):
        clear_table('app_features')
        query = "SELECT * FROM app"
        app_details = do_query('', query)
        self.generate_feature(app_details)

    def generate_feature(self, app_details_list):
        insert_query = "INSERT IGNORE INTO app_features(app_id, serious_words_count, teacher_approved, score, rating, " \
                       "category_id) " \
                       "VALUES (%s, %s, %s, %s, %s, %s)"
        i = 0
        computed_features = []
        for app in app_details_list:
            computed_features.append(self.compute_features_values(app))
            if len(computed_features) > 500:
                multiple_query(computed_features, insert_query)
                computed_features = []
        if len(computed_features):
            multiple_query(computed_features, insert_query)

    def compute_features_values(self, app):
        app_id = str(app[APP_ID_POS])
        category_id = str(app[CATEGORY_ID_POS])
        query = "SELECT id FROM category WHERE category_id = %s"
        result = do_query([category_id], query)
        if result:
            category_id = int(result[0][0])
        else:
            category_id = 100
        try:
            score = float(app[SCORE_POS])
        except TypeError:
            score = 0
        try:
            n_reviews = int(app[RATING_POS])
        except TypeError:
            n_reviews = 0
        is_approved = int(app[TEACHER_APPROVED_DESC])
        serious_words_count, word_occurrence = self.count_occurrences(str(app[APP_NAME_POS]),
                                                                      str(app[DESCRIPTION_POS]))

        return app_id, serious_words_count, is_approved, score, n_reviews, category_id

    def generate_random_non_repeated_indexes(self, max_value):
        try:
            f_out = open('./data/input_data/training_samples.txt', 'r')
            content = f_out.readlines()[0]
            ints_list = content.split(sep=',')
            for int_el in ints_list:
                self.indexes_to_analyze.append(int_el)
        except FileNotFoundError:
            self.first_initialization(max_value)

    def first_initialization(self, max_value):
        f_out = open('./data/input_data/training_samples.txt', 'w')
        self.select_400_teacher_approved(f_out)
        while len(self.indexes_to_analyze) < 1200:
            random_generator = random.Random()
            random_integer = random_generator.randint(0, max_value)
            if random_integer not in self.indexes_to_analyze:
                self.indexes_to_analyze.append(random_integer)
                if len(self.indexes_to_analyze) == 1200:
                    f_out.write(str(random_integer))
                else:
                    f_out.write(str(random_integer) + ',')

    def select_400_teacher_approved(self, file_out):
        query = "SELECT * FROM APP"
        app_details = do_query('', query)
        i = 0
        teacher_approved_index = 0
        for app in app_details:
            approved = app[TEACHER_APPROVED_DESC]
            if approved == 1:
                self.indexes_to_analyze.append(teacher_approved_index)
                file_out.write(str(teacher_approved_index) + ',')
                i = i + 1
            teacher_approved_index = teacher_approved_index + 1
            if i == 400:
                break

    def count_occurrences(self, app_name, app_description):
        word_occurrence = {}
        global_occurrences = 0
        for serious_word in self.serious_games_words:
            if serious_word in app_description or serious_word in app_name:
                global_occurrences += len(serious_word.split())
                word_occurrence.__setitem__(serious_word, 1)
        for non_serious_word in self.non_serious_game_words:
            if non_serious_word in app_description:
                global_occurrences += (-1.05)*len(non_serious_word.split())
        return global_occurrences, word_occurrence
