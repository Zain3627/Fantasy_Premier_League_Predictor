import DataLoader as dl
import DataPreprocessing as dp
import FeatureEngineering as fe
import StatsPipeline as sp
import pandas as pd

if __name__ == "__main__":
    loader = dl.DataLoader()
    preprocessor = dp.DataPreprocessing()
    # feature_engineering = fe.FeatureEngineering()

    statsPipeline = sp.StatsPipeline(loader,preprocessor)
    statsPipeline.run()


