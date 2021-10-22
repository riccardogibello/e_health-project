from nltk import WordNetLemmatizer, PunktSentenceTokenizer, WordPunctTokenizer
from nltk.corpus import stopwords

from DatabaseManager import do_query
from WordsMiner import WordsMiner


def count_labelings(evaluations):
    serious = 0
    non_serious = 0
    for el in evaluations:
        if el == 0:
            non_serious = non_serious + 1
        else:
            serious = serious + 1

    return serious, non_serious


def extract_data_from_db():
    """
    This method extracts from the database all the applications which have a flag set in 'verified' column (these are
    all the applications which are found to be 'teacher and doctor approved' and manually checked) and many applications
    that were discarded because not part of an interesting category. These two sets will compose our training dataset
    for classification.
    :return: a list of all the training descriptions of the applications
    :return: a list of all the labels related to the given training descriptions
    """
    evaluations = []
    descriptions = []

    query = "SELECT description, teacher_approved FROM app WHERE teacher_approved = True"
    descriptions_evaluations = do_query('', query)  # this returns a list of lists, in the form of [(description,
    # True), ...]
    query = "SELECT description, False FROM discarded_app"
    tmp_descriptions_evaluations = do_query('', query)
    descriptions_evaluations.append(tmp_descriptions_evaluations)

    for desc_eval in descriptions_evaluations:
        descriptions.append(desc_eval[0])
        evaluations.append(desc_eval[1])

    return descriptions, evaluations


def transform_dictionary(dictionary_word_occurrence):
    word_set = set(dictionary_word_occurrence.keys())
    word_set = sorted(word_set)
    dictionary_occurrence_words = {}
    for word in word_set:
        occurrence = dictionary_word_occurrence.get(word)
        word_list = dictionary_occurrence_words.get(occurrence)
        if word_list:
            dictionary_occurrence_words.__setitem__(occurrence, word_list.append(word))
        else:
            dictionary_occurrence_words.__setitem__(occurrence, word)
    return dictionary_occurrence_words


class MNBayesClassifier:
    descriptions = []
    evaluations = []
    non_serious_games_words = []
    serious_games_words = []
    non_serious_occurrences = {}
    serious_occurrences = {}
    prior_probabilites = {'serious': 0.0, 'non-serious': 0.0}
    serious_likelihood_probabilities = {}
    non_serious_likelihood_probabilities = {}
    word_miner = WordsMiner

    def __init__(self, word_miner):
        self.word_miner = word_miner
        self.create_bag_of_words()
        self.compute_prior_probabilities()
        self.compute_likelihood_probabilities()
        self.save_statistics()

    def save_statistics(self):
        f_out = open('./data/output_data/priors.txt')
        f_out.write('serious -> ' + str(self.prior_probabilites.get('serious')))
        f_out.write('non-serious -> ' + str(self.prior_probabilites.get('non-serious')))
        f_out = open('./data/output_data/likelihoods.txt')
        f_out.write('-------------------------------------------------- SERIOUS LIKELIHOODS '
                    '--------------------------------------------------\n')
        for word in self.serious_likelihood_probabilities.keys():
            occurrences = self.serious_likelihood_probabilities.get(word)
            f_out.write(str(occurrences) + ' --> ' + word + '\n')
        f_out.write('\n-------------------------------------------------- NON SERIOUS LIKELIHOODS '
                    '--------------------------------------------------\n')
        for word in self.non_serious_likelihood_probabilities.keys():
            occurrences = self.non_serious_likelihood_probabilities.get(word)
            f_out.write(str(occurrences) + ' --> ' + word + '\n')

    def compute_prior_probabilities(self):
        """
        This method computes the prior probabilities for the two classes of descriptions
        ('serious game' / 'non serious game')
        """
        descriptions, evaluations = extract_data_from_db()
        serious, non_serious = count_labelings(evaluations)
        self.prior_probabilites.__setitem__('serious', serious / len(evaluations))
        self.prior_probabilites.__setitem__('non-serious', non_serious / len(evaluations))
        self.descriptions = descriptions
        self.evaluations = evaluations

    def compute_likelihood_probabilities(self):
        """
        This method computes the likelihood probabilities, that is, it computes the probability for each
        feature (word) in the vocabulary (set of all descriptions), given the class
        ('serious game' / 'non serious game'). The likelihood is then computed by dividing two terms A/B:
            - A: # of occurrences of the word in the descriptions, given a specific class
            - B: # of words in the descriptions, given the specific class
        In particular a simple smoother, like Lapace smoother, is used, in order to avoid zero-vanishing when
        computing the product of probabilities.
        """
        vocabulary_size = len(self.non_serious_games_words) + len(self.serious_games_words)
        occurrences = set().union(self.serious_occurrences.keys(), self.non_serious_occurrences.keys())
        serious_vocabulary_size = len(self.serious_games_words)
        non_serious_vocabulary_size = len(self.non_serious_games_words)
        for word in occurrences:
            occurrences_given_serious = self.serious_occurrences.get(word)
            if occurrences_given_serious:
                likelihood = (occurrences_given_serious + 1) / (serious_vocabulary_size + vocabulary_size)
            else:
                likelihood = 1 / (serious_vocabulary_size + vocabulary_size)
            self.serious_likelihood_probabilities.__setitem__(word, likelihood)

            occurrences_given_non_serious = self.non_serious_occurrences.get(word)
            if occurrences_given_non_serious:
                likelihood = (occurrences_given_non_serious + 1) / (non_serious_vocabulary_size + vocabulary_size)
            else:
                likelihood = 1 / (non_serious_vocabulary_size + vocabulary_size)
            self.non_serious_likelihood_probabilities.__setitem__(word, likelihood)

    def create_bag_of_words(self):
        """
        # TODO:
        :return:
        """
        self.tokenize_descriptions('serious')
        self.integrate_counts_with_mined_pages()
        self.tokenize_descriptions('non-serious')

    def integrate_counts_with_mined_pages(self):
        mined_pages_occurrences = self.word_miner.global_occurrences
        for word in mined_pages_occurrences.keys():
            tmp_occurrences = self.serious_occurrences.get(word)
            if tmp_occurrences:
                self.serious_occurrences.__setitem__(word, tmp_occurrences + mined_pages_occurrences.get(word))
            else:
                self.serious_occurrences.__setitem__(word, mined_pages_occurrences.get(word))

    def tokenize_descriptions(self, list_field_to_update):
        """
        # TODO:
        :return:
        """
        tokenized_descriptions = []  # this list contains all the words found into all the descriptions
        i = 0
        for description in self.descriptions:
            # here the description is not considered if the actual tokenization is being done on a class of
            # game description different from the current one
            if list_field_to_update == 'serious' and self.evaluations[i] == 0:
                continue
            if list_field_to_update == 'non-serious' and self.evaluations[i] == 1:
                continue

            # firstly, divide the whole description into sentences, using punctuation as divider.
            sent_tokenizer = PunktSentenceTokenizer(description)
            sentences = sent_tokenizer.tokenize(description)

            # secondly, split each sentence into single words.
            word_punctuation_tokenizer = WordPunctTokenizer()
            words = []
            for sentence in sentences:
                words.append(word_punctuation_tokenizer.tokenize(sentence))

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
                # now updated in the right dictionary (serious / non-serious) the number of
                # occurrences of the current word by adding one to the count.
                self.update_word_count(list_field_to_update, lemmatized_word)
            tokenized_descriptions.append(words)
            i = i + 1

        if list_field_to_update == 'non-serious':
            self.non_serious_games_words = tokenized_descriptions
        else:
            self.serious_games_words = tokenized_descriptions

    def update_word_count(self, list_field_to_update, word):
        """
        # TODO:
        :return:
        """
        if list_field_to_update == 'serious':
            actual_count = self.serious_occurrences.get(word)
            if actual_count:
                self.serious_occurrences.__setitem__(word, actual_count + 1)
            else:
                self.serious_occurrences.__setitem__(word, 1)
        else:
            actual_count = self.non_serious_occurrences.get(word)
            if actual_count:
                self.non_serious_occurrences.__setitem__(word, actual_count + 1)
            else:
                self.non_serious_occurrences.__setitem__(word, 1)
