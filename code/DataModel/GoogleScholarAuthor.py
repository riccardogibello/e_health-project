from bs4 import BeautifulSoup

from DataModel.Author import Author
from DataModel.Publication import Publication
from WEBFunctions.web_mining_functions import find_web_page


class GoogleScholarAuthor(Author):
    author_link_2_pubs = ''

    def __init__(self, author_name, author_surname, author_link_2_pubs):
        super().__init__(author_name, author_surname)
        self.author_link_2_pubs = author_link_2_pubs
        self.retrieve_publications()

    def retrieve_publications(self):
        query = 'https://scholar.google.it/' + self.author_link_2_pubs + '&view_op=list_works&sortby=pubdate'
        page = find_web_page(query)

        soup = BeautifulSoup(page, 'html.parser')
        publications = soup.find_all(class_="gsc_a_t")

        for publication_tag in publications:
            for el in publication_tag:
                if el.name == 'a':
                    pub_link = 'https://scholar.google.it/' + el.attrs.get('href')
                    title = el.text

                    abstract_page = find_web_page(pub_link)
                    soup = BeautifulSoup(abstract_page, 'html.parser')
                    abstract_tag = soup.find(class_="gsh_csp")
                    if not abstract_tag:
                        continue
                    abstract = abstract_tag.text

                    publication = Publication(title, abstract, [self])
                    self.publications.append(publication)


