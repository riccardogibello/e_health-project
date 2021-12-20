import re
from DataManagers.DatabaseManager import do_query
from DataManagers.words_mining_functions import sanitize_string
from DataModel.PubMedPublication import PubMedPublication
from DataModel.Publication import Publication


def format_query(query):
    return query.replace(' ', '%20')


class Scraper:
    library = ''

    def __init__(self, library):
        self.library = library

    def find_cited_apps(self):
        query = 'SELECT app_id, app_name FROM selected_app'
        results = do_query('', query)

        publications = self.library.publications

        for result in results:
            app_id = result[0]
            app_name = result[1]

            for publication in publications:
                pub_id = publication.id
                title = publication.title
                abstract = publication.abstract

                if app_name in title or app_name in abstract:
                    query = 'INSERT IGNORE INTO app_paper(paper_id, app_id) VALUES (%s, %s)'
                    do_query((pub_id, app_id), query)

    def create_publication(self, title, abstract, authors, journal, nature_type):
        """
        This method creates a new publication (if not already existing) and then adds this publication (if not already
        present) to each author
        """
        title = sanitize_string(title)
        title = re.sub(r'"+', "", title)
        publication = Publication(title, abstract, authors, journal, nature_type)
        self.library.add_publication(publication)
        for author in authors:
            author.add_publication(publication)

    def create_pubmed_publication(self, title, abstract, authors, pubmed_id):
        title = sanitize_string(title)
        title = re.sub(r'"+', "", title)
        publication = PubMedPublication(title, abstract, authors, pubmed_id)
        publication = self.library.add_publication(publication)
        return publication
