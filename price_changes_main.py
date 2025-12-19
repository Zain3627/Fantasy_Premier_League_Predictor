import DataLoader as dl
import DataPreprocessing as dp
import FeatureEngineering as fe
import PriceChanges as pc
import pandas as pd

if __name__ == "__main__":
    loader = dl.DataLoader()
    preprocessor = dp.DataPreprocessing()

    price_pipeline = pc.PriceChanges(loader,preprocessor)
    price_pipeline.run()
    print("Price Changes Pipeline completed successfully.")