import math
import os.path
import re
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from DataManagers.DatabaseManager import do_query
from DataManagers.WordsMiner import sanitize_and_tokenize, count_occurrences
from DataModel.Publication import Publication
from Utilities.Classifiers.PaperClassifiers.PaperClassifier import PaperClassifier
from Utilities.ConfusionMatrixPrinter import save_confusion_matrix
import dataframe_image as dfi

URL_PATTERN = r'[A-Za-z0-9]+://[A-Za-z0-9%-_]+(/[A-Za-z0-9%-_])*(#|\\?)[A-Za-z0-9%-_&=]*'


def remove_urls(text: str):
    return re.sub(URL_PATTERN, '', text)


def sanitize_text(text: str, lower: bool = True, url: bool = True):
    text = text.lower() if lower else text
    text = remove_urls(text) if url else text
    text = re.sub(r'[^A-Za-z -]', ' ', text)
    return re.sub(r'[\s]+', ' ', text).strip()


def format_label(label):
    list_ = re.findall('[A-Z][^A-Z]*', label)  # this regex matches every capital letter
    # followed by a series of lower-case letters
    study_type = label
    if len(list_) != len(label):
        study_type = ''
        for sub_word in list_:
            study_type = study_type + sub_word + '\n'
        study_type = study_type[:-1]
    return study_type


def compute_total_occurrences(occurrence_list):
    total = 0
    for occurrence in occurrence_list:
        total = total + occurrence
    return total


def print_metrics(results, labels):
    # results = ([precision], [recall], [f1])
    study_type_list = []
    results_dictionary = {'precision': [], 'recall': [], 'f1': []}
    index = 0
    for label in labels:
        study_type_list.append(label)
        precision_list = results_dictionary.get('precision')
        recall_list = results_dictionary.get('recall')
        f1_list = results_dictionary.get('f1')
        precision = results[0][index]
        precision_list.append(precision)
        recall = results[1][index]
        recall_list.append(recall)
        f1 = results[2][index]
        f1_list.append(f1)

        results_dictionary = {'precision': precision_list,
                              'recall': recall_list,
                              'f1': f1_list}

        index = index + 1
    dataframe = DataFrame(results_dictionary, index=study_type_list)
    dataframe = dataframe.style.set_properties(**{'background-color': 'black',
                                                  'color': 'green'})

    dfi.export(dataframe, './data/output_data/resu.png')

    print(results_dictionary)


class NBayesPaperClassifier(PaperClassifier):
    def __init__(self, recompute):
        super().__init__()
        self.prior_probabilities = {}  # { study_type : log_probability }}
        self.likelihoods = {}  # { study_type : { word : loglikelihood }}
        if recompute:
            self.studytype__word_occurrence_dictionary__dictionary = {}
            self.compute_words_per_studytype()
            self.compute_prior_probabilities()
            self.compute_likelihoods()
            self.save_model()
        else:
            self.load_model()
        self.array_predicted_labels = []
        self.array_true_labels = []
        self.test_model()

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
        for study_type in self.studytype_paperlist_dictionary.keys():
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
        for study_type in self.studytype_paperlist_dictionary.keys():
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

    def test_model(self):
        query = 'SELECT paper_id, text, true_type FROM test_paper'
        results = do_query('', query)
        for result in results:
            paper_id = result[0]
            text = result[1]
            true_type = int(result[2])
            true_study_type = self.retrieve_study_type_string_from_int(true_type)
            predicted_study_type = self.classify_paper(Publication(title=text, abstract='', authors=''))
            predicted_study_type_int = self.study_type_correspondence.get(predicted_study_type)

            query = 'UPDATE test_paper SET predicted_type = %s WHERE paper_id = %s'
            do_query((predicted_study_type_int, paper_id), query)

            predicted_study_type = format_label(predicted_study_type)
            true_study_type = format_label(true_study_type)
            self.array_predicted_labels.append(predicted_study_type)
            self.array_true_labels.append(true_study_type)

        self.print_confusion_matrix()

    def print_confusion_matrix(self):
        indexes = self.compute_scatter_matrix_indexes()
        columns = indexes
        cm = confusion_matrix(y_true=self.array_true_labels, y_pred=self.array_predicted_labels, labels=indexes)
        cm_df = pd.DataFrame(cm,
                             index=indexes,
                             columns=columns)

        save_confusion_matrix(fig_width=8, fig_height=6, heatmap_width=5, heatmap_height=3,
                              confusion_matrix_dataframe=cm_df, path='./data/output_data/test.png')

        labels = self.studytype_paperlist_dictionary.keys()
        results = precision_recall_fscore_support(y_true=self.array_true_labels, y_pred=self.array_predicted_labels)
        print_metrics(results, labels)

    def compute_scatter_matrix_indexes(self):
        indexes = []
        for study_type in self.study_type_correspondence.keys():
            study_type = format_label(study_type)
            indexes.append(study_type)
        return indexes
