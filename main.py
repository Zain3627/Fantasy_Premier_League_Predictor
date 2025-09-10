import DataLoader as dl
import DataPreprocessing as dp
import FeatureEngineering as fe
import FantasyPredicorPipeline as fpp
import FantasyModel as fm
import pandas as pd

if __name__ == "__main__":
    loader = dl.DataLoader()
    preprocessor = dp.DataPreprocessing()
    feature_engineering = fe.FeatureEngineering()
    goalkeeper_model = fm.FantasyModel(1)
    defender_model = fm.FantasyModel(2)
    attacker_model = fm.FantasyModel(3)
    fantasyPredictorPipeline = fpp.FantasyPredicorPipeline(loader,preprocessor,goalkeeper_model,defender_model,attacker_model,feature_engineering)
    position_dictionaries = fantasyPredictorPipeline.run(4,6)


