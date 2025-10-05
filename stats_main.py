import DataLoader as dl
import DataPreprocessing as dp
import StatsPipeline as sp

if __name__ == "__main__":
    loader = dl.DataLoader()
    preprocessor = dp.DataPreprocessing()
    # feature_engineering = fe.FeatureEngineering()

    statsPipeline = sp.StatsPipeline(loader,preprocessor)
    statsPipeline.run()
    print("Stats Pipeline completed successfully.")


