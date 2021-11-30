from Utilities.Scrapers.PubMedScraper import find_author_n_publications


class Author:
    name = ''
    surname = ''
    publications = []
    n_published_papers = 0

    def __init__(self, author_name, author_surname):
        self.name = author_name
        self.surname = author_surname
        self.n_published_papers = find_author_n_publications(self)
