import numpy
from bs4 import BeautifulSoup

from DataManagers.DatabaseManager import do_query, clear_table
from Utilities.Scrapers.Scraper import format_query
from WEBFunctions.web_mining_functions import find_web_page
import random
from descriptions_sanitizer import sanitize_string


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
        else:
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=' + str(
                id_.text) + '&retmode=xml'
            page = find_web_page(url)
            soup = BeautifulSoup(page, 'lxml')
            xml_result = soup.find('articletitle')

            for el in xml_result:
                if el == '\n':
                    continue
                paper_text = paper_text + el.text

            paper_text = paper_text + '\n'

            xml_result = soup.findAll('abstracttext')
            for el in xml_result:
                if el == '\n':
                    continue
                paper_text = paper_text + el.text
        if not paper_text == '':
            papers.append(paper_text)
    return papers


class PaperClassifier:
    study_type_correspondence = {'CaseControl': 0, 'CohortStudy': 1, 'MetaAnalysis': 2, 'ObservationalStudy': 3,
                                 'RCT': 4, 'SystematicReview': 5}

    def __init__(self):
        self.studytype_paperlist_dictionary = {}
        self.retrieve_papers()
        self.split_train_test_papers(test_percentage=0.2)

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
