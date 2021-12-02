from nltk import WordNetLemmatizer, PunktSentenceTokenizer, WordPunctTokenizer, sent_tokenize
from nltk.corpus import stopwords
from DataManagers.DatabaseManager import do_query
from DataManagers.WordsMiner import WordsMiner


def count_labels(name_desc_eval):
    serious = 0
    non_serious = 0
    for el in name_desc_eval:
        evaluation = el[2]
        if evaluation == 0:
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

    query = "SELECT app_name, description, human_classified " \
            "FROM app AS a, labeled_app AS la " \
            "WHERE la.app_id = a.app_id"
    name_desc_eval = do_query('', query)  # this returns a list of tuples, in which we find name,
    # description and manual classification of the training app

    return name_desc_eval


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
    name_desc_eval = []
    non_serious_games_words = []
    serious_games_words = []
    non_serious_occurrences = {}
    serious_occurrences = {}
    prior_probabilities = {'serious': 0.0, 'non-serious': 0.0}
    serious_likelihood_probabilities = {}
    non_serious_likelihood_probabilities = {}
    word_miner = WordsMiner

    def __init__(self):
        self.word_miner = WordsMiner({'wikipage': 'https://en.wikipedia.org/wiki/Serious_game',
                                      'paper_1': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5222787/pdf/fpsyt-07'
                                                 '-00215.pdf',
                                      'paper_2': 'https://www.hindawi.com/journals/ijcgt/2014/787968/'})

    def build_model(self):
        self.compute_prior_probabilities()
        self.create_bag_of_words()
        self.compute_likelihood_probabilities()
        self.save_statistics()

    def save_statistics(self):
        f_out = open('./data/output_data/priors.txt', 'w', encoding='utf-8')
        f_out.write('serious -> ' + str(self.prior_probabilities.get('serious')) + '\n')
        f_out.write('non-serious -> ' + str(self.prior_probabilities.get('non-serious')) + '\n')
        f_out = open('./data/output_data/likelihoods.txt', 'w', encoding='utf-8')
        f_out.write('-------------------------------------------------- SERIOUS LIKELIHOODS '
                    '--------------------------------------------------\n')
        for word in self.serious_likelihood_probabilities.keys():
            occurrences = self.serious_likelihood_probabilities.get(word)
            if occurrences < 0.005 or len(word) < 3:
                continue
            f_out.write(str(occurrences) + ' --> ' + word + '\n')
        f_out.write('\n-------------------------------------------------- NON SERIOUS LIKELIHOODS '
                    '--------------------------------------------------\n')
        for word in self.non_serious_likelihood_probabilities.keys():
            occurrences = self.non_serious_likelihood_probabilities.get(word)
            if occurrences < 0.005 or len(word) < 3:
                continue
            f_out.write(str(occurrences) + ' --> ' + word + '\n')

    def compute_prior_probabilities(self):
        """
        This method computes the prior probabilities for the two classes of descriptions
        ('serious game' / 'non serious game')
        """
        name_desc_eval = extract_data_from_db()
        serious, non_serious = count_labels(name_desc_eval)
        self.prior_probabilities.__setitem__('serious', serious / len(name_desc_eval))
        self.prior_probabilities.__setitem__('non-serious', non_serious / len(name_desc_eval))
        self.name_desc_eval = name_desc_eval

    def compute_likelihood_probabilities(self):
        """
        This method computes the likelihood probabilities, that is, it computes the probability for each
        feature (word) in the vocabulary (set of all descriptions), given the class
        ('serious game' / 'non serious game'). The likelihood is then computed by dividing two terms A/B:
            - A: # of occurrences of the word in the descriptions, given a specific class
            - B: # of words in the descriptions, given the specific class
        In particular a simple smoother, like Laplace smoother, is used, in order to avoid zero-vanishing when
        computing the product of probabilities.
        """
        word_occurrences = set().union(self.serious_occurrences.keys(), self.non_serious_occurrences.keys())
        vocabulary_size = len(word_occurrences)
        serious_vocabulary_size = len(self.serious_games_words)
        non_serious_vocabulary_size = len(self.non_serious_games_words)
        for word in word_occurrences:
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
        tmp_cnt = 0
        for tuple_ in self.name_desc_eval:
            name = tuple_[0].lower()
            description = tuple_[1].lower()
            is_serious_game = tuple_[2]

            # here the description is not considered if the actual tokenization is being done on a class of
            # game description different from the current one
            if list_field_to_update == 'serious' and is_serious_game == 0:
                continue
            if list_field_to_update == 'non-serious' and is_serious_game == 1:
                continue

            self.compute_occurrences(name, list_field_to_update)
            self.compute_occurrences(description, list_field_to_update)
            tmp_cnt = tmp_cnt + 1
        print(tmp_cnt)

    def compute_occurrences(self, text, list_field_to_update):
        # firstly, divide the whole text into sentences, using punctuation as divider.
        try:
            sent_tokenizer = PunktSentenceTokenizer(text)
            sentences = sent_tokenizer.tokenize(text)
        except ValueError:
            sentences = sent_tokenize(text)

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
            # now update in the right dictionary (serious / non-serious) the number of
            # occurrences of the current word by adding one to the count.
            self.update_word_count(list_field_to_update, lemmatized_word)

    def update_word_count(self, list_field_to_update, word):
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
