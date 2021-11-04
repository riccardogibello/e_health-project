from nltk import WordNetLemmatizer, PunktSentenceTokenizer, WordPunctTokenizer, sent_tokenize
from nltk.corpus import stopwords

from WEBFunctions.web_mining_functions import *


def count_occurrences(words):
    occurrences = {}
    i = 0
    for word in words:
        count = 1
        remaining_list = words[1:]
        for other_word in remaining_list:
            if other_word == word:
                count = count + 1
        occurrences.__setitem__(word, count)
        while word in words:
            words.remove(word)
        i = i + 1

    # the returned dictionary contains an entry for each word found, and the correspondent value is the number of times
    # that word has been found
    # { key = word, value = count }
    return occurrences


def split_text(text):
    # Firstly, divide the whole text into sentences, using punctuation as divider.
    # This tokenizer is more advanced than others, because it is trained on the given text.
    sent_tokenizer = PunktSentenceTokenizer(text)
    sentences = sent_tokenizer.tokenize(text)

    # Secondly, split each sentence into single words.
    word_punctuation_tokenizer = WordPunctTokenizer()
    words = []
    for sentence in sentences:
        constituent_words = word_punctuation_tokenizer.tokenize(sentence)
        for word in constituent_words:
            words.append(word)

    # Lastly, if possible, lemmatize the word given, that is, try to find the root of the word in the WordNet
    # dictionary.
    lemmatizer = WordNetLemmatizer()
    for word in words:
        lemmatized_word = lemmatizer.lemmatize(word)
        if word != lemmatized_word:
            words.remove(word)
            words.append(lemmatized_word)

    return words


def sanitize_text(text):
    text = text.lower()
    new_string = str(text.encode('ascii', errors='ignore').decode())
    new_string = re.sub(r"[ ]+", " ", new_string)
    new_string = re.sub(r"[\b]+", "", new_string)
    new_string = re.sub(r"[\t]+", "", new_string)
    new_string = re.sub(r"[\f]+", "", new_string)
    new_string = re.sub(r"[\r]+", "", new_string)
    new_string = re.sub(r"[\n]+", " ", new_string)

    # firstly, divide the whole text into sentences, using punctuation as divider.
    try:
        sent_tokenizer = PunktSentenceTokenizer(new_string)
        sentences = sent_tokenizer.tokenize(new_string)
    except ValueError:
        sentences = sent_tokenize(new_string)

    # secondly, split each sentence into single words.
    word_punctuation_tokenizer = WordPunctTokenizer()
    words = []
    for sentence in sentences:
        word_list = word_punctuation_tokenizer.tokenize(sentence)
        for word in word_list:
            words.append(word)

    # lastly, if possible, lemmatize the words given, that is, try to find the root of the word in the WordNet
    # dictionary.
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    for word in words:
        if word in stop_words:
            continue
        lemmatized_word = lemmatizer.lemmatize(word)
        if word != lemmatized_word:
            words.remove(word)
            words.append(lemmatized_word)

    return words


def save_occurrence_word_to_file(filepath, word_occurrence_dict):
    fp = open(filepath, 'w')
    occurrence_word_dict = {}
    for word, occurrence in word_occurrence_dict.items():
        words = occurrence_word_dict.get(occurrence)
        if words is not None:
            words.append(word)
            occurrence_word_dict.__setitem__(occurrence, words)
        else:
            occurrence_word_dict.__setitem__(occurrence, [word])

    for occurrence in sorted(occurrence_word_dict.keys()):
        for word in occurrence_word_dict.get(occurrence):
            fp.write(str(occurrence) + ' -> ' + word + '\n')


class WordsMiner:
    pages = {}
    mined_pages = {}
    """ Dictionary containing as key all the filenames related to the pages that have been analysed to extract
    words of serious games. Each key has a dictionary in which are stored (word, # of occurrences found). """
    global_occurrences = {}
    """Dictionary containing as key all the words found during the analysis of different pages on the web and as 
    value the number of occurrences of such words. """

    def __init__(self, dictionary_of_pages):
        self.pages = dictionary_of_pages
        self.find_serious_games_words()
        self.compute_global_occurrences()

    def find_serious_games_words(self):
        """
        This method, given a web path, finds the occurrences of each word contained into it. The result is stored
        into both the field 'mined_pages' and in the file with the given 'filename' (in the form of
        (word, # of occurrences))
        """
        for filename, path in self.pages.items():
            if '.pdf' in path:
                text = find_pdf_from_web_page(path)
            else:
                text = find_text_from_web_page(path)

            words = sanitize_text(text)  # the method returns a list of words found in the text

            occurrence_word_dictionary = count_occurrences(words)  # return value -> { key = word, value = #occurrence }
            occurrences = sorted(
                occurrence_word_dictionary)  # a list of the keys is returned, ordered in alphabetical order
            new_occurrences_ordered = {}
            for occurrence in occurrences:
                # here the dictionary has the same structure as before, but it has the occurrences ordered in ascending
                # alphabetical order.
                # { key = word, value = #occurrence }
                if len(occurrence) > 3:
                    new_occurrences_ordered.__setitem__(occurrence, occurrence_word_dictionary.get(occurrence))

            save_occurrence_word_to_file('./data/output_data/' + filename + '.txt', new_occurrences_ordered)

            # save the words found for later statistics
            self.mined_pages.__setitem__(filename, new_occurrences_ordered)

    def compute_global_occurrences(self):
        """"
        This method computes the aggregated occurrences of every word, related to serious games, that is found
        with the previous methods by searching on the web.
        """

        for filename in self.mined_pages.keys():
            local_occurrences = self.mined_pages.get(filename)
            for word in local_occurrences.keys():
                tmp_count = self.global_occurrences.get(word)
                if tmp_count:
                    self.global_occurrences.__setitem__(word, tmp_count + local_occurrences.get(word))
                else:
                    self.global_occurrences.__setitem__(word, local_occurrences.get(word))
