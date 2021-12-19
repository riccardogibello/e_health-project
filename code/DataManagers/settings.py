import multiprocessing

SERIOUS_GAMES_CATEGORIES_LIST = ['Adventure', 'Racing', 'Puzzle', 'Arcade', 'Education', 'Board', 'Educational',
                                 'Casual', 'Card', 'Trivia', 'Strategy', 'Action', 'Simulation', 'Role Playing']

KAGGLE_KEY_COLUMNS = ['App Id', 'Category', 'App Name']
KAGGLE_DATASET_PATH = 'data/input_data/kaggle_playstore_apps_new.csv'

# 1546300800 - Tuesday 1 January 2019 00:00:00
# 1577836800 - Wednesday 1 January 2020 00:00:00
# 1609459200 - Friday 1 January 2021 00:00:00
LAST_UPDATE = 1546300800

ADULT_RATINGS = ['Adult only 18+', 'Mature 17+']

# PERFORMANCE
MAX_RETRIEVE_APP_DATA_THREADS = multiprocessing.cpu_count() * 10

# CLASSIFICATION SETTINGS
SMOOTHING_COEFFICIENT = 1
TEST_SET_DIMENSION = 0.20  # fraction of training set
NUM_MODELS = 1
NON_IMPROVING_ITERATIONS = 1
MAX_ITERATIONS = 5
TRUE_CLASSIFIED_INCREMENT = 0.001
WRONG_CLASSIFIED_INCREMENT = 15 * TRUE_CLASSIFIED_INCREMENT
SOFT_VOTING = False   # True - Soft voting. False - Hard voting

# DATABASE SETTINGS
MAX_CONNECTION_ATTEMPTS = 20

# APP TABLE ATTRIBUTES POSITIONS
APP_ID_POS = 0
APP_NAME_POS = 1
DESCRIPTION_POS = 2
CATEGORY_ID_POS = 3
SCORE_POS = 4
RATING_POS = 5
INSTALLS_POS = 6
DEV_ID_POS = 7
LAST_UPDATE_POS = 8
CONT_RATING_POS = 9
TEACHER_APPROVED_DESC = 10

stop_words = [
    "a", "about", "above", "across", "after", "afterwards", "again", "all", "almost", "alone", "along", "already",
    "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "another", "any",
    "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "as", "at", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "behind", "being", "beside", "besides", "between", "beyond", "both", "but",
    "by", "can", "cannot", "cant", "could", "couldnt", "de", "describe", "do", "done", "each", "eg", "either", "else",
    "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "find", "for",
    "found", "four", "from", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her",
    "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however",
    "i", "ie", "if", "in", "indeed", "is", "it", "its", "itself", "keep", "least", "less", "ltd", "made", "many", "may",
    "me", "meanwhile", "might", "mine", "more", "moreover", "most", "mostly", "much", "must", "my", "myself", "name",
    "namely", "neither", "never", "nevertheless", "next", "no", "nobody", "none", "noone", "nor", "not", "nothing",
    "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise",
    "our", "ours", "ourselves", "out", "over", "own", "part", "perhaps", "please", "put", "rather", "re", "same", "see",
    "seem", "seemed", "seeming", "seems", "she", "should", "since", "sincere", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such", "take", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these",
    "they", "this", "those", "though", "through", "throughout", "thru", "thus", "to", "together", "too", "toward",
    "towards", "under", "until", "up", "upon", "us", "very", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether",
    "which", "while", "who", "whoever", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet",
    "you", "your", "yours", "yourself", "yourselves", "u", "b", "s", "ha", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "0"
]
