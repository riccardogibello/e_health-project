from bs4 import BeautifulSoup
from pymed import PubMed
from Application import Application
from DataManagers.DatabaseManager import do_query
from Utilities.Scrapers.Scraper import Scraper, format_query
from WEBFunctions.web_mining_functions import find_web_page

mesh_terms = ['Child', 'Video Games', 'Models, Educational']


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
              + '&usehistory=y'
        url = format_query(url)
        page = find_web_page(url)
        soup = BeautifulSoup(page, 'lxml')
        xml_result = soup.find('idlist')
        for el in xml_result:
            if el == '\n':
                continue
            total = total + 1
    return total


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

    # Generate list of dict records which will hold all article details that could be fetch from PUBMED API
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


class PubMedScraper(Scraper):

    def __init__(self, library):
        super().__init__(library)
        self.find_apps_evidence()

    def find_apps_evidence(self):
        """
        This methods searches for publications on PubMed which contain as occurrence the name of the application.
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
