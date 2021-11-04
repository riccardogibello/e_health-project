import time
import pandas as pd
import play_scraper
from concurrent.futures import ThreadPoolExecutor
from DataManagers.DatabaseManager import do_query


def find_app_id(old_app_title):
    # before inserting I should find the id of the app, by starting from the title
    result = play_scraper.search(old_app_title)
    for el in result:
        new_app_title = el.get('title')
        if new_app_title == old_app_title:
            return el.get('app_id')
    return ''


def extract_app_details(df, i, columns, interesting_categories):
    details = []
    for column_name in columns:
        element = df.at[i, column_name]
        if not isinstance(element, str):
            element = str(element)
        if column_name == 'Category' and element not in interesting_categories:
            return []
        details.append(element)

    app_id = find_app_id(details[0])
    if app_id != '':
        details.append(app_id)
        return details
    else:
        return []


class OldDatasetManager:
    applications = ''
    reviews = ''
    latest_app_name_extracted = ''
    latest_app_id_extracted = ''
    app_not_found = ''

    def __init__(self):
        # The following are rendering improvements to be used in order to print the data in the console
        # pd.set_option('display.max_rows', None)
        # pd.set_option('display.max_columns', None)
        # pd.set_option('display.width', None)
        # pd.set_option('display.max_colwidth', None)

        self.applications = pd.read_csv('./data/input_data/old_googleplaystore.csv')
        self.reviews = pd.read_csv('./data/input_data/old_googleplaystore_user_reviews.csv')

        # print(df.loc[[i], ['App']])   # here an object is still extracted, containing the index
        # of the element, the column name and the value stored in the column

        # print(df.at[i, 'App']) # this is the way to extract specific values stored in a table in a specific
        # (row,col) position
        # print(df.loc[i])

    def load_old_dataset_into_db(self):
        # ----------------------------------------------
        # here the loading of the app dataset is handled
        batch_size = self.applications.size * 0.05 // 1
        n_threads_max = self.applications.size // batch_size + 1
        offset = 0
        # now call the function to extract and process data from the dataset, passing as argument the batch size
        # and the offset to find the starting position
        threads_status = []
        status = False
        with ThreadPoolExecutor(max_workers=n_threads_max) as executor:
            while offset < self.applications.size:
                threads_status.append(status)
                executor.submit(self.load_app_batch_into_db, offset, batch_size, threads_status)
                offset = offset + batch_size

        while False in threads_status:
            time.sleep(3)
        # ----------------------------------------------
        # ----------------------------------------------
        # now the loading of the related reviews is handled
        # self.load_app_reviews_into_db()

    def load_app_batch_into_db(self, offset, batch_size, threads_status):
        columns = ['App', 'Category']
        interesting_categories = ['MEDICAL', 'EDUCATION', 'FAMILY', 'GAME_EDUCATIONAL']
        if offset + batch_size > self.applications.size:
            offset = self.applications.size

        for i in range(int(offset), int(offset + batch_size), 1):
            details = extract_app_details(self.applications, i, columns, interesting_categories)

            # if the category is not of interest or the app id is not found, the previous method will give back an
            # empty list of details
            if len(details) == 0:
                continue

            insert_stmt = (
                "INSERT INTO preliminary(app_id, `check`, from_dataset)"
                "VALUES (%s, %s, %s)"
            )
            do_query((details[2], False, True), insert_stmt)
        threads_status.pop()
