from Utilities.Scrapers.PubMedScraper import find_author_n_publications


class Author:
    name = ''
    surname = ''
    publications = []
    n_published_papers = 0

    def __init__(self, author_name, author_surname):
        if author_name:
            self.name = str(author_name.encode('ascii', errors='ignore').decode())
        if author_surname:
            self.surname = str(author_surname.encode('ascii', errors='ignore').decode())
        self.n_published_papers = find_author_n_publications(self)
