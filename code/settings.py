import multiprocessing

SERIOUS_GAMES_CATEGORIES_LIST = ['Adventure',
                                 'Racing',
                                 'Puzzle',
                                 'Arcade',
                                 'Education',
                                 'Board',
                                 'Educational',
                                 'Casual',
                                 'Card',
                                 'Trivia',
                                 'Strategy',
                                 'Action',
                                 'Simulation',
                                 'Role Playing']

KAGGLE_KEY_COLUMNS = ['App Id', 'Category', 'App Name']
KAGGLE_DATASET_PATH = 'data/input_data/kaggle_playstore_apps_new.csv'

# 1546300800 - Tuesday 1 January 2019 00:00:00
# 1577836800 - Wednesday 1 January 2020 00:00:00
# 1609459200 - Friday 1 January 2021 00:00:00
LAST_UPDATE = 1546300800

ADULT_RATINGS = ['Adult only 18+', 'Mature 17+']


# PERFORMANCE
MAX_DATASET_THREADS = min(multiprocessing.cpu_count(), 6)
MAX_RETRIEVE_APP_DATA_THREADS = multiprocessing.cpu_count()*2

# DEBUG
DEBUG = False
DATASET_DEBUG = False

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

SERIOUS_WORDS = [
    "strong educational potential",
    "educational potential"
    "educational-related needs",
    "educational needs"
    "teaching material",
    "teaching",
    "serious",
    "serious game",
    "serious purpose",
    "serious purpose scenario",
    "real life cases",
    "training",
    "education",
    "learning game",
    "learning",
    "increase awareness",
    "stimulate",
    "train",
    "inform",
    "teach",
    "influence",
    "edugames",
    "edu-games",
    "rules",
    "games for education",
    "educational game",
    "transmit educational knowledge",
    "transmit knowledge",
    "cognitive performance",
    "brain training",
    "educational multiplayer online game",
    "problem solving strategies",
    "problem solving",
    "solving strategies",
    "decision making",
    "decision-making",
    "kids",
    "childen",
    "learn",
    "learning",
    "educational",
    "toddlers",
    "sounds",
    "memory",
    "baby",
    "preschool",
    "kid",
    "shapes",
    "sounds"
    "colors"
    "reading",
    "drawing",
    "babies",
    "preschoolers",
    "writing",
    "recognition",
    "imagination",
    "phonics",
    "motor",
    "literacy",
    "preschool",
    "solving",
    "ability",
    "pronunciation",
    "handwriting",
    "tracing",
    "child-friendly",
    "encouragement",
    "edutainment",
    "preschool learning",
    "to spell",
    "for kindergarten",
    "toddler games",
    "learn abc",
    "learn shapes",
    "games for toddlers",
    "game for toddlers",
    "children to learn",
    "kids learn to read",
    "learning games for kids"
    "counting skills",
    "educational puzzle game",
    "practice elementary arithmetic",
    "encourage kids"
    "educational application",
    "develop attention",
    "speech therapy",
    "game for early development",
    "expand reading vocabulary"

]
