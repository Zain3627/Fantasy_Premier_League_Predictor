import DataLoader as dl
import DataPreprocessing as dp
import FeatureEngineering as fe
import LiveStats as ls
import pandas as pd

if __name__ == "__main__":
    loader = dl.DataLoader()
    preprocessor = dp.DataPreprocessing()

    liveStatsPipeline = ls.LiveStats(loader,preprocessor)
    liveStatsPipeline.run()
    print("Live Stats Pipeline completed successfully.")
