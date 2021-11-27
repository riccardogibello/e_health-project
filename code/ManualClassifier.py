from DataManagers import DatabaseManager
from settings import  DEBUG


class ManualClassifier:
    last_analyzed_index = None
    last_index_file = None
    current_index = None
    start_index = None
    end_index = None
    google_play_link = "https://play.google.com/store/apps/details?id="
    settings_suffix = '&hl=en&gl=US'
    apps_list = None
    file_path = 'data/input_data/last_analyzed.txt'

    def __init__(self, start, end):
        if DEBUG:
            print(f"Starting classifying apps in range {start} - {end}")
        self.start_index = start
        self.end_index = end
        self.current_index = self.start_index
        get_apps_query = (
            "SELECT app_id, human_classified FROM labeled_app"
        )
        self.apps_list = DatabaseManager.do_query((), query=get_apps_query)
        while self.apps_list[self.current_index][1] is not None and self.current_index <= self.end_index:
            self.current_index = self.current_index + 1

    def get_app_to_classify(self):
        if self.current_index > self.end_index:
            result = (None, None)
            return result
        app = self.apps_list[self.current_index]
        app_id = app[0]
        url = self.google_play_link + str(app[0] + self.settings_suffix)
        result = (url, app_id)
        return result

    def classify_app_as_serious(self, app_id, serious=False):
        classify_query = (
            "UPDATE labeled_app SET human_classified = %s WHERE app_id = %s"
        )
        DatabaseManager.do_query((serious, (str(app_id))), classify_query)
        self.current_index = self.current_index + 1
