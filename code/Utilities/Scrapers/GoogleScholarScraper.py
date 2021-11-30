import re
from bs4 import BeautifulSoup
from DataModel.Publication import Publication
from Scraper import Scraper, format_query
from WEBFunctions.web_mining_functions import find_web_page, find_text_from_web_page
from descriptions_sanitizer import sanitize_string


class GoogleScholarScraper(Scraper):
    def __init__(self, library):
        super().__init__(library)
        self.find_serious_games_papers()
        self.find_cited_apps()

    def find_serious_games_papers(self):
        keywords_list = ['serious games children', 'gamification children applications', 'mobile children applications']

        for keywords in keywords_list:
            for i in range(5):
                keywords = format_query(keywords)
                query = 'https://scholar.google.it/scholar?as_vis=1&q=' + keywords + '&hl=en&start=' + str(i * 10)
                page = find_web_page(query)

                self.find_information(page)
        print('ended')

    def find_information(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        publications = soup.find_all(class_="gs_rt")
        authors = soup.find_all(class_="gs_a")

        if not publications or not authors:
            return

        for i in range(max(len(publications) - 1, len(authors) - 1)):
            publication = publications[i]
            pub_authors = authors[i]

            pub_authors = self.find_authors(pub_authors)
            self.find_publication(publication, pub_authors)

    def find_authors(self, tags):
        authors = []
        for tag in tags:
            if tag.name == 'a':
                author_link = tag.attrs.get('href')
                author_name = tag.text
                author = self.library.find_googlescholar_author(author_name, author_link)
                authors.append(author)
        return authors

    def find_publication(self, tag, authors):
        title = ''
        link = ''
        for el in tag:
            if el.name == 'a':
                link = el.attrs.get('href')
                title = el.text

        if not link or '.pdf' in link or 'https://books.google.it/books?' in link:
            return -1
        else:
            text_content = find_text_from_web_page(link)

        text_content = sanitize_string(text_content)
        text_content = text_content.lower()
        abstract_position = text_content.find('abstract')
        if abstract_position == -1:
            return -1

        abstract_position = 0
        matches = []
        while abstract_position < len(text_content):
            abstract_position = text_content.find('abstract', abstract_position)
            if abstract_position == -1:
                break
            matches.append(text_content[abstract_position:abstract_position + 1000:1])
            abstract_position += 8  # +2 because len('ll') == 2

        title = sanitize_string(title)
        title = re.sub(r'"+', "", title)

        abstract = ''
        for match in matches:
            abstract = abstract + str(match)
        publication = Publication(title, abstract, authors)

        self.library.add_publication(publication)
