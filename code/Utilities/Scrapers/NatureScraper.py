import requests
from Utilities.Scrapers.Scraper import Scraper


def format_query(query):
    return query.replace(' ', '%20')


class NatureScraper(Scraper):
    """
    This class is a scraping class intended to retrieve publications data from Nature starting from general keywords
    such as 'serious games children'. In this way the publication data and the related authors' data are retrieved
    and stored in the database. Finally, this set of papers is searched for citations of the names of the applications
    selected as serious games.
    """
    def __init__(self, library):
        super().__init__(library)
        self.find_serious_games_papers()
        self.find_cited_apps()

    def find_serious_games_papers(self):
        keywords_list = [
            'serious games children']  # other keywords could have been
        # 'gamification children applications', 'mobile children applications'
        page_length = 50
        start = 1

        for keywords in keywords_list:
            query = 'http://api.springernature.com/metadata/json?q=keyword:' + keywords \
                    + ' sort:date language:en&s=' + str(start) + '&p=' + str(page_length) + \
                    '&api_key=c36e401a220b60a51c236d8924aecb10'
            query = format_query(query)
            json_result = requests.get(query).json()

            result = json_result['result'][0]
            self.find_information(json_result)
            total = int(result['total'])

            while start <= total:
                start = start + page_length
                query = 'http://api.springernature.com/metadata/json?q=keyword:' + keywords \
                        + ' sort:date language:en&s=' + str(start) + '&p=' + \
                        str(page_length) + '&api_key=c36e401a220b60a51c236d8924aecb10'
                query = format_query(query)
                json_result = requests.get(query).json()

                self.find_information(json_result)

        self.library.persist_data()

    def find_information(self, json_result):
        publications = json_result['records']

        if not publications:
            return

        for i in range(len(publications) - 1):
            publication_dictionary = publications[i]  # dictionary
            language = publication_dictionary['language']
            if not language == 'en':
                continue

            creator_list = publication_dictionary['creators']  # list of dictionaries, each with one key ('creator')
            authors = self.find_authors(
                creator_list)  # this returns a list of authors (found or created) from the library

            title = publication_dictionary['title']
            abstract = publication_dictionary['abstract']
            journal = publication_dictionary['publicationName']
            nature_type = publication_dictionary['publicationType']
            self.create_publication(title, abstract, authors, journal, nature_type)

    def find_authors(self, author_list):
        authors = []
        for author_dict in author_list:
            author_string = author_dict['creator']  # this is a string formatted as SURNAME,NAME
            author_string_split = author_string.split(sep=',', maxsplit=1)
            if len(author_string_split) < 2:
                continue
            name = author_string_split[1]
            surname = author_string_split[0]
            author = self.library.find_generic_author(name, surname)
            authors.append(author)
        return authors
