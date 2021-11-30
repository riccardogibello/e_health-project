import http
import urllib
import io
from urllib.request import Request
import PyPDF2
import play_scraper
from bs4 import BeautifulSoup
from DataManagers.DatabaseManager import *


def find_available_categories():
    clear_table('category')
    categories = play_scraper.categories()

    i = 1
    for first_key, category in categories.items():
        data = []
        for second_key, category_datum in category.items():
            if second_key != 'url':
                data.append(category_datum)
        query = (
            "INSERT INTO category(id, category_id)"
            "VALUES (%s, %s)"
        )
        do_query([str(i), category.get('category_id')], query)
        i = i + 1


def find_text_from_web_page(path):
    """
    This method retrieves the page from the specified web URL and parses it, extracting data from a HTML file.
    """
    page = find_web_page(path)
    soup = BeautifulSoup(page, 'html.parser')
    return soup.get_text()


def find_pdf_from_web_page(path):
    """
    This method retrieves the page from the specified web URL and parses it, extracting data from a PDF file.
    """

    page = find_web_page(path)
    filereader = PyPDF2.PdfFileReader(page)
    n_pages = filereader.numPages
    text = ''
    i = 0
    while i < n_pages:
        text = text + filereader.getPage(i).extractText()
        i = i + 1
    return text


def find_web_page(path):
    """
    This method retrieves the page from the specified web URL. It is returned as a stream of bytes that can be read
    by a PDF reader or a HTML parser.
    """
    try:
        req = Request(path, headers={'User-Agent': 'Mozilla/5.0'})
        print('requesting ' + str(path))
        page = io.BytesIO(urllib.request.urlopen(req).read())
    except http.client.RemoteDisconnected:
        return io.BytesIO(urllib.request.urlopen(Request(path, headers={'User-Agent': 'Mozilla/5.0'})).read())
    return page
