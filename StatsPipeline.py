import os
output_dir = 'stats'

class StatsPipeline:
    def __init__(self,loader,preprocessor):
        self.loader = loader
        self.preprocessor = preprocessor

    def run(self):
        
        teams_for = self.loader.load_data_selenium('https://fbref.com/en/comps/9/Premier-League-Stats#all_stats_squads_gca','stats_squads_standard_for')  
        print(f'Loaded teams for stats: {teams_for is not None}')
        teams_against = self.loader.load_data_selenium('https://fbref.com/en/comps/9/Premier-League-Stats#all_stats_squads_gca','stats_squads_standard_against')    
        print(f'Loaded teams against stats: {teams_against is not None}')

        teams_for = self.preprocessor.stats_teams_prepocessing(teams_for,False)
        teams_against = self.preprocessor.stats_teams_prepocessing(teams_against,True)
        teams_for.to_csv(f"{output_dir}/teams_for.csv",index=False)
        teams_against.to_csv(f"{output_dir}/teams_against.csv",index=False)

        goalkeepers_stats = self.loader.load_data_selenium('https://fbref.com/en/comps/9/keepers/Premier-League-Stats','stats_keeper')
        print(f'Loaded goalkeepers stats: {goalkeepers_stats is not None}')
        goalkeepers_stats = self.preprocessor.stats_gk_preprocessing(goalkeepers_stats)
        goalkeepers_stats.to_csv(f"{output_dir}/goalkeepers.csv",index=False)

        defence_stats = self.loader.load_data_selenium('https://fbref.com/en/comps/9/defense/Premier-League-Stats','stats_defense')
        print(f'Loaded defence stats: {defence_stats is not None}')
        defence_stats = self.preprocessor.stats_defence_preprocessing(defence_stats)
        defence_stats.to_csv(f"{output_dir}/defenders.csv",index=False)

        passing_stats = self.loader.load_data_selenium('https://fbref.com/en/comps/9/passing/Premier-League-Stats','stats_passing')
        print(f'Loaded passing stats: {passing_stats is not None}')
        passing_stats = self.preprocessor.stats_passing_preprocessing(passing_stats)
        passing_stats.to_csv(f"{output_dir}/passing.csv",index=False)

        shooting_stats = self.loader.load_data_selenium('https://fbref.com/en/comps/9/shooting/Premier-League-Stats','stats_shooting')
        print(f'Loaded shooting stats: {shooting_stats is not None}')
        shooting_stats = self.preprocessor.stats_shooting_preprocessing(shooting_stats)
        shooting_stats.to_csv(f"{output_dir}/shooting.csv",index=False)

        