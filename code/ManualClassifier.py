from DataManagers import DatabaseManager


class ManualClassifier:
    last_analyzed_index = None
    last_index_file = None
    current_index = None
    start_index = None
    end_index = None
    google_play_link = "https://play.google.com/store/apps/details?id="
    settings_suffix = '&hl=en&gl=US'
    app_features_list = None
    file_path = 'data/input_data/last_analyzed.txt'

    def __init__(self, start, end):
        self.end_index = end + 1
        try:
            self.last_index_file = open(self.file_path, 'r')
            self.last_analyzed_index = int(self.last_index_file.readlines()[0])
            self.last_index_file.close()
        except FileNotFoundError:
            self.last_analyzed_index = start - 1
        if start <= self.last_analyzed_index:
            self.start_index = self.last_analyzed_index + 1
        else:
            self.start_index = start

        if not self.current_index:
            self.current_index = self.start_index

        features_get_query = (
            "SELECT * FROM app_features"
        )
        self.app_features_list = DatabaseManager.do_query((), query=features_get_query)

    def get_app_to_classify(self):
        if self.current_index > self.end_index:
            result = (None, None)
            return result
        app = self.app_features_list[self.current_index]
        app_id = app[0]
        url = self.google_play_link + str(app[0] + self.settings_suffix)
        result = (url, app_id)
        return result

    def classify_app_as_serious(self, app_id, serious=False):
        classify_query = (
            "INSERT IGNORE INTO labeled_app(app_id, human_classified) VALUES (%s , %s)"
        )
        DatabaseManager.do_query(((str(app_id)), serious), classify_query)
        self.last_analyzed_index = self.current_index
        self.current_index = self.current_index + 1

        self.last_index_file = open(self.file_path, 'w')
        self.last_index_file.write(str(self.last_analyzed_index))
        self.last_index_file.close()


if __name__ == '__main__':
    manual_classifier = ManualClassifier()
