import re

import numpy
import pandas as pd
from bs4 import BeautifulSoup
import langid
from pandas import DataFrame
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
import dataframe_image as dfi
from DataManagers.DatabaseManager import do_query, clear_table
from DataModel.Publication import Publication
from Utilities.ConfusionMatrixPrinter import save_confusion_matrix
from Utilities.Scrapers.Scraper import format_query
from WEBFunctions.web_mining_functions import find_web_page
import random
from descriptions_sanitizer import sanitize_string


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


def print_metrics(results, labels, metrics_path):
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

    dfi.export(dataframe, metrics_path)

    print(results_dictionary)


def find_papers(id_list, is_from_pubmed_site):
    papers = []
    for id_ in id_list:
        paper_text = ''
        if is_from_pubmed_site:
            url = 'https://pubmed.ncbi.nlm.nih.gov/' + str(
                id_.text)
            page = find_web_page(url)
            soup = BeautifulSoup(page, 'html.parser')

            title_tag = soup.find(class_='heading-title')
            if not title_tag:
                continue
            title = sanitize_string(title_tag.text)
            paper_text = paper_text + title + '\n'

            abstract_tag = soup.find(class_='abstract-content selected')
            if not abstract_tag:
                continue
            abstract = sanitize_string(abstract_tag.text)
            paper_text = paper_text + abstract
            if not langid.classify(paper_text)[0] == 'en':
                continue
        else:
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + str(
                id_.text) + '&retmode=xml'
            page = find_web_page(url)
            soup = BeautifulSoup(page, 'lxml')
            xml_result = soup.find('articletitle')
            if not xml_result:
                continue

            for el in xml_result:
                if el == '\n':
                    continue
                paper_text = paper_text + el.text

            paper_text = paper_text + '\n'

            xml_result = soup.findAll('abstracttext')
            if not xml_result:
                continue

            for el in xml_result:
                if el == '\n':
                    continue
                paper_text = paper_text + el.text
            if not langid.classify(paper_text)[0] == 'en':
                continue
        if not paper_text == '':
            papers.append(paper_text)
    return papers


def classify_serious_games_papers(classification_function):
    query = 'SELECT paper_id, paper_title, abstract FROM paper'
    results = do_query('', query)

    for result in results:
        paper_id = result[0]
        title = result[1]
        abstract = result[2]
        text = title + abstract

        predicted_study_type = classification_function(
            Publication(title=text, abstract='', authors='', journal='', nature_type=''))

        query = 'UPDATE paper SET type = %s WHERE paper_id = %s'
        do_query((predicted_study_type, paper_id), query)


class PaperClassifier:
    study_type_correspondence = {'CaseControl': 0, 'CohortStudy': 1, 'MetaAnalysis': 2, 'ObservationalStudy': 3,
                                 'RCT': 4, 'SystematicReview': 5}

    def __init__(self):
        self.studytype_paperlist_dictionary = {}
        # TODO : removed only to run after NBayes with same papers
        '''self.retrieve_papers()
        self.split_train_test_papers(test_percentage=0.2)'''

    def retrieve_papers(self):
        f_in = open('./data/input_data/study_type_mesh_correspondence.txt')
        lines = f_in.readlines()

        for line in lines:
            splitted_line = line.split(',')
            study_type = splitted_line[0]
            query = splitted_line[1]

            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed' + query
            url = format_query(url)
            page = find_web_page(url)
            soup = BeautifulSoup(page, 'lxml')
            xml_result = soup.find('idlist')
            id_list = []
            for el in xml_result:
                if el == '\n':
                    continue
                id_list.append(el)

            if study_type == 'SystematicReview' or study_type == 'ObservationalStudy':
                paper_text_list = find_papers(id_list, True)
            else:
                paper_text_list = find_papers(id_list, False)

            self.studytype_paperlist_dictionary.__setitem__(study_type, paper_text_list)

        self.balance_papers()

    def balance_papers(self):
        min_n_papers = -1
        for study_type in self.studytype_paperlist_dictionary.keys():
            n_papers = len(self.studytype_paperlist_dictionary.get(study_type))
            if min_n_papers < 0:
                min_n_papers = n_papers
            else:
                if n_papers < min_n_papers:
                    min_n_papers = n_papers

        for study_type in self.studytype_paperlist_dictionary.keys():
            paper_list = self.studytype_paperlist_dictionary.get(study_type)
            random.shuffle(paper_list)
            paper_list = paper_list[:min_n_papers]
            self.studytype_paperlist_dictionary.__setitem__(study_type, paper_list)

    def split_train_test_papers(self, test_percentage):
        # firstly clear all previous data already present in the table
        clear_table('test_paper')

        for study_type in self.studytype_paperlist_dictionary.keys():
            papers = self.studytype_paperlist_dictionary.get(study_type)
            papers = numpy.array(papers)
            numpy.random.shuffle(papers)

            for i in range(int(len(papers) * test_percentage)):
                paper = str(papers[i])
                papers = numpy.delete(papers, i)
                query = 'INSERT INTO test_paper(text, true_type) VALUES (%s, %s)'
                study_type_int = str(self.study_type_correspondence.get(study_type))
                do_query((paper, study_type_int), query)

            self.studytype_paperlist_dictionary.__setitem__(study_type, papers.tolist())

    def retrieve_study_type_string_from_int(self, value_searched):
        for study_type_string, value in self.study_type_correspondence.items():
            if value == value_searched:
                return study_type_string

    def print_confusion_matrix(self, indexes, columns, y_true, y_pred, path_for_confusion_matrix, metrics_path):
        cm = confusion_matrix(y_true=y_true, y_pred=y_pred, labels=indexes)
        cm_df = pd.DataFrame(cm,
                             index=indexes,
                             columns=columns)

        save_confusion_matrix(fig_width=8, fig_height=6, heatmap_width=5, heatmap_height=3,
                              confusion_matrix_dataframe=cm_df, path=path_for_confusion_matrix)

        labels = self.study_type_correspondence.keys()
        results = precision_recall_fscore_support(y_true=y_true, y_pred=y_pred)
        print_metrics(results, labels, metrics_path)

    def test_model(self, classification_function, path_for_confusion_matrix, metrics_path):
        query = 'SELECT paper_id, text, true_type FROM test_paper'
        results = do_query('', query)
        array_predicted_labels = []
        array_true_labels = []
        for result in results:
            paper_id = result[0]
            text = result[1]
            true_type = int(result[2])
            true_study_type = self.retrieve_study_type_string_from_int(true_type)
            predicted_study_type = classification_function(Publication(title=text, abstract='', authors='',
                                                                       journal='', nature_type=''))
            predicted_study_type_int = self.study_type_correspondence.get(predicted_study_type)

            query = 'UPDATE test_paper SET predicted_type = %s WHERE paper_id = %s'
            do_query((predicted_study_type_int, paper_id), query)

            predicted_study_type = format_label(predicted_study_type)
            true_study_type = format_label(true_study_type)
            array_predicted_labels.append(predicted_study_type)
            array_true_labels.append(true_study_type)

        self.print_confusion_matrix_(array_predicted_labels, array_true_labels, path_for_confusion_matrix, metrics_path)

    def print_confusion_matrix_(self, array_predicted_labels, array_true_labels, path_for_confusion_matrix,
                                metrics_path):
        indexes = self.compute_scatter_matrix_indexes()
        columns = indexes

        self.print_confusion_matrix(indexes=indexes, columns=columns,
                                    y_true=array_true_labels, y_pred=array_predicted_labels,
                                    path_for_confusion_matrix=path_for_confusion_matrix,
                                    metrics_path=metrics_path)

    def compute_scatter_matrix_indexes(self):
        indexes = []
        for study_type in self.study_type_correspondence.keys():
            study_type = format_label(study_type)
            indexes.append(study_type)
        return indexes
