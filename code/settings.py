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
LAST_UPDATE = 0


# PERFORMANCE
MAX_DATASET_THREADS = min(multiprocessing.cpu_count(), 12)
MAX_RETRIEVE_APP_DATA_THREADS = multiprocessing.cpu_count()*8

# DEBUG
DEBUG = True
DATASET_DEBUG = True

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
CONT_RATING_DESC_POS = 10
TEACHER_APPROVED_DESC = 11
