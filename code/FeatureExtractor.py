import random

from numpy import arange

from DatabaseManager import do_query, clear_table


def load_features():
    clear_table('app_features')
    clear_table('app_word_occurrences')
    query = "INSERT INTO app_features SELECT * FROM featured_all_app;"
    app_details = do_query('', query)


class FeatureExtractor:
    serious_games_words = []  # this is a set of meaningful words related to serious games, both manually and
    # automatically (done by the WordsMiner) extracted
    indexes_to_analyze = []

    def __init__(self, words):
        self.serious_games_words = words

    def compute_training_features(self):
        clear_table('app_features')
        clear_table('app_word_occurrences')
        query = "SELECT * FROM app"
        app_details = do_query('', query)
        self.generate_random_non_repeated_indexes(len(app_details) - 1)

        self.generate_feature(app_details)

    def compute_features(self):
        clear_table('app_features')
        clear_table('app_word_occurrences')
        query = "SELECT * FROM app"
        app_details = do_query('', query)
        for el in arange(0, len(app_details)):
            self.indexes_to_analyze.append(el)

        self.generate_feature(app_details)

    def generate_feature(self, app_details_list):
        i = 0
        while self.indexes_to_analyze:
            app = app_details_list[int(self.indexes_to_analyze[0])]
            self.indexes_to_analyze.pop(0)

            app_id = str(app[0])
            category_id = str(app[6])
            query = "SELECT id FROM category WHERE category_id = %s"
            result = do_query([category_id], query)
            if result:
                category_id = int(result[0][0])
            else:
                category_id = 15
            try:
                score = int(app[4])
            except TypeError:
                score = 0
            try:
                n_reviews = int(app[5])
            except TypeError:
                n_reviews = 0
            is_approved = int(app[8])
            serious_words_count, word_occurrence = self.count_occurrences(str(app[1]), str(app[2]))

            query = "INSERT INTO app_features(app_id, serious_words_count, teacher_approved, score, rating, " \
                    "category_id) " \
                    "VALUES (%s, %s, %s, %s, %s, %s)"
            do_query([app_id, serious_words_count, is_approved, score, n_reviews, category_id],
                     query)
            query = "INSERT INTO app_word_occurrences(app_id, app_name, word, occurrences) " \
                    "VALUES (%s, %s, %s, %s)"
            for word in word_occurrence.keys():
                do_query([app_id, str(app[1]), word, word_occurrence.get(word)], query)
            i = i + 1

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
            approved = app[8]
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
            if serious_word in app_name or serious_word in app_description:
                global_occurrences = global_occurrences + 1
                word_occurrence.__setitem__(serious_word, 1)
        return global_occurrences, word_occurrence
