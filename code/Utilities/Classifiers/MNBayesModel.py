import math
import random
from nltk import WordNetLemmatizer
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from DataManagers.settings import SMOOTHING_COEFFICIENT, stop_words, TEST_SET_DIMENSION
from DataModel.PerformanceMetrics import PerformanceMetrics


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
    def __init__(self, training):
        self.__training_set = []
        self.__testing_set = []
        self.__create_model_sets(training)
        self.__serious_words = {}
        self.__non_serious_words = {}
        self.__vocabulary = {}
        self.__serious_likelihoods = {}
        self.__non_serious_likelihoods = {}
        #  prior probabilities are calculated during model creation even with balanced training.
        self.__prior_probabilities = self.calculate_prior_probabilities()
        #  performance metrics and occurrences of the best iteration are saved
        #  if in the next iterations performances improves then values will be updated, if not then these values will be
        #  restored and used for classification. The number of iterations after each save are defined in settings file.
        self.__performance = PerformanceMetrics(0, 0, 0, 0)
        self.__best_likelihoods = []
        #  following lists are used for saving classification of apps from training set after each train iteration.
        self.__training_classified_serious = []
        self.__training_classified_non_serious = []
        #  flag indicating when the model completed the training process.
        self.__training_complete = False

    def __create_model_sets(self, tuples):

        serious_apps = [app for app in tuples if app[1]]
        non_serious_apps = [app for app in tuples if not app[1]]

        training_serious = random.sample(serious_apps, int(len(serious_apps) * (1 - TEST_SET_DIMENSION)))
        training_non_serious = random.sample(non_serious_apps, int(len(non_serious_apps) * (1 - TEST_SET_DIMENSION)))

        self.__training_set = training_serious + training_non_serious
        self.__testing_set = [app for app in tuples if app not in self.__training_set]

        #for app in serious_apps + non_serious_apps:
        #    if app not in training_serious:
        #        self.__testing_set.append(app)
        #for app in non_serious_apps:
        #    if app not in training_non_serious:
        #        self.__testing_set.append(app)
        print(len(self.__testing_set))

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
        self.compute_likelihoods()
        self.evaluate_model()

        # save_dictionary(self.non_serious_likelihoods, self.serious_likelihoods)

    def delete_stopwords(self):
        for word in self.vocabulary:
            if word in stop_words:
                self.__serious_words[word] = 0
                self.__non_serious_words[word] = 0
                self.__serious_words.pop(word)
                self.__non_serious_words.pop(word)

    def examine_descriptions(self):
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
        self.vocabulary = {}
        for dictionary in dictionaries:
            for word in dictionary:
                if word in self.vocabulary:
                    self.vocabulary[word] += dictionary[word]
                else:
                    self.vocabulary[word] = dictionary[word]

    def  compute_likelihoods(self):
        """
        Log likelihood probabilities are calculated for both classes and then inserted in
        respective dictionary.
        """
        vocabulary_size = len(self.vocabulary)
        serious_size = count_all_word_in_dict(self.__serious_words)
        non_serious_size = count_all_word_in_dict(self.__non_serious_words)
        for word in self.vocabulary:
            total_count = self.vocabulary[word]
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

    def save_performance(self, true, predicted):
        self.__performance = PerformanceMetrics(accuracy=accuracy_score(true, predicted),
                                                precision=precision_score(true, predicted),
                                                f1=f1_score(true, predicted),
                                                recall=recall_score(true, predicted))

    def evaluate_model(self):
        classified_serious = []
        classified_non_serious = []
        y_true = []
        y_pred = []
        for app in self.__testing_set + self.__training_set:
            if self.classify_app(app):
                classified_serious.append(app)
            else:
                classified_non_serious.append(app)
        #print(len(self.__testing_set))
        for app in self.__testing_set:
            y_true.append(app[1])
            y_pred.append(app in classified_serious)

        # print(f'TRUE {len(y_true)}')
        # print(f'PRED {len(y_pred)}')

            # if app[1]:
            #    y_true.append(1)
            # elif not app[1]:
            #    y_true.append(0)
            # TODO remove after debug
            # if app in classified_serious:
            #    y_pred.append(1)
            # else:
            #    y_pred.append(0)
        self.save_performance(y_true, y_pred)

        tn = []
        tp = []
        fn = []
        fp = []

        #test_tn = 0
        #test_fn = 0
        #test_tp = 0
        #test_fp = 0

        print([app for app in self.__testing_set if app in classified_serious and app[1] is False])
        test_fp = 0
        test_tp = len([app for app in self.__testing_set if app in classified_serious and app[1] is True])
        test_tn = len([app for app in self.__testing_set if app in classified_non_serious and app[1] is False])
        test_fn = len([app for app in self.__testing_set if (app in classified_non_serious and app[1] is True)])

        for app in classified_serious:
            if app[1]:
                if app in self.__training_set:
                    tp.append(app)
            else:
                if app in self.__training_set:
                    fp.append(app)

        for app in classified_non_serious:
            if app[1]:
                if app in self.__training_set:
                    fn.append(app)
            else:
                if app in self.__training_set:
                    tn.append(app)

        # precision = test_tp / (test_tp + test_fn)
        # print(f"MODEL precision: {precision}")
        print(f'Recall : {recall_score(y_true, y_pred)}\tAccuracy : {accuracy_score(y_true, y_pred)}\t'
              f'Precision : {precision_score(y_true,y_pred)}\tF1 score: {f1_score(y_true,y_pred)}\t '
              f'TP {test_tp},'
              f' TN {test_tn}, FN {test_fn}, FP {test_fp}')

        for app in fn:
            if app in self.__testing_set:
                continue
            for word in self.__serious_words:
                if word in app[0]:
                    self.__serious_words[word] += 0.0025
        for app in fp:
            if app in self.__testing_set:
                continue
            for word in self.__non_serious_words:
                if word in app[0]:
                    self.__non_serious_words[word] += 0.0025
        self.create_global_vocabulary()
        self.compute_likelihoods()
        self.evaluate_model()

    def classify_app(self, app):
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
