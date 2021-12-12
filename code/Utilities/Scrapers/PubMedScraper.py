from bs4 import BeautifulSoup
from pymed import PubMed
from DataManagers.WordsMiner import sanitize_and_tokenize, count_occurrences
from DataModel.Application import Application
from DataManagers.DatabaseManager import do_query, clear_table
from Utilities.Classifiers.PaperClassifiers.NBayesPaperClassifier import sanitize_text
from Utilities.Classifiers.PaperClassifiers.PaperClassifier import find_papers
from Utilities.Scrapers.Scraper import Scraper, format_query
from WEBFunctions.web_mining_functions import find_web_page

mesh_terms = ['Video Games']  # TODO : , 'Child', 'Models, Educational']

queries = ['((serious games) AND (Video Games[MeSH Major Topic])) AND (Child[MeSH Terms])',
           '(serious games) AND (Video Games[MeSH Major Topic])']


def find_author_n_publications(author):
    """
    This method find, given an author, all the publications related to this author and to any of the
    mesh terms reported above the method (mesh terms are a sort of tag used to index the papers on PubMed).
    """
    total = 0
    query = '(' + author.name + ' ' + author.surname + '[Author])'
    for mesh_term in mesh_terms:
        query = '(' + query + ' AND (' + mesh_term + '[MeSH Major Topic]))'
        # TODO : very unlikely that some results will be found with this further constraint given by MESH tokens
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' + query \
              + '&sort=date'
        # TODO : in previous query &sort=date set in place of &usehistory=y

        url = format_query(url)
        page = find_web_page(url)
        soup = BeautifulSoup(page, 'lxml')
        xml_result = soup.find('idlist')
        if not xml_result:
            continue
        for el in xml_result:
            if el == '\n':
                continue
            total = total + 1
    return total


def find_papers_keywords(papers):
    list_ = []

    for paper_text in papers:
        word_list = sanitize_and_tokenize(text=paper_text, max_n_gram=3)
        word_occurrence__dictionary = count_occurrences(word_list)
        list_.append(word_occurrence__dictionary)

    return list_  # a list of { word : occurrence }


def find_app_related_papers(app_name):
    """
    This method finds all the papers which cite the name of the app.
    """
    pubmed = PubMed(tool='ehealth_group07', email='riccardo.gibello@mail.polimi.it')
    results = pubmed.query(app_name, max_results=100)

    article_list = []
    article_info = []

    for article in results:
        # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
        # We need to convert it to dictionary with available function
        article_dict = article.toDict()
        article_list.append(article_dict)

    # Generate list of dict records which will hold all article details that could be fetched from PUBMED API
    for article in article_list:
        # Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId in that list -
        # that's article pubmedId
        pubmed_id = article['pubmed_id'].partition('\n')[0]
        # Append article info to dictionary
        article_info.append({u'pubmed_id': pubmed_id,
                             u'title': article['title'],
                             u'keywords': article['keywords'],
                             u'journal': article['journal'],
                             u'abstract': article['abstract'],
                             u'conclusions': article['conclusions'],
                             u'methods': article['methods'],
                             u'results': article['results'],
                             u'copyrights': article['copyrights'],
                             u'doi': article['doi'],
                             u'publication_date': article['publication_date'],
                             u'authors': article['authors']})

    return article_info


def aggregate_occurrences(list_dict_of_occurrences):
    word_occurrence__aggregated_dictionary = {}
    for word_occurrence_dictionary in list_dict_of_occurrences:
        for word in word_occurrence_dictionary.keys():
            prev_occurrences = word_occurrence__aggregated_dictionary.get(word)
            curr_occurrences = word_occurrence_dictionary.get(word)
            if not prev_occurrences:
                word_occurrence__aggregated_dictionary.__setitem__(word, curr_occurrences)
            else:
                word_occurrence__aggregated_dictionary.__setitem__(word, prev_occurrences + curr_occurrences)

    sorted_dict = dict(sorted(word_occurrence__aggregated_dictionary.items(), key=lambda x: x[1], reverse=True))
    return sorted_dict


def find_key_words_for_serious_games():
    for query in queries:
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' + query \
              + '&sort=date&RetMax=9000'

        url = format_query(url)
        page = find_web_page(url)
        soup = BeautifulSoup(page, 'lxml')
        xml_result = soup.find('idlist')
        if not xml_result:
            continue
        id_list = []
        for el in xml_result:
            if el == '\n':
                continue
            id_list.append(el)

        papers = find_papers(id_list=id_list, is_from_pubmed_site=False)

        list_dict_of_occurrences = find_papers_keywords(papers)
        word_occurrence__dictionary = aggregate_occurrences(list_dict_of_occurrences)
        general_word_occurrence__dictionary = compute_general_keywords_medical_field()
        # this is used in order to filter all general keywords that can be found in any kind of paper
        cnt = 0
        for word in word_occurrence__dictionary.keys():
            if word not in general_word_occurrence__dictionary.keys():
                occurrences = word_occurrence__dictionary.get(word)
                query = 'INSERT INTO keyword(keyword, occurrences) VALUES (%s, %s)'
                do_query((word, occurrences), query)
                cnt = cnt + 1
        print(cnt)


def compute_general_keywords_medical_field():
    query = 'SELECT text FROM test_paper'
    results = do_query((), query)
    papers = []

    for result in results:
        text = result[0]
        papers.append(text)

    list_ = find_papers_keywords(papers)
    return aggregate_occurrences(list_)


class PubMedScraper(Scraper):

    def __init__(self, library):
        super().__init__(library)
        clear_table('keyword')
        find_key_words_for_serious_games()
        # TODO : the following has been commented because actually does not find anything meaningful
        # self.find_apps_evidence()

    def find_apps_evidence(self):
        """
        This method searches for publications on PubMed which contain as occurrence the name of the application.
        Given an application, if some papers are found, for each the id, title, abstract and authors are extracted.
        Then, each author is retrieved (and in case created) from the library. At the end a new publication instance
        is created and added to the library (if not already created). Lastly, the application instance,
        which is cited into the paper, is added to the cited_apps list into the related publication instance.
        """
        query = 'SELECT app_id, app_name FROM selected_app'
        app_name_list = do_query('', query)

        for app_name_sublist in app_name_list:
            app_id = app_name_sublist[0]
            app_name = app_name_sublist[1]
            application = Application(app_id, False)
            papers = find_app_related_papers(
                app_name)  # list of dictionaries, each one containing the information about a paper

            if len(papers):
                for paper in papers:
                    paper_pubmed__id = paper.get('pubmed_id')
                    paper_title = paper.get('title')
                    paper_abstract = paper.get('abstract')
                    if not paper_abstract:
                        continue
                    authors = paper.get('authors')  # this returns a list of dictionaries, each one having
                    # as keys 'lastname', 'firstname', 'initials', 'affiliation'
                    new_authors = []
                    for author in authors:
                        author = self.library.find_generic_author(author['firstname'], author['lastname'])
                        new_authors.append(author)

                    publication = self.create_pubmed_publication(paper_title, paper_abstract, authors, paper_pubmed__id)
                    publication.add_cited_app(application)

        self.library.persist_data()
