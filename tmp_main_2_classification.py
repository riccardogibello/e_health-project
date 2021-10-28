from FeatureExtractor import FeatureExtractor
from LogRegClassifier import LogRegClassifier

if __name__ == '__main__':
    log_classif = LogRegClassifier()
    log_classif.train_model()

    words = ["strong educational potential", "educational-related needs", "teaching material",
             "serious purpose scenario", "real life cases",
             "training", "education", "learning games", "increase awareness", "stimulate", "train", "inform", "teach",
             "influence",
             "edugames", "rules", "games for education", "transmit educational knowledge", "cognitive performance",
             "brain training",
             "educational multiplayer online game", "problem solving strategies"]
    feature_extractor = FeatureExtractor(words)
    feature_extractor.compute_features()
    log_classif.classify_apps()
