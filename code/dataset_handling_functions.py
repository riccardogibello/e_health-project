import pandas as pd
import play_scraper
from database_handling_functions import *
from concurrent.futures import ThreadPoolExecutor


def find_app_id(old_app_title):
    # before inserting I should find the id of the app, by starting from the title
    result = play_scraper.search(old_app_title)
    for el in result:
        new_app_title = el.get('title')
        if new_app_title == old_app_title:
            return el.get('app_id')
    return 'NOT GIVEN'


def extract_details(df, i, columns, interesting_categories):
    details = []
    for column_name in columns:
        element = df.at[i, column_name]
        if not isinstance(element, str):
            element = str(element)
        if column_name == 'Category' and element not in interesting_categories:
            details = []
            return details
        details.append(element)

    details.append(find_app_id(details[0]))
    return details


class OldDatasetHandler:
    dataframe = ''

    def __init__(self):
        # The following are rendering improvements to be used in order to print the data in the console
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # pd.set_option('display.max_colwidth', None)

        self.dataframe = pd.read_csv('./data/input_data/old_googleplaystore.csv')

        # print(df.loc[[i], ['App']])   # here an object is still extracted, containing the index
        # of the element, the column name and the value stored in the column

        # print(df.at[i, 'App']) # this is the way to extract specific values stored in a table in a specific
        # (row,col) position
        # print(df.loc[i])

    def load_old_dataset_into_db(self):
        batch_size = self.dataframe.size * 0.5 // 1
        n_threads_max = self.dataframe.size // batch_size + 1
        offset = 0
        # now call the function to extract and process data from the dataset, passing as argument the batch size
        # and the offset to find the starting position
        with ThreadPoolExecutor(max_workers=n_threads_max) as executor:
            while offset < self.dataframe.size:
                executor.submit(self.load_batch_into_db, offset, batch_size)
                offset = offset + batch_size

    def load_batch_into_db(self, offset, batch_size):
        columns = ['App', 'Category', 'Rating', 'Reviews', 'Content Rating', 'Genres']
        interesting_categories = ['MEDICAL', 'EDUCATION', 'FAMILY', 'GAME_EDUCATIONAL']
        if offset + batch_size > self.dataframe.size:
            offset = self.dataframe.size

        for i in range(int(offset), int(offset + batch_size), 1):
            details = extract_details(self.dataframe, i, columns, interesting_categories)

            # if the category is not of interest, the previous method will give back an empty list of details
            if len(details) == 0:
                continue

            insert_stmt = (
                "INSERT INTO APP(app, category, rating, reviews, content_rating, genres, app_id)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )

            insert_tuple(details, insert_stmt)


