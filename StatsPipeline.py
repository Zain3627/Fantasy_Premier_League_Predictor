import DataLoader as dl
import DataPreprocessing as dp

import pandas as pd
import numpy as np
import os
output_dir = 'stats'

class StatsPipeline:
    def __init__(self,loader,preprocessor):
        self.loader = loader
        self.preprocessor = preprocessor

    def run(self):

        teams_for = self.loader.load_data('https://fbref.com/en/comps/9/Premier-League-Stats#all_stats_squads_gca','stats_squads_standard_for')    
        teams_against = self.loader.load_data('https://fbref.com/en/comps/9/Premier-League-Stats#all_stats_squads_gca','stats_squads_standard_against')    

        teams_for = self.preprocessor.stats_teams_prepocessing(teams_for,False)
        teams_against = self.preprocessor.stats_teams_prepocessing(teams_against,True)
        
        teams_for.to_csv(f"{output_dir}/teams_for.csv",index=False)
        teams_against.to_csv(f"{output_dir}/teams_against.csv",index=False)