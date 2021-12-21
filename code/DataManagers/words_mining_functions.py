import string
import numpy as np
from nltk import WordNetLemmatizer, PunktSentenceTokenizer, WordPunctTokenizer, sent_tokenize, ngrams
from nltk.corpus import stopwords
from WEBFunctions.web_mining_functions import *


def sanitize_string(string_):
    new_string = str(string_.encode('ascii', errors='ignore').decode())
    new_string = re.sub(r"[\b]+", "", new_string)
    new_string = re.sub(r"[\t]+", "", new_string)
    new_string = re.sub(r"[\f]+", "", new_string)
    new_string = re.sub(r"[\r]+", "", new_string)
    new_string = re.sub(r"[\n]+", " ", new_string)
    new_string = re.sub(r"[ ]+", " ", new_string)
    return new_string


def count_occurrences(words):
    """
    This method, given a list of words (for example a set of tokenized sentences and words), returns a dictionary
    with all the words contained and the related occurrences.
    """
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

    sorted_dict = dict(sorted(occurrences.items(), key=lambda x: x[1], reverse=True))
    # the dictionary is returned in descending by value of the occurrences
    return sorted_dict


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


def sanitize_and_tokenize_sentences(entire_text):
    text = entire_text.lower()
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

    return sentences


def concatenate_n_grams(n_grams_list):
    list_ = []
    for n_gram in n_grams_list:
        concatenated_string = ''
        for el in n_gram:
            concatenated_string = concatenated_string + el + ' '
        concatenated_string = re.sub('[ ]$', '', concatenated_string)
        list_.append(concatenated_string)
    return list_


def sanitize_and_tokenize(text, max_n_gram=1):
    sentences = sanitize_and_tokenize_sentences(text)
    # secondly, split each sentence into single words.
    word_punctuation_tokenizer = WordPunctTokenizer()
    words = []
    for sentence in sentences:
        sentence = sentence.translate(str.maketrans('', '', string.punctuation.replace('-', '')))
        word_list = word_punctuation_tokenizer.tokenize(sentence)
        for i in np.arange(2, max_n_gram + 1):
            n_grams_list = list(ngrams(sentence.split(), i))
            n_grams_list = concatenate_n_grams(n_grams_list)
            word_list = word_list + n_grams_list
        for word in word_list:
            words.append(word)

    # lastly, if possible, lemmatize the words given, that is, try to find the root of the word in the WordNet
    # dictionary.
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    for word in words:
        if word in stop_words:
            words.remove(word)
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
