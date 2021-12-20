from DataManagers.DatabaseManager import do_query


def persist_classification(app_id, is_serious=False):
    classify_query = (
        "INSERT INTO labeled_app(app_id, human_classified) VALUES (%s, %s)"
    )
    do_query((str(app_id), is_serious), classify_query)


class ManualClassifierComponent:
    def __init__(self):
        self.google_play_link = "https://play.google.com/store/apps/details?id="
        self.settings_suffix = '&hl=en&gl=US'
        self.file_path = 'data/input_data/last_analyzed.txt'

    def get_app_to_classify(self):
        query = 'SELECT app_id FROM selected_app WHERE app_id NOT IN (SELECT app_id FROM labeled_app) LIMIT 1'
        results = do_query((), query)

        app_id = -1
        for result in results:
            app_id = result[0]

        url = self.google_play_link + str(str(app_id) + self.settings_suffix)

        return url, app_id
