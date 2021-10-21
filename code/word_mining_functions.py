from nltk import WordNetLemmatizer, PunktSentenceTokenizer, WordPunctTokenizer
from web_mining_functions import *


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
        words.append(word_punctuation_tokenizer.tokenize(sentence))

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
    text = re.sub("[\n]+", "\n", text)
    text = text.encode('utf8').decode('ascii', 'ignore')
    punctuations = '''`=|0123456789!()[]{};:'",<>./?@#$%^&*_~'''
    for c in punctuations:
        text = text.replace(c, '')

    return text


class WordsMiner:
    mined_pages = {}
    """ Dictionary containing as key all the filenames related to the pages that have been analysed to extract
    words of serious games. Each key has a dictionary in which are stored (word, # of occurrences found). """
    global_occurrences = {}
    """Dictionary containing as key all the words found during the analysis of different pages on the web and as 
    value the number of occurrences of such words. """

    def find_serious_games_words(self, filename, path):
        """
        This method, given a web path, finds the occurrences of each word contained into it. The result is stored
        into both the field 'mined_pages' and in the file with the given 'filename' (in the form of
        (word, # of occurrences))
        """

        if '.pdf' in path:
            text = find_pdf_from_web_page(path)
        else:
            text = find_text_from_web_page(path)

        text = sanitize_text(text)
        words = split_text(text)  # the method returns a list of words found in the text

        occurrence_word_dictionary = count_occurrences(words)  # return value -> { key = word, value = #occurrence }
        occurrences = sorted(
            occurrence_word_dictionary)  # a list of the keys is returned, ordered in alphabetical order
        new_occurrences_ordered = {}
        for occurrence in occurrences:
            # here the dictionary has the same structure as before, but it has the occurrences ordered in ascending
            # alphabetical order.
            # { key = word, value = #occurrence }
            new_occurrences_ordered.__setitem__(occurrence, occurrence_word_dictionary.get(occurrence))

        fp = open('./data/output_data/' + filename + '.txt', 'w')
        for occ, n_occ in new_occurrences_ordered.items():
            fp.write(occ + '     ' + str(n_occ) + '\n')

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
