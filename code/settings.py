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
                                 'Role Playing',
                                 'Medical']

KAGGLE_DATASET_COLUMNS = ['App Name', 'App Id', 'Category', 'Rating', 'Rating Count', 'Installs',
                          'Minimum Installs', 'Maximum Installs', 'Free', 'Price', 'Currency' 'Size',
                          'Minimum Android', 'Developer Id', 'Developer Website', 'Developer Email', 'Released',
                          'Last Updated', 'Content Rating', 'Privacy Policy',
                          'Ad Supported', 'In App Purchases', 'Editors Choice', 'Scraped Time']

KAGGLE_KEY_COLUMNS = ['App Id', 'Category', 'App Name']
KAGGLE_DATASET_PATH = 'data/input_data/kaggle_playstore_apps_new.csv'

# PERFORMANCE
MAX_DATASET_THREADS = 16
MAX_RETRIEVE_APP_DATA_THREADS = 32
MAX_FILTER_THREADS = 10

# DEBUG
DEBUG = True

# DATABASE SETTINGS
MAX_CONNECTION_ATTEMPTS = 20
