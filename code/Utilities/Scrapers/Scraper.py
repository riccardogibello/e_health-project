import re
from DataManagers.DatabaseManager import do_query
from DataModel.PubMedPublication import PubMedPublication
from DataModel.Publication import Publication
from descriptions_sanitizer import sanitize_string


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
        cited_apps = {}

        for result in results:
            app_id = result[0]
            app_name = result[1]

            for publication in publications:
                title = publication.title
                abstract = publication.abstract

                if app_name in title or app_name in abstract:
                    cited_apps.__setitem__(app_id, app_name)
        return cited_apps

    def create_publication(self, title, abstract, authors):
        title = sanitize_string(title)
        title = re.sub(r'"+', "", title)
        publication = Publication(title, abstract, authors)
        self.library.add_publication(publication)

    def create_pubmed_publication(self, title, abstract, authors, pubmed_id):
        title = sanitize_string(title)
        title = re.sub(r'"+', "", title)
        publication = PubMedPublication(title, abstract, authors, pubmed_id)
        publication = self.library.add_publication(publication)
        return publication
