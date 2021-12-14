class PerformanceMetrics:
    def __init__(self, accuracy, precision, recall, f1):
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1 = f1

    def print_values(self):
        print(f'MODEL PERFORMANCES:\n'
              f'\t* Accuracy\t : {self.accuracy}\n'
              f'\t* Recall\t : {self.recall}\n'
              f'\t* Precision\t : {self.precision}\n'
              f'\t* F1     \t : {self.f1}')
