import math
import os.path
import re
import numpy as np
from DataManagers.words_mining_functions import sanitize_and_tokenize, count_occurrences
from Utilities.Classifiers.PaperClassifiers.PaperClassifier import PaperClassifier, classify_serious_games_papers

URL_PATTERN = r'[A-Za-z0-9]+://[A-Za-z0-9%-_]+(/[A-Za-z0-9%-_])*(#|\\?)[A-Za-z0-9%-_&=]*'


def remove_urls(text: str):
    return re.sub(URL_PATTERN, '', text)


def sanitize_text(text: str, lower: bool = True, url: bool = True):
    text = text.lower() if lower else text
    text = remove_urls(text) if url else text
    text = re.sub(r'[^A-Za-z -]', ' ', text)
    return re.sub(r'[\s]+', ' ', text).strip()


def compute_total_occurrences(occurrence_list):
    total = 0
    for occurrence in occurrence_list:
        total = total + occurrence
    return total


class NBayesPaperClassifier(PaperClassifier):
    """
    This is the last and adopted version of the Paper Classifier. This class adapts the Naive Bayes Text Classifier
    to the given problem. In particular, it retrieves a large set of papers related to general medicine from PubMed
    and splits them into a train and test set.
    In this way, the train set is used to create a vocabulary of words and, for each word, it is computed the number
    of occurrences that word has for a specific study type. Then the likelihoods and the priors can be calculated
    and the model is tested on an unseen set of papers (with a gold-standard label given by PubMed and used to evaluate
    the classifying performances of the model.
    Lastly it also classifies all the serious games related papers stored in the 'paper' table.
    """
    def __init__(self, recompute):
        self.prior_probabilities = {}  # { study_type : log_probability }}
        self.likelihoods = {}  # { study_type : { word : loglikelihood }}
        self.array_predicted_labels = []
        self.array_true_labels = []
        if recompute:
            super().__init__()
            self.studytype__word_occurrence_dictionary__dictionary = {}
            self.compute_words_per_studytype()
            self.compute_prior_probabilities()
            self.compute_likelihoods()
            self.save_model()
            self.test_model_()
        else:
            self.load_model()
        self.classify_serious_games_papers_()

    def save_model(self):
        if not os.path.exists('./data/models'):
            os.makedirs('./data/models')
        if not os.path.exists('./data/models/NBayesPaperClassifier'):
            os.makedirs('./data/models/NBayesPaperClassifier')
        if not os.path.exists('./data/models/NBayesPaperClassifier/likelihoods'):
            os.makedirs('./data/models/NBayesPaperClassifier/likelihoods')
        if not os.path.exists('./data/models/NBayesPaperClassifier/prior_probabilities'):
            os.makedirs('data/models/NBayesPaperClassifier/prior_probabilities')

        for study_type in self.prior_probabilities.keys():
            f_out = open('./data/models/NBayesPaperClassifier/prior_probabilities/' + study_type + '.txt', 'w')
            f_out.write(str(self.prior_probabilities.get(study_type)))

            f_out = open('./data/models/NBayesPaperClassifier/likelihoods/' + study_type + '.txt', 'w')
            sorted_dictionary = dict(sorted(self.likelihoods.get(study_type).items(), key=lambda x: x[1], reverse=True))
            for word in sorted_dictionary.keys():
                f_out.write(word + ',' + str(sorted_dictionary.get(word)) + '\n')

    def load_model(self):
        for study_type in self.study_type_correspondence.keys():
            f_in = open('./data/models/NBayesPaperClassifier/prior_probabilities/' + study_type + '.txt', 'r')
            lines = f_in.readlines()
            for line in lines:
                self.prior_probabilities.__setitem__(study_type, float(line))

            f_in = open('./data/models/NBayesPaperClassifier/likelihoods/' + study_type + '.txt', 'r')
            lines = f_in.readlines()
            word_likelihood_dict = {}
            for line in lines:
                splitted_line = line.split(',')
                word = str(splitted_line[0])
                loglikelihood = float(splitted_line[1])
                word_likelihood_dict.__setitem__(word, loglikelihood)

            self.likelihoods.__setitem__(study_type, word_likelihood_dict)

    def compute_words_per_studytype(self):
        for study_type in self.studytype_paperlist_dictionary.keys():
            paper_text_list = self.studytype_paperlist_dictionary.get(study_type)
            word_occurrences_dictionary = {}
            # this is a dictionary containing as keys the study type and as value a dictionary.
            # This dictionary contains as key the words found in the related papers and as value the related occurrence
            for text in paper_text_list:
                word_list = sanitize_text(text, True, True)
                word_list = sanitize_and_tokenize(text=word_list, max_n_gram=1)
                word_list_occurrences = count_occurrences(word_list)
                for word in word_list_occurrences.keys():
                    occurrences = word_list_occurrences.get(word)
                    if word not in word_occurrences_dictionary.keys():
                        word_occurrences_dictionary.__setitem__(word, occurrences)
                    else:
                        prev_occurrences = word_occurrences_dictionary.get(word)
                        word_occurrences_dictionary.__setitem__(word, prev_occurrences + occurrences)
            self.studytype__word_occurrence_dictionary__dictionary.__setitem__(study_type, word_occurrences_dictionary)

    def compute_prior_probabilities(self):
        total_n_papers = 0
        for study_type in self.studytype_paperlist_dictionary.keys():
            paper_list = self.studytype_paperlist_dictionary.get(study_type)
            total_n_papers = total_n_papers + len(paper_list)
        for study_type in self.studytype_paperlist_dictionary.keys():
            paper_list = self.studytype_paperlist_dictionary.get(study_type)
            n_papers = len(paper_list)
            self.prior_probabilities.__setitem__(study_type, math.log(n_papers * 1.0 / total_n_papers, 2))

    def compute_likelihoods(self):
        # firstly initialize for each study type an empty dictionary, which will contain the correspondence btw
        # each word of the entire vocabulary and the related likelihood to appear in the text of that study type
        for study_type in self.studytype__word_occurrence_dictionary__dictionary.keys():
            self.likelihoods.__setitem__(study_type, {})

        vocabulary_set = set()
        # let's first create a vocabulary of all the words present in all the types of studies
        for study_type in self.studytype__word_occurrence_dictionary__dictionary.keys():
            word_occurrence_dictionary = self.studytype__word_occurrence_dictionary__dictionary.get(study_type)
            vocabulary_set = set.union(vocabulary_set, word_occurrence_dictionary.keys())

        vocabulary_size = len(vocabulary_set)  # this is the size of the whole vocabulary
        # (without duplicated of the words)

        # then we can compute the likelihood for each word in each of the study types
        for study_type in self.studytype__word_occurrence_dictionary__dictionary.keys():
            likelihoods = self.likelihoods.get(study_type)
            word_occurrence_dictionary = self.studytype__word_occurrence_dictionary__dictionary.get(study_type)
            study_type_dictionary_size = compute_total_occurrences(word_occurrence_dictionary.values())
            for word in vocabulary_set:
                word_occurrences_given_studytype = word_occurrence_dictionary.get(word)
                if word_occurrences_given_studytype:
                    likelihood = (word_occurrences_given_studytype + 1) / (study_type_dictionary_size + vocabulary_size)
                else:
                    likelihood = 1 / (study_type_dictionary_size + vocabulary_size)
                log_likelihood = math.log(likelihood, 2)
                likelihoods.__setitem__(word, log_likelihood)

            self.likelihoods.__setitem__(study_type, likelihoods)

    def classify_paper(self, publication):
        study_type_array = []
        probabilities_array = []
        for study_type in self.study_type_correspondence.keys():
            # for each type of publication, compute the total count of
            # the occurrences of the words given in the vocabularies
            study_type_array.append(study_type)

            title = publication.title

            title_words = set(sanitize_and_tokenize(text=title, max_n_gram=1))
            words = title_words
            probability = self.prior_probabilities.get(study_type)
            word_likelihood_dict = self.likelihoods.get(study_type)
            for word in words:
                word_likelihood = word_likelihood_dict.get(word)
                if not word_likelihood:
                    continue
                probability = probability + word_likelihood

            probabilities_array.append(probability)

        # find the class with the maximum number of occurrences of the words in the given publication abstract and title
        probabilities_array = np.array(probabilities_array)
        index_max = np.argmax(probabilities_array)
        assert (len(probabilities_array) == len(study_type_array))

        return study_type_array[index_max]  # this returns a string with the name of the predicted class

    def test_model_(self):
        super().test_model(classification_function=self.classify_paper,
                           path_for_confusion_matrix='./data/output_data/NBayesConfusionMatrix.png',
                           metrics_path='./data/output_data/NBayesMetrics.png')

    def classify_serious_games_papers_(self):
        classify_serious_games_papers(classification_function=self.classify_paper)
