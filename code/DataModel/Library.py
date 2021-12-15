from DataManagers.DatabaseManager import do_query, do_multiple_queries, clear_table
from DataModel.Author import Author
from DataModel.GoogleScholarAuthor import GoogleScholarAuthor


class Library:
    def __init__(self):
        self.publications = []
        self.authors = []

    def add_publication(self, publication):
        for pub in self.publications:
            if pub.title == publication.title and pub.abstract == publication.abstract:
                return pub
            elif pub.title == publication.title:
                publication.abstract = publication.abstract + '\n' + pub.abstract
                for author in publication.authors:
                    pub.authors.append(author)
                return pub
        self.publications.append(publication)
        return publication

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

    def persist_data(self):
        self.persist_publications()
        self.persist_authors()

    def persist_publications(self):
        clear_table('paper')
        clear_table('app_paper')
        for publication in self.publications:
            query_par_dict = {'START TRANSACTION': '',
                              'INSERT IGNORE INTO paper(paper_title, abstract, journal, nature_type) '
                              'VALUES (%s, %s, %s, %s)': (
                                  publication.title, publication.abstract,
                                  publication.journal, publication.nature_type),
                              'SELECT LAST_INSERT_ID()': '', 'COMMIT': ''}

            results = do_multiple_queries(query_par_dict)
            sql_pub_id = results.get('SELECT LAST_INSERT_ID()')[0][0]
            publication.id = sql_pub_id

            for application in publication.cited_apps:
                query = 'INSERT IGNORE INTO app_paper(paper_id, app_id) VALUES (%s, %s)'
                do_query((sql_pub_id, application.app_id), query)

    def persist_authors(self):
        clear_table('author')
        clear_table('author_paper')
        for author in self.authors:
            query_par_dict = {'START TRANSACTION': '',
                              'INSERT IGNORE INTO author(name, surname, papers) VALUES (%s, %s, %s)': (
                                  author.name, author.surname, author.n_published_papers),
                              'SELECT LAST_INSERT_ID()': '', 'COMMIT': ''}
            results = do_multiple_queries(query_par_dict)
            sql_auth_id = int(results.get('SELECT LAST_INSERT_ID()')[0][0])

            publications = author.publications
            for publication in publications:
                publication_id = publication.id
                query = 'INSERT IGNORE INTO author_paper(author_id, paper_id) VALUES (%s, %s)'
                do_query((sql_auth_id, publication_id), query)
