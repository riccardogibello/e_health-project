import math

from nltk import PunktSentenceTokenizer, sent_tokenize, WordPunctTokenizer, WordNetLemmatizer
from nltk.corpus import stopwords
from DataManagers.settings import SMOOTHING_COEFFICIENT, DEBUG, stop_words

from DataManagers.DatabaseManager import do_query as query, clear_table


def get_apps_descriptions():
    result_tuples = query(None, "SELECT app_id, description FROM app")
    apps = {}
    for tuple in result_tuples:
        apps[tuple[0]] = tuple[1]
    return apps


def get_training():
    """
    This method extracts from database information about applications contained in the training set.
    These will be used for training the model and then for classification of all applications.
    :return: list of tuples containing the description of the app and how the app is classified
    """
    return query(None,
                 "SELECT A.description, LA.human_classified "
                 "FROM app as A, labeled_app as LA "
                 "WHERE A.app_id = LA.app_id")  # the method query directly creates the list of tuples


def calculate_likelihood(class_occurrences, total_occurrences, vocabulary_size):
    nominator = class_occurrences + SMOOTHING_COEFFICIENT
    denominator = total_occurrences + vocabulary_size + 1
    return math.log2(nominator / denominator)


class MNBayesAppsClassifier:

    def __init__(self):
        self.training_set = get_training()
        self.stop_words = stop_words
        self.prior_probabilities = self.calculate_prior_probabilities()
        self.serious_games_words = {}
        self.non_serious_games_words = {}
        self.vocabulary = {}
        self.serious_likelihoods = {}
        self.non_serious_likelihoods = {}
        self.create_bag_of_words()
        self.compute_likelihoods()

    def calculate_prior_probabilities(self):
        """
        Method calculating prior probabilities for the two classes of app (serious or non serious)
        :return: dictionary containing prior probabilities
        """
        serious_count = non_serious_count = 0
        for app in self.training_set:
            if app[1]:
                serious_count += 1
            else:
                non_serious_count += 1
        prior_serious_probability = math.log2(serious_count / len(self.training_set))
        prior_non_serious_probability = math.log2(non_serious_count / len(self.training_set))
        return {'serious': prior_serious_probability, 'non-serious': prior_non_serious_probability}

    def create_bag_of_words(self):
        self.examine_descriptions()
        self.create_global_vocabulary()
        self.delete_stopwords()

    def delete_stopwords(self):
        for word in self.vocabulary:
            if word in self.stop_words:
                self.vocabulary[word] = 0
                self.serious_games_words[word] = 0
                self.non_serious_games_words[word] = 0

    def examine_descriptions(self):
        for training_tuple in self.training_set:
            description = training_tuple[0].lower()
            serious = training_tuple[1]
            self.tokenize_description(description, serious)

    def tokenize_description(self, description, serious):
        """
        Divides the description into tokens and if possible performs the lemmatisation
        using WordNet dictionary.
        :param description: considered description
        :param serious: boolean flag indicating the description belonging to serious category
        """
        if serious:
            used_dictionary = self.serious_games_words
        else:
            used_dictionary = self.non_serious_games_words

        # Using split method because descriptions are already without punctuation
        # due to use of clean_text method from mysmallutils package during insertion in database
        description_tokens = description.split()

        lemmatizer = WordNetLemmatizer()

        for token in description_tokens:
            word = lemmatizer.lemmatize(token)
            if word in used_dictionary:
                used_dictionary[word] += 1
            else:
                used_dictionary[word] = 1

    def create_global_vocabulary(self):
        """
        Creates a vocabulary given the two dictionaries of serious and non serious games words.
        The result is a dictionary containing all words from the description and their occurrences
        """
        dictionaries = [self.serious_games_words, self.non_serious_games_words]
        for dictionary in dictionaries:
            for word in dictionary:
                if word in self.vocabulary:
                    self.vocabulary[word] += dictionary[word]
                else:
                    self.vocabulary[word] = dictionary[word]

    def compute_likelihoods(self):
        """
        Log likelihood probabilities are calculated for both classes and then inserted in
        respective dictionary.
        """
        vocabulary_size = len(self.vocabulary)
        for word in self.vocabulary:
            total_count = self.vocabulary[word]
            if total_count == 0:
                continue
            try:
                serious_count = self.serious_games_words[word]
            except KeyError:
                serious_count = 0
            try:
                non_serious_count = self.non_serious_games_words[word]
            except KeyError:
                non_serious_count = 0

            self.serious_likelihoods[word] = calculate_likelihood(serious_count, total_count, vocabulary_size)
            self.non_serious_likelihoods[word] = calculate_likelihood(non_serious_count, total_count, vocabulary_size)

    def classify_apps(self):
        if DEBUG:
            print("NAIVE BAYES CLASSIFIER: Classification started!")
        description_dict = get_apps_descriptions()

        #print(self.serious_games_words)

        clear_table('selected_app')
        i = 0

        for app in description_dict:
            serious_probability = self.prior_probabilities['serious']
            non_serious_probability = self.prior_probabilities['non-serious']
            #serious_probability = non_serious_probability = 0
            for word in self.serious_likelihoods:
                if word in description_dict[app]:
                    serious_probability += self.serious_likelihoods[word]
            for word in self.non_serious_likelihoods:
                if word in description_dict[app]:
                    non_serious_probability += self.non_serious_likelihoods[word]
            i += 1
            if (i%100) == 0: print(i)
            #print(f'Probabilities for {app} - S:{serious_probability} - NS {non_serious_probability}')
            if serious_probability > non_serious_probability:
                print(f' SERIOUS!!!!!! Probabilities for {app} - S:{serious_probability} - NS {non_serious_probability}')
                query((app,), "INSERT INTO selected_app SELECT * FROM app WHERE %s = app.app_id")

