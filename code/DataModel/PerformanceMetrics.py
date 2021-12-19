class PerformanceMetrics:
    def __init__(self, accuracy=0, precision=0, recall=0, f1=0, matthews_cc=0):
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1 = f1
        self.matthews_correlation_coefficient = matthews_cc

    def print_values(self):
        print(f'MODEL PERFORMANCES:\n'
              f'\t* Accuracy\t : {self.accuracy}\n'
              f'\t* Recall\t : {self.recall}\n'
              f'\t* Precision\t : {self.precision}\n'
              f'\t* F1     \t : {self.f1}'
              f'\t* Matthews_CC\t : {self.matthews_correlation_coefficient}')
