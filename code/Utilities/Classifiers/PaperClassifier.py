import os
import numpy as np

from DataManagers.DatabaseManager import do_query
from DataModel.Publication import Publication


class PaperClassifier:
    """
    This class is used in order to classify a particular publication in one of the 8 possible classes.
    These are: Case Control, Case Series, Cohort Study, Meta Analysis, Observational Study, Other, RCT and Systematic
    Review.
    """

    def __init__(self):
        self.class_words__dictionary = {}  # this is a dictionary in which for every class (key)
        # a list of the related words is provided (value)

        file_names_list = next(os.walk('./data/dictionaries/'))[2]
        for file_name in file_names_list:
            f_in = open('./data/dictionaries/' + str(file_name), 'r')
            class_name = file_name.replace('.txt', '')
            lines = f_in.readlines()
            words_list = []
            for line in lines:
                line = line.replace('\n', '')
                words_list.append(line)

            self.class_words__dictionary.__setitem__(class_name, words_list)

    def classify_paper(self, publication):
        """
        This method evaluates, for each class of paper, how many occurrences of the related words are found in the title
        and in the abstract of the given publication.
        """
        class_array = []
        occurrence_array = []
        for class_ in self.class_words__dictionary.keys():
            class_array.append(class_)

            title = publication.title
            abstract = publication.abstract

            total_occurrences = 0
            for word in self.class_words__dictionary.get(class_):
                total_occurrences = total_occurrences + title.count(word) + abstract.count(word)

            occurrence_array.append(total_occurrences)

        occurrence_array = np.array(occurrence_array)
        index_max = np.argmax(occurrence_array)
        assert (len(occurrence_array) == len(class_array))

        return class_array[index_max]
