import math
import random
from nltk import WordNetLemmatizer
from DataModel.PerformanceMetrics import PerformanceMetrics
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, matthews_corrcoef
from DataManagers.settings import SMOOTHING_COEFFICIENT, stop_words, TEST_SET_DIMENSION, NON_IMPROVING_ITERATIONS, \
    WRONG_CLASSIFIED_INCREMENT, TRUE_CLASSIFIED_INCREMENT, MAX_ITERATIONS


def calculate_likelihood(class_occurrences, class_size, vocabulary_size):
    """
    Formula to calculate the likelihood of a word to be part of a given class.
    :param class_occurrences: count of the word in the class.
    :param class_size: number of words in the class including repetitions.
    :param vocabulary_size: number of unique words in the given class.
    :return: probability value.
    """
    nominator = class_occurrences + SMOOTHING_COEFFICIENT
    denominator = class_size + vocabulary_size + 1
    return math.log2(nominator / denominator)


def calculate_app_distribution_from_labels(true_labels, predicted_labels):
    """
    Given two lists of labels creates the number of true positives, true negatives, false positives and false negatives.
    :param true_labels: labels with manual classification values.
    :param predicted_labels: labels with algorithm prediction values.
    :return: Four integers with number of elements in respective class.
    """
    tp = len([true_labels[i] for i in range(len(true_labels)) if true_labels[i] and predicted_labels[i]])
    tn = len([true_labels[i] for i in range(len(true_labels)) if not true_labels[i] and not predicted_labels[i]])
    fp = len([true_labels[i] for i in range(len(true_labels)) if not true_labels[i] and predicted_labels[i]])
    fn = len([true_labels[i] for i in range(len(true_labels)) if true_labels[i] and not predicted_labels[i]])
    return tp, tn, fp, fn


def count_all_word_in_dict(dictionary):
    """
    Function counting all words in given class.
    :param dictionary: dictionary containing all words of a class as key
           and their occurrences as respective integer value.
    :return: number of words in the class.
    """
    return sum(dictionary.values())


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
        self.__performance = PerformanceMetrics()
        #  prior probabilities are calculated during model creation even with balanced training.
        self.__prior_probabilities = self.__calculate_prior_probabilities()
        #  performance metrics and occurrences of the best iteration are saved
        #  if in the next iterations performances improves then values will be updated, if not then these values will be
        #  restored and used for classification. The number of iterations after each save are defined in settings file.
        self.__best_performance = PerformanceMetrics()
        self.__best_likelihoods = [{}, {}]
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

    def __calculate_prior_probabilities(self):
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
        """
        Method managing training process of the model.
        """
        self.__examine_descriptions()
        self.__delete_stopwords()
        self.__create_global_vocabulary()
        while not self.__training_complete:
            self.__iteration_count += 1
            self.compute_likelihoods()
            self.__evaluate_model()
            self.__update_occurrences()
            self.__training_complete = self.__after_best_iterations >= NON_IMPROVING_ITERATIONS
            self.__training_complete += self.__iteration_count >= MAX_ITERATIONS
        self.__restore_best_model()

    def __delete_stopwords(self):
        """
        Method deleting stop words from the created dictionaries.
        """
        for word in set(self.__serious_words) | set(self.__non_serious_words):
            if word in stop_words:
                self.__serious_words[word] = 0
                self.__non_serious_words[word] = 0
                self.__serious_words.pop(word)
                self.__non_serious_words.pop(word)

    def __examine_descriptions(self):
        """
        Method taking description from training set and starting tokenization process for each of them
        """
        for training_tuple in self.__training_set:
            description = training_tuple[0].lower()
            serious = training_tuple[1]
            self.__tokenize_description(description, serious)

    def __tokenize_description(self, description, serious):
        """
        Divides the description into tokens and if possible performs the lemmatisation
        using WordNet dictionary.
        :param description: considered description
        :param serious: boolean flag indicating the description belonging to serious category
        """
        used_dictionary = self.__serious_words if serious else self.__non_serious_words

        # Using split method because descriptions are already without punctuation
        # due to use of clean_text method from mysmallutils package during insertion in database
        description_tokens = description.split()
        lemmatizer = WordNetLemmatizer()

        for token in description_tokens:
            word = lemmatizer.lemmatize(token)

            used_dictionary[word] = (used_dictionary[word] + 1) if word in used_dictionary else 1

    def __create_global_vocabulary(self):
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

    def __save_performance(self):
        """
        Method saving the current performances as the best overall of the model.
        The check is done before calling the method.
        """
        self.__best_performance = self.__performance

    def __save_likelihoods(self):
        """
        Method saving in a list a copy of the likelihoods with best performances in order to restore it at the
        end of the instance training process.
        """
        self.__best_likelihoods = [self.__serious_likelihoods.copy(), self.__non_serious_likelihoods.copy()]

    def __restore_best_model(self):
        """
        Method used to restore the status of the model with best performance.
        After this the training process is terminated and __training_complete flag is set to True.
        Finally words dictionaries are deleted in order to not waste memory
        """
        self.__performance = self.__best_performance
        self.__serious_likelihoods = self.__best_likelihoods[0]
        self.__non_serious_likelihoods = self.__best_likelihoods[1]
        self.__serious_words = self.__non_serious_words = self.__vocabulary = None
        self.__training_classified_serious = self.__training_classified_non_serious = None
        self.__training_apps_classification_distribution = self.__after_best_iterations = None

    def calculate_performances(self, true_labels, predicted_labels):
        """
        Method used to compute the performances of the classifier instance. Calculates
        :param true_labels: labels with the value in test set.
        :param predicted_labels: labels with values predicted by the classifier.
        """
        tp, tn, fp, fn = calculate_app_distribution_from_labels(true_labels, predicted_labels)

        self.__performance = PerformanceMetrics(accuracy=accuracy_score(true_labels, predicted_labels),
                                                precision=precision_score(true_labels, predicted_labels),
                                                recall=recall_score(true_labels, predicted_labels),
                                                f1=f1_score(true_labels, predicted_labels),
                                                matthews_cc=matthews_corrcoef(true_labels, predicted_labels),
                                                tp=tp, tn=tn, fp=fp, fn=fn)

    def __training_classification(self):
        """
        Method classifying all apps from testing and training sets combined.
        """
        self.__training_classified_serious.clear()
        self.__training_classified_non_serious.clear()
        for app in self.__testing_set + self.__training_set:
            classification_result = self.classify_app(app[0])
            if classification_result['serious'] > classification_result['non-serious']:
                self.__training_classified_serious.append(app)
            else:
                self.__training_classified_non_serious.append(app)

    def __create_validation_labels(self):
        """
        Method creating labels for each app in validation set.
        :return two lists containing true and predicted respectively.
        """
        true_labels = []
        predicted_labels = []
        for app in self.__testing_set:
            true_labels.append(app[1])
            predicted_labels.append(app in self.__training_classified_serious)
        return true_labels, predicted_labels

    def __create_training_apps_classification_distribution(self):
        """
        Method creating the lists of applications based on the way they was classified by the classifier.
        These lists will be used for occurrence update after each training iteration.
        :return:
        """
        self.__training_apps_classification_distribution.clear()
        self.__training_apps_classification_distribution['TP'] = [app for app in self.__training_classified_serious if
                                                                  app[1] and app in self.__training_set]
        self.__training_apps_classification_distribution['TN'] = [app for app in self.__training_classified_non_serious
                                                                  if not app[1] and app in self.__training_set]
        self.__training_apps_classification_distribution['FP'] = [app for app in self.__training_classified_serious if
                                                                  not app[1] and app in self.__training_set]
        self.__training_apps_classification_distribution['FN'] = [app for app in self.__training_classified_non_serious
                                                                  if app[1] and app in self.__training_set]

    def __evaluate_model(self):
        """
        Evaluation of the model performances on the validation set.
        All applications from training and validation sets are classified using the current model and then performances
        are computed. If the current model is better then the best among previous ones then it becomes the new best and
        likelihood are saved.
        """
        self.__training_classification()
        y_true, y_pred = self.__create_validation_labels()
        self.calculate_performances(y_true, y_pred)
        self.__create_training_apps_classification_distribution()

        if self.__has_better_performances():
            self.__after_best_iterations = 1
            self.__save_performance()
            self.__save_likelihoods()
        else:
            self.__after_best_iterations += 1

    def __update_occurrences(self):
        """
        After evaluation, if needed, the occurrences of the words are updated.
        :return:
        """
        false_positive_number = len(self.__training_apps_classification_distribution['FP'])
        false_positive_number = false_positive_number if false_positive_number else 1
        false_negative_number = len(self.__training_apps_classification_distribution['FN'])
        false_negative_number = false_negative_number if false_negative_number else 1

        for app in self.__training_apps_classification_distribution['FN']:
            desc = app[0].split()
            for word in desc:
                try:
                    self.__serious_words[
                        word] += WRONG_CLASSIFIED_INCREMENT * false_negative_number / false_positive_number
                except KeyError:
                    pass
        for app in self.__training_apps_classification_distribution['FP']:
            desc = app[0].split()
            for word in desc:
                try:
                    self.__non_serious_words[
                        word] += WRONG_CLASSIFIED_INCREMENT * false_positive_number / false_negative_number
                except KeyError:
                    pass
        for app in self.__training_apps_classification_distribution['TP']:
            desc = app[0].split()
            for word in desc:
                try:
                    self.__serious_words[word] += TRUE_CLASSIFIED_INCREMENT
                except KeyError:
                    pass
        for app in self.__training_apps_classification_distribution['TN']:
            desc = app[0].split()
            for word in desc:
                try:
                    self.__non_serious_words[word] += TRUE_CLASSIFIED_INCREMENT
                except KeyError:
                    pass
        self.__create_global_vocabulary()

    def __has_better_performances(self):
        """
        Method compares the performance of the model at a given time with the best result overall.
        :return: True if model improved the performance, False otherwise.
        """
        return self.__performance.f1 > self.__best_performance.f1

    def classify_app(self, description):
        """
        Considering the description of the application calculates the probability of app being a serious game or not.
        :param description: a string containing all description of the application to classify
        :return: Dictionary containing the probabilities for the application of belonging to respective class.
        """
        serious_probability = self.__prior_probabilities['serious']
        non_serious_probability = self.__prior_probabilities['non-serious']
        description = description.split()
        for word in description:
            serious_probability += self.__serious_likelihoods.get(word, 0)
            non_serious_probability += self.__non_serious_likelihoods.get(word, 0)
        return {'serious': serious_probability, 'non-serious': non_serious_probability}
