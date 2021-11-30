from DataModel.Author import Author
from DataModel.GoogleScholarAuthor import GoogleScholarAuthor


class Library:
    publications = []
    authors = []

    def add_publication(self, publication):
        for pub in self.publications:
            if pub.title == publication.title and pub.abstract == publication.abstract:
                return
            elif pub.title == publication.title:
                publication.abstract = publication.abstract + '\n' + pub.abstract
                for author in publication.authors:
                    pub.authors.append(author)
                return
        self.publications.append(publication)

    def find_googlescholar_author(self, author_name, author_surname, author_link):
        for author in self.authors:
            if author.name == author_name and author.surname == author_surname:
                return author

        author = GoogleScholarAuthor(author_name, author_surname, author_link)
        self.authors.append(author)
        author_publications = author.publications
        for publication in author_publications:
            self.add_publication(publication)

        return author

    def find_generic_author(self, author_name, author_surname):
        for author in self.authors:
            if author.name == author_name and author.surname == author_surname:
                return author

        author = Author(author_name, author_surname)
        self.authors.append(author)

        return author
