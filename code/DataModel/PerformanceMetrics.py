class PerformanceMetrics:
    def __init__(self, accuracy=0, precision=0, recall=0, f1=0, matthews_cc=0, tp=0, tn=0, fp=0, fn=0):
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1 = f1
        self.matthews_correlation_coefficient = matthews_cc
        self.true_positives = tp
        self.true_negatives = tn
        self.false_positives = fp
        self.false_negatives = fn

    def print_values(self):
        print(f'MODEL PERFORMANCES:\n'
              f'\t* Accuracy\t : {self.accuracy}'
              f'\t* True Positives\t : {self.true_positives}\n'
              f'\t* Recall\t : {self.recall}'
              f'\t* True negatives\t : {self.true_negatives}\n'
              f'\t* Precision\t : {self.precision}'
              f'\t* False Positives\t : {self.false_positives}\n'
              f'\t* F1     \t : {self.f1}'
              f'\t* False Negatives\t : {self.false_negatives}\n'
              f'\t* Matthews_CC: {self.matthews_correlation_coefficient}')
