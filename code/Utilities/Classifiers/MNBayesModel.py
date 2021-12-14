import math
import random
from nltk import WordNetLemmatizer
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from DataManagers.settings import SMOOTHING_COEFFICIENT, stop_words, TEST_SET_DIMENSION, NON_IMPROVING_ITERATIONS, \
    ITERATION_FREQUENCY_UPDATE
from DataModel.PerformanceMetrics import PerformanceMetrics
from DataManagers.DatabaseManager import do_query as database_query, clear_table


def calculate_likelihood(class_occurrences, class_size, vocabulary_size):
    nominator = class_occurrences + SMOOTHING_COEFFICIENT
    denominator = class_size + vocabulary_size + 1
    return math.log2(nominator / denominator)


def count_all_word_in_dict(dictionary):
    count = 0
    for word in dictionary:
        count += dictionary[word]
    return count


def order_dictionary_desc(dictionary):
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)}


def save_dictionary(dictionary1, dictionary2):
    dict = order_dictionary_desc(dictionary1)
    dict2 = order_dictionary_desc(dictionary2)

    file = open('banana.txt', 'w')
    for app in dict:
        if dict[app] > dict2[app]:
            file.write(f'{dict2[app]} | {app} | {dict[app]}\n')
    pass
    file.close()
    file = open('banana2.txt', 'w')
    for app in dict2:
        file.write(f'{dict2[app]} | {app}\n')


class MNBayesClassifierModel:
    def __init__(self, assigned_id, training):
        self.__id = assigned_id
        self.__iteration_count = 0
        self.__training_set = []
        self.__testing_set = []
        self.__create_model_sets(training)
        #  occurrences of the words in considered classes
        self.__serious_words = {}
        self.__non_serious_words = {}
        # vocabulary is a dictionary containing all words in the training apps and their occurrences
        self.__vocabulary = {}
        #  dictionaries containing likelihoods for each word in respective classes
        self.__serious_likelihoods = {}
        self.__non_serious_likelihoods = {}
        #  current performance of the model evaluated on the validation set
        self.__performance = PerformanceMetrics(0, 0, 0, 0)
        #  prior probabilities are calculated during model creation even with balanced training.
        self.__prior_probabilities = self.calculate_prior_probabilities()
        #  performance metrics and occurrences of the best iteration are saved
        #  if in the next iterations performances improves then values will be updated, if not then these values will be
        #  restored and used for classification. The number of iterations after each save are defined in settings file.
        self.__best_performance = PerformanceMetrics(0, 0, 0, 0)
        self.__best_likelihoods = []
        #  following lists are used for saving classification of apps from training set after each train iteration.
        self.__training_classified_serious = []
        self.__training_classified_non_serious = []
        self.__training_apps_classification_distribution = {}
        #  flag indicating when the model completed the training process.
        self.__training_complete = False
        self.__after_best_iterations = 0

    def __create_model_sets(self, tuples):
        """
        Method dividing the application given by classification manager in two sets: training and validation.
        Training is used for training while validation is set used to analyze the performance.
        :param tuples: result tuples containing needed data about apps
        """

        serious_apps = [app for app in tuples if app[1]]
        non_serious_apps = [app for app in tuples if not app[1]]

        training_serious = random.sample(serious_apps, int(len(serious_apps) * (1 - TEST_SET_DIMENSION)))
        training_non_serious = random.sample(non_serious_apps, int(len(non_serious_apps) * (1 - TEST_SET_DIMENSION)))

        self.__training_set = training_serious + training_non_serious
        self.__testing_set = [app for app in tuples if app not in self.__training_set]

    def calculate_prior_probabilities(self):
        """
        Method calculating prior probabilities for the two classes of app (serious or non serious)
        :return: dictionary containing prior probabilities
        """
        serious_count = non_serious_count = 0
        for app in self.__training_set:
            if app[1]:
                serious_count += 1
            else:
                non_serious_count += 1
        prior_serious_probability = math.log2(serious_count / len(self.__training_set))
        prior_non_serious_probability = math.log2(non_serious_count / len(self.__training_set))
        return {'serious': prior_serious_probability, 'non-serious': prior_non_serious_probability}

    def train_model(self):
        self.examine_descriptions()
        self.create_global_vocabulary()
        self.delete_stopwords()
        self.create_global_vocabulary()
        while not self.__training_complete:
            self.__iteration_count += 1
            self.compute_likelihoods()
            self.evaluate_model()
            self.__update_occurrences()

        # save_dictionary(self.non_serious_likelihoods, self.serious_likelihoods)

    def delete_stopwords(self):
        """
        Method deleting stop words from the created dictionaries.
        """
        for word in self.__vocabulary:
            if word in stop_words:
                self.__serious_words[word] = 0
                self.__non_serious_words[word] = 0
                self.__serious_words.pop(word)
                self.__non_serious_words.pop(word)

    def examine_descriptions(self):
        """
        Method taking description from training set and starting tokenization process for each of them
        """
        for training_tuple in self.__training_set:
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
            used_dictionary = self.__serious_words
        else:
            used_dictionary = self.__non_serious_words

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
        dictionaries = [self.__serious_words, self.__non_serious_words]
        self.__vocabulary.clear()
        for dictionary in dictionaries:
            for word in dictionary:
                if word in self.__vocabulary:
                    self.__vocabulary[word] += dictionary[word]
                else:
                    self.__vocabulary[word] = dictionary[word]

    def compute_likelihoods(self):
        """
        Log likelihood probabilities are calculated for both classes and then inserted in
        respective dictionary.
        """
        vocabulary_size = len(self.__vocabulary)
        serious_size = count_all_word_in_dict(self.__serious_words)
        non_serious_size = count_all_word_in_dict(self.__non_serious_words)
        for word in self.__vocabulary:
            total_count = self.__vocabulary[word]
            if total_count == 0:
                continue
            try:
                serious_count = self.__serious_words[word]
            except KeyError:
                serious_count = 0
            try:
                non_serious_count = self.__non_serious_words[word]
            except KeyError:
                non_serious_count = 0

            self.__serious_likelihoods[word] = calculate_likelihood(serious_count, serious_size, vocabulary_size)
            self.__non_serious_likelihoods[word] = calculate_likelihood(non_serious_count, non_serious_size,
                                                                        vocabulary_size)

    def save_performance(self):
        """
        Method saving the current performances as the best overall
        """
        self.__best_performance = self.__performance

    def save_likelihoods(self):
        """
        Method saving in a list a copy of the likelihoods with best performances in order to restore it if needed
        """
        self.__best_likelihoods = [self.__serious_likelihoods.copy(), self.__non_serious_likelihoods.copy()]

    def restore_best_model(self):
        """
        Method used to restore the status of the model with best performance.
        After this the training process is terminated and __training_complete flag is set to True.
        Finally words dictionaries are deleted in order to not waste memory
        """
        self.__performance = self.__best_performance
        self.__serious_likelihoods = self.__best_likelihoods[0]
        self.__non_serious_likelihoods = self.__best_likelihoods[1]
        self.__training_complete = True
        self.__serious_words = self.__non_serious_words = self.__vocabulary = None

    def calculate_performances(self, true_labels, predicted_labels):

        self.__performance = PerformanceMetrics(accuracy=accuracy_score(true_labels, predicted_labels),
                                                precision=precision_score(true_labels, predicted_labels),
                                                recall=recall_score(true_labels, predicted_labels),
                                                f1=f1_score(true_labels, predicted_labels))
        test_tp = len([app for app in self.__training_classified_serious if app[1] and app in self.__testing_set])
        test_tn = len(
            [app for app in self.__training_classified_non_serious if (not app[1]) and app in self.__testing_set])
        test_fp = len([app for app in self.__training_classified_serious if (not app[1]) and app in self.__testing_set])
        test_fn = len([app for app in self.__training_classified_non_serious if app[1] and app in self.__testing_set])

        print(f'Recall : {self.__performance.recall}\tAccuracy : {self.__performance.accuracy}\t'
              f'Precision : {self.__performance.precision}\tF1 score: {self.__performance.f1}\t '
              f'TP {test_tp},'
              f' TN {test_tn}, FN {test_fn}, FP {test_fp}')

        # TODO test_distribution rewrite for better performance
        print(str(self.__id) + str(self.__iteration_count))
        database_query((self.__id, self.__iteration_count, self.__performance.recall, self.__performance.accuracy,
                        self.__performance.precision, self.__performance.f1, test_tp, test_tn, test_fp, test_fn),
                       "INSERT INTO classification_performance(model_id, iteration, recall, accuracy, `precision`, "
                       "f1_score, true_positive, true_negative, false_positive, false_negative) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    def __training_classification(self):
        """
        Method classifying all apps from testing and training sets combined.
        """
        self.__training_classified_serious.clear()
        self.__training_classified_non_serious.clear()
        for app in self.__testing_set + self.__training_set:
            if self.classify_app(app):
                self.__training_classified_serious.append(app)
            else:
                self.__training_classified_non_serious.append(app)

    def __create_validation_labels(self):
        """
        Method creating labels with true and predicted labels for each app in validation set
        """
        true_labels = []
        predicted_labels = []
        for app in self.__testing_set:
            true_labels.append(app[1])
            predicted_labels.append(app in self.__training_classified_serious)
        return true_labels, predicted_labels

    def __create_training_apps_classification_distribution(self):
        self.__training_apps_classification_distribution.clear()
        self.__training_apps_classification_distribution['TP'] = [app for app in self.__training_classified_serious if
                                                                  app[1] and app in self.__training_set]
        self.__training_apps_classification_distribution['TN'] = [app for app in self.__training_classified_non_serious
                                                                  if not app[1] and app in self.__training_set]
        self.__training_apps_classification_distribution['FP'] = [app for app in self.__training_classified_serious if
                                                                  not app[1] and app in self.__training_set]
        self.__training_apps_classification_distribution['FN'] = [app for app in self.__training_classified_non_serious
                                                                  if app[1] and app in self.__training_set]

    def evaluate_model(self):
        self.__training_classification()
        y_true, y_pred = self.__create_validation_labels()
        self.calculate_performances(y_true, y_pred)
        self.__create_training_apps_classification_distribution()

        if self.has_better_performances():
            self.__after_best_iterations = 0
            self.save_performance()
            self.save_likelihoods()
        else:
            self.__after_best_iterations += 1

        #self.create_global_vocabulary()
        #self.compute_likelihoods()
        #self.evaluate_model()

    def __update_occurrences(self):
        for app in self.__training_apps_classification_distribution['FN']:
            for word in self.__serious_words:
                if word in app[0]:
                    self.__serious_words[word] += ITERATION_FREQUENCY_UPDATE
        for app in self.__training_apps_classification_distribution['FP']:
            for word in self.__non_serious_words:
                if word in app[0]:
                    self.__non_serious_words[word] += ITERATION_FREQUENCY_UPDATE
        self.create_global_vocabulary()

    def has_better_performances(self):
        """
        Method compares the performance of the model at a given time with the best result overall.
        :return: True if model improved the performance, False otherwise.
        """
        return self.__performance.f1 > self.__best_performance.f1

    def classify_app(self, app):
        """
        Considering the description of the application calculates the probability of app being a serious game or not.
        :param app: tuple containing data about application.
        :return: True if the considered app is more likely to be serious game, False otherwise.
        """
        serious_probability = self.__prior_probabilities['serious']
        non_serious_probability = self.__prior_probabilities['non-serious']
        app_description = app[0]
        for word in self.__serious_likelihoods:
            if word in app_description:
                serious_probability += self.__serious_likelihoods[word]
        for word in self.__non_serious_likelihoods:
            if word in app_description:
                non_serious_probability += self.__non_serious_likelihoods[word]
        return serious_probability > non_serious_probability
