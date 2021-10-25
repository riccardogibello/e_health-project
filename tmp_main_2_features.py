from FeatureExtractor import FeatureExtractor

if __name__ == '__main__':
    words = ["strong educational potential",
             "educational potential"
             "educational-related needs",
             "educational needs"
             "teaching material",
             "teaching",
             "serious",
             "serious game",
             "serious purpose",
             "serious purpose scenario",
             "real life cases",
             "training",
             "education",
             "learning game",
             "learning",
             "increase awareness",
             "stimulate",
             "train",
             "inform",
             "teach",
             "influence",
             "edugames",
             "edu-games",
             "rules",
             "games for education",
             "educational game",
             "transmit educational knowledge",
             "transmit knowledge",
             "cognitive performance",
             "brain training",
             "educational multiplayer online game",
             "problem solving strategies",
             "problem solving",
             "solving strategies",
             "decision making",
             "decision-making",
             ]
    feature_extractor = FeatureExtractor(words)
    feature_extractor.compute_features()
