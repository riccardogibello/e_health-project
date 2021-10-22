from DatabaseManager import do_query


class FeatureExtractor:
    serious_games_words = []  # this is a set of meaningful words related to serious games, both manually and
    # automatically (done by the WordsMiner) extracted

    def __init__(self, words):
        self.serious_games_words = words

    def compute_features(self):
        query = "SELECT * FROM APP"
        app_details = do_query('', query)

        for app in app_details:
            app_id = str(app[0])
            score = int(app[4])
            n_reviews = int(app[5])
            is_approved = int(app[9])
            serious_words_count, word_occurrence = self.count_occurrences(str(app[1]), str(app[2]))

            query = "INSERT INTO app_features(app_id, serious_words_count, teacher_approved, score, rating) " \
                    "VALUES (%s, %s, %s, %s, %s)"
            do_query([app_id, serious_words_count, is_approved, score, n_reviews], query)
            query = "INSERT INTO app_word_occurrences(app_id, app_name, word, occurrences) " \
                    "VALUES (%s, %s, %s, %s)"
            for word in word_occurrence.keys():
                do_query([app_id, str(app[1]), word, word_occurrence.get(word)], query)

    def count_occurrences(self, app_name, app_description):
        occurrences = 0
        word_occurrence = {}
        for serious_word in self.serious_games_words:
            if serious_word in app_name or serious_word in app_description:
                occurrences = occurrences + 1
            word_occurrence.__setitem__(serious_word, occurrences)
        return occurrences, word_occurrence
