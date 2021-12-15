import os
import numpy as np
from DataManagers.DatabaseManager import do_query
from Utilities.Classifiers.PaperClassifiers.PaperClassifier import PaperClassifier, classify_serious_games_papers


class FrequentistPaperClassifier(PaperClassifier):
    """
    This class is used in order to classify a particular publication in one of the 8 possible classes.
    These are: Case Control, Case Series, Cohort Study, Meta Analysis, Observational Study, Other, RCT and Systematic
    Review.
    """

    def __init__(self):
        super().__init__()
        self.class_words__dictionary = {}  # this is a dictionary in which for every class (key)
        # a list of the related words is provided (value)

        self.initialize_class_name_word_lists()

        self.test_model_()
        self.classify_serious_games_papers_()

    def initialize_class_name_word_lists(self):
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

    def test_model_(self):
        super().test_model(classification_function=self.classify_paper,
                           path_for_confusion_matrix='./data/output_data/FrequentistConfusionMatrix.png',
                           metrics_path='./data/output_data/FrequentistMetrics.png')

    def classify_paper(self, publication):
        """
        This method evaluates, for each class of paper, how many occurrences of the related words are found in the title
        and in the abstract of the given publication.
        """
        class_array = []
        occurrence_array = []
        for class_ in self.class_words__dictionary.keys():
            # for each type of publication, compute the total count of
            # the occurrences of the words given in the vocabularies
            class_array.append(class_)

            title = publication.title
            abstract = publication.abstract

            total_occurrences = 0
            for word in self.class_words__dictionary.get(class_):
                total_occurrences = total_occurrences + title.count(word) + abstract.count(word)

            occurrence_array.append(total_occurrences)

        # find the class with the maximum number of occurrences of the words in the given publication abstract and title
        occurrence_array = np.array(occurrence_array)
        index_max = np.argmax(occurrence_array)
        assert (len(occurrence_array) == len(class_array))

        # now updates the value in the table 'paper' for the given publication
        query = 'UPDATE paper SET type = %s WHERE paper_id = %s'
        do_query((class_array[index_max], publication.id), query)

        return class_array[index_max]

    def classify_serious_games_papers_(self):
        classify_serious_games_papers(classification_function=self.classify_paper)
