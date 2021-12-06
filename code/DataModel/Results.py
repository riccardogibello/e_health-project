class Results:
    def __init__(self, y_test, y_pred_list_test, ids_test):
        self.results = []
        i = 0
        for id_ in ids_test:
            self.results.append([id_, y_test[i], y_pred_list_test[i]])
            i = i + 1
