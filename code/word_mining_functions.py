import io
import re
import time
import urllib.request
from urllib.request import Request

from bs4 import BeautifulSoup
from nltk import word_tokenize
import PyPDF2


def find_serious_games_words(filename, path):
    if '.pdf' in path:
        text = find_pdf_from_web(path)
    else:
        text = find_text_from_web(path)
    text = re.sub("[\n]+", "\n", text)
    tokenized_text = word_tokenize(text, language='english')

    punctuations = '''`=|0123456789!()[]{};:'",<>./?@#$%^&*_~'''
    tokenized_text_without_punc = []
    for string in tokenized_text:
        string = string.encode('utf8').decode('ascii', 'ignore')
        no_punct = ""
        for char in string:
            if char not in punctuations:
                no_punct = no_punct + char
        if no_punct == '' or no_punct == '-':
            continue
        tokenized_text_without_punc.append(no_punct)
    words = []
    for w in tokenized_text_without_punc:
        words.append(w.lower())
    words.sort()
    occurrence_word_dictionary = count_occurrences(words)
    occurrences = sorted(occurrence_word_dictionary)
    new_occurrences_oreded = {}
    for occurrence in occurrences:
        new_occurrences_oreded.__setitem__(occurrence, occurrence_word_dictionary.get(occurrence))

    fp = open('./data/output_data/' + filename + '.txt', 'w')
    for occ, words in new_occurrences_oreded.items():
        for word in words:
            fp.write(str(occ) + '     ' + word + '\n')


def find_text_from_web(path):
    wiki_html_page = urllib.request.urlopen(path).read()
    soup = BeautifulSoup(wiki_html_page, 'html.parser')
    return soup.get_text()


def find_pdf_from_web(path):
    req = Request(path, headers={'User-Agent': 'Mozilla/5.0'})
    wiki_html_page = io.BytesIO(urllib.request.urlopen(req).read())
    time.sleep(3)
    filereader = PyPDF2.PdfFileReader(wiki_html_page)
    n_pages = filereader.numPages
    text = ''
    i = 0
    while i < n_pages:
        text = text + filereader.getPage(i).extractText()
        i = i + 1
    return text


def count_occurrences(words):
    occurrences = {}
    i = 0
    for word in words:
        count = 1
        remaining_list = words[1:]
        for other_word in remaining_list:
            if other_word == word:
                count = count + 1
        previous_words = occurrences.get(count)
        if not previous_words:
            occurrences.__setitem__(count, [word])
        else:
            previous_words.append(word)
            occurrences.__setitem__(count, previous_words)
        while word in words:
            words.remove(word)
        i = i + 1

    return occurrences
