import pandas as pd
from google_play_scraper import app
import play_scraper
from database_handling_functions import *


def read_dataset():
    # pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    df = pd.read_csv('./data/googleplaystore.csv')
    # print(df)

    columns = ['App', 'Category', 'Rating', 'Reviews', 'Size', 'Installs',
               'Type', 'Price', 'Content Rating', 'Genres', 'Last Updated', 'Current Ver', 'Android Ver']
    interesting_categories = ['Education', 'GAME_ACTION', 'GAME_ADVENTURE']
    for i in range(5):
        # print(df.loc[[i], ['App']])   # here an object is still extracted, containing the index
        # of the element, the column name and the value stored in the column

        # print(df.at[i, 'App']) # this is the way to extract specific values stored in a table in a specific
        # (row,col) position
        # print(df.loc[i])

        details = []
        for column_name in columns:
            element = df.at[i, column_name]
            if not isinstance(element, str):
                element = str(element)
            details.append(element)

        insert_stmt = (
            "INSERT INTO APP(app, category, rating, reviews, size, installs, type, "
            "price, content_rating, genres, last_updated, current_ver, android_ver)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        # before inserting I should find the id
        #result = play_scraper.search(details[0], page=2)
        #print(result)

        #insert_tuple(details, insert_stmt)

    print(play_scraper.search('dogs', page=2))
