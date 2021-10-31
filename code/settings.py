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
