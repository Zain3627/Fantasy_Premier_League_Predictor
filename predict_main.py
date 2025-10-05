import DataLoader as dl
import DataPreprocessing as dp
import FeatureEngineering as fe
import FantasyPredicorPipeline as fpp
import FantasyModel as fm

if __name__ == "__main__":
    loader = dl.DataLoader()
    preprocessor = dp.DataPreprocessing()
    feature_engineering = fe.FeatureEngineering()
    goalkeeper_model = fm.FantasyModel(1)
    defender_model = fm.FantasyModel(2)
    attacker_model = fm.FantasyModel(3)
    fantasyPredictorPipeline = fpp.FantasyPredicorPipeline(loader,preprocessor,goalkeeper_model,defender_model,attacker_model,feature_engineering)

    deadlines = loader.load_data_api('https://fantasy.premierleague.com/api/bootstrap-static/','events')
    finished_gw = dp.DataPreprocessing().get_current_gw(deadlines) - 1

    position_dictionaries = fantasyPredictorPipeline.run(finished_gw+1,finished_gw+5)

