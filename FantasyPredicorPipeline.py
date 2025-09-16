import DataLoader as dl
import DataPreprocessing as dp
import FantasyModel as fm
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
output_dir = 'predictions'
ou = 'logs'

os.makedirs(output_dir, exist_ok=True)

class FantasyPredicorPipeline:
    def __init__(self,loader,preprocessor,goalkeeper_model,defender_model,attacker_model,feature_engineering):
        self.loader = loader
        self.preprocessor = preprocessor
        self.goalkeeper_model = goalkeeper_model
        self.defender_model = defender_model
        self.attacker_model = attacker_model
        self.feature_engineering = feature_engineering
        self.fixtures = None
        self.team_stats = None
        self.finished_gw = 0
        self.full_players = None

    def append_team(self,df):
        fixt = self.fixtures[self.fixtures['finished'] == True]
        df_left = fixt.add_prefix("fixtures_")
        df_right = self.team_stats.add_prefix("awayteam_")
        df_merged = pd.merge(df_left, df_right, left_on="fixtures_team_a", right_on="awayteam_id", how="inner")

        df_right = self.team_stats.add_prefix('hometeam_')
        df_merged = pd.merge(df_merged, df_right, left_on="fixtures_team_h", right_on="hometeam_id", how="inner")

        df_left = df.add_prefix("player_")
        df_merged = pd.merge(df_left, df_merged, left_on="player_fixture", right_on="fixtures_id", how="inner")
        ####### for each row i want to set will_play for players with minutes=0 to 0 and set home and way strengths
        for idx, row in df_merged.iterrows():
            if row['player_minutes'] == 0:
                df_merged.loc[idx, 'player_will_play'] = 0
            elif row['player_minutes'] < 60:
                df_merged.loc[idx, 'player_will_play'] = 0.7
            else:
                df_merged.loc[idx, 'player_will_play'] = 1

            if row['player_was_home'] == False:
                #away match
                #playerteam
                df_merged.loc[idx, 'player_team_strength'] = row['awayteam_strength']
                df_merged.loc[idx, 'player_team_strength_overall'] = row['awayteam_strength_overall_away']
                df_merged.loc[idx, 'player_team_strength_attack'] = row['awayteam_strength_attack_away']
                df_merged.loc[idx, 'player_team_strength_defence'] = row['awayteam_strength_defence_away']
                #opponent
                df_merged.loc[idx, 'opponent_team_strength'] = row['hometeam_strength']
                df_merged.loc[idx, 'opponent_team_strength_overall'] = row['hometeam_strength_overall_home']
                df_merged.loc[idx, 'opponent_team_strength_attack'] = row['hometeam_strength_attack_home']
                df_merged.loc[idx, 'opponent_team_strength_defence'] = row['hometeam_strength_defence_home']

            else:
                #home match
                #playerteam
                df_merged.loc[idx, 'player_team_strength'] = row['hometeam_strength']
                df_merged.loc[idx, 'player_team_strength_overall'] = row['hometeam_strength_overall_home']
                df_merged.loc[idx, 'player_team_strength_attack'] = row['hometeam_strength_attack_home']
                df_merged.loc[idx, 'player_team_strength_defence'] = row['hometeam_strength_defence_home']
                #opponent
                df_merged.loc[idx, 'opponent_team_strength'] = row['awayteam_strength']
                df_merged.loc[idx, 'opponent_team_strength_overall'] = row['awayteam_strength_overall_away']
                df_merged.loc[idx, 'opponent_team_strength_attack'] = row['awayteam_strength_attack_away']
                df_merged.loc[idx, 'opponent_team_strength_defence'] = row['awayteam_strength_defence_away']
        return df_merged
    
    def goalkeeper_append_for_predictions(self, df, fix_gw):
        stats_to_average = ['player_points_per_game','player_goals_scored','player_assists','player_clean_sheets','player_goals_conceded','player_own_goals',
                            'player_penalties_saved','player_yellow_cards','player_red_cards','player_saves','player_bonus','player_bps','player_influence','player_creativity',
                            'player_threat','player_ict_index','player_clearances_blocks_interceptions','player_recoveries','player_expected_goals','player_expected_assists',
                            'player_expected_goal_involvements','player_expected_goals_conceded','player_will_play','player_team','player_avg_points_last_3y',
                            
                            'saves_per_goal_conceded','saves_per_match','clean_sheets_per_match','player_recoveries_per_match',
                            'team_defense_efficiency',

                            ]
        df_rolling = df.groupby('player_id')[stats_to_average].rolling(window=5, min_periods=1).mean().round(3).reset_index()
        df_player_avg = df_rolling.groupby('player_id').last().reset_index()
        fixt = self.fixtures[self.fixtures['event'] == fix_gw]
        df_left = fixt.add_prefix("fixtures_")
        df_right = self.team_stats.add_prefix("awayteam_")
        df_merged = pd.merge(df_left, df_right, left_on="fixtures_team_a", right_on="awayteam_id", how="inner")

        df_right = self.team_stats.add_prefix('hometeam_')
        df_merged = pd.merge(df_merged, df_right, left_on="fixtures_team_h", right_on="hometeam_id", how="inner")
        df_left = df_player_avg.copy()

        for idx,p in df_left.iterrows():
            for _,f in df_merged.iterrows():
                if p['player_team'] == f['fixtures_team_h']:
                    #home match
                    df_left.loc[idx,'player_was_home'] = True
                    df_left.loc[idx, 'player_team_strength'] = f['hometeam_strength']
                    df_left.loc[idx, 'player_team_strength_overall'] = f['hometeam_strength_overall_home']
                    df_left.loc[idx, 'player_team_strength_attack'] = f['hometeam_strength_attack_home']
                    df_left.loc[idx, 'player_team_strength_defence'] = f['hometeam_strength_defence_home']

                    df_left.loc[idx, 'player_opponent_team'] = f['fixtures_team_a']
                    df_left.loc[idx, 'opponent_team_strength'] = f['awayteam_strength']
                    df_left.loc[idx, 'opponent_team_strength_overall'] = f['awayteam_strength_overall_away']
                    df_left.loc[idx, 'opponent_team_strength_attack'] = f['awayteam_strength_attack_away']
                    df_left.loc[idx, 'opponent_team_strength_defence'] = f['awayteam_strength_defence_away']

                elif p['player_team'] == f['fixtures_team_a']:
                    #away match
                    df_left.loc[idx,'player_was_home'] = False
                    df_left.loc[idx, 'player_opponent_team'] = f['fixtures_team_h']
                    df_left.loc[idx, 'player_team_strength'] = f['awayteam_strength']
                    df_left.loc[idx, 'player_team_strength_overall'] = f['awayteam_strength_overall_away']
                    df_left.loc[idx, 'player_team_strength_attack'] = f['awayteam_strength_attack_away']
                    df_left.loc[idx, 'player_team_strength_defence'] = f['awayteam_strength_defence_away']

                    df_left.loc[idx, 'opponent_team_strength'] = f['hometeam_strength']
                    df_left.loc[idx, 'opponent_team_strength_overall'] = f['hometeam_strength_overall_home']
                    df_left.loc[idx, 'opponent_team_strength_attack'] = f['hometeam_strength_attack_home']
                    df_left.loc[idx, 'opponent_team_strength_defence'] = f['hometeam_strength_defence_home']

        return df_left

    def outfielders_append_for_predictions(self, df, fix_gw):
        stats_to_average = ['player_points_per_game','player_goals_scored','player_assists','player_clean_sheets','player_goals_conceded','player_own_goals',
                            'player_penalties_missed','player_yellow_cards','player_red_cards','player_bonus','player_bps','player_influence','player_creativity',
                            'player_threat','player_ict_index','player_clearances_blocks_interceptions','player_recoveries','player_expected_goals','player_expected_assists',
                            'player_expected_goal_involvements','player_expected_goals_conceded','player_will_play','player_team',
                            'player_defensive_contribution','player_tackles','player_avg_points_last_3y',

                            'clean_sheets_per_match','goals_per_match','assists_per_match','recoveries_per_match',
                            'tackles_per_match','interceptions_per_match','DC_per_match','team_defense_efficiency',
                            ]
        df_rolling = df.groupby('player_id')[stats_to_average].rolling(window=5, min_periods=1).mean().round(3).reset_index()
        df_player_avg = df_rolling.groupby('player_id').last().reset_index()
        fixt = self.fixtures[self.fixtures['event'] == fix_gw]
        df_left = fixt.add_prefix("fixtures_")
        df_right = self.team_stats.add_prefix("awayteam_")
        df_merged = pd.merge(df_left, df_right, left_on="fixtures_team_a", right_on="awayteam_id", how="inner")

        df_right = self.team_stats.add_prefix('hometeam_')
        df_merged = pd.merge(df_merged, df_right, left_on="fixtures_team_h", right_on="hometeam_id", how="inner")
        df_left = df_player_avg.copy()

        for idx,p in df_left.iterrows():
            for _,f in df_merged.iterrows():
                if p['player_team'] == f['fixtures_team_h']:
                    #home match
                    df_left.loc[idx,'player_was_home'] = True
                    df_left.loc[idx, 'player_team_strength'] = f['hometeam_strength']
                    df_left.loc[idx, 'player_team_strength_overall'] = f['hometeam_strength_overall_home']
                    df_left.loc[idx, 'player_team_strength_attack'] = f['hometeam_strength_attack_home']
                    df_left.loc[idx, 'player_team_strength_defence'] = f['hometeam_strength_defence_home']

                    df_left.loc[idx, 'player_opponent_team'] = f['fixtures_team_a']
                    df_left.loc[idx, 'opponent_team_strength'] = f['awayteam_strength']
                    df_left.loc[idx, 'opponent_team_strength_overall'] = f['awayteam_strength_overall_away']
                    df_left.loc[idx, 'opponent_team_strength_attack'] = f['awayteam_strength_attack_away']
                    df_left.loc[idx, 'opponent_team_strength_defence'] = f['awayteam_strength_defence_away']

                elif p['player_team'] == f['fixtures_team_a']:
                    #away match
                    df_left.loc[idx,'player_was_home'] = False
                    df_left.loc[idx, 'player_opponent_team'] = f['fixtures_team_h']
                    df_left.loc[idx, 'player_team_strength'] = f['awayteam_strength']
                    df_left.loc[idx, 'player_team_strength_overall'] = f['awayteam_strength_overall_away']
                    df_left.loc[idx, 'player_team_strength_attack'] = f['awayteam_strength_attack_away']
                    df_left.loc[idx, 'player_team_strength_defence'] = f['awayteam_strength_defence_away']

                    df_left.loc[idx, 'opponent_team_strength'] = f['hometeam_strength']
                    df_left.loc[idx, 'opponent_team_strength_overall'] = f['hometeam_strength_overall_home']
                    df_left.loc[idx, 'opponent_team_strength_attack'] = f['hometeam_strength_attack_home']
                    df_left.loc[idx, 'opponent_team_strength_defence'] = f['hometeam_strength_defence_home']

        return df_left

    def train_goalkeepers(self, df, gw):
        # Prepare data for finished GW
        goalkeepers_df = self.append_team(df)
        goalkeepers_df = self.feature_engineering.add_features(goalkeepers_df,self.full_players,1,True)
        df = goalkeepers_df.copy()
        features_to_exclude = ['player_element_type','player_web_name','player_element','player_fixture','player_opponent_team','player_total_points','player_round'
                                ,'fixtures_finished','fixtures_event','fixtures_stats','fixtures_code','fixtures_id','fixtures_team_a','fixtures_team_h',
                                'fixtures_pulse_id','awayteam_id','awayteam_name','awayteam_position','awayteam_short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty',
                                'hometeam_id','hometeam_name','hometeam_position','hometeam_short_name','player_starts',
                                'awayteam_strength','awayteam_strength_overall_home','awayteam_strength_overall_away','awayteam_strength_attack_home',
                                'awayteam_strength_attack_away','awayteam_strength_defence_home','awayteam_strength_defence_away',
                                'hometeam_strength','hometeam_strength_overall_home','hometeam_strength_overall_away','hometeam_strength_attack_home',
                                'hometeam_strength_attack_away','hometeam_strength_defence_home','hometeam_strength_defence_away',
                                'player_team_h_score','player_team_a_score','player_minutes',
                                'player_clearances_blocks_interceptions','player_recoveries',
                               'short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty']
        features = [col for col in goalkeepers_df.columns if col not in features_to_exclude]
        # Split the data into features (X) and target (y)
        X = goalkeepers_df[features]
        
        Y = goalkeepers_df['player_total_points']
        # Train the model
        self.goalkeeper_model.train(X, Y)
        # X.to_csv(f"{ou}/goalkeepers_gw_{gw}_train.csv", index=False)
        

        # Prepare data for new GW
        goalkeepers_df = self.goalkeeper_append_for_predictions(df,gw)
        features_to_exclude = ['player_element_type','player_web_name','player_element','player_fixture','player_total_points','player_round'
                                ,'fixtures_finished','fixtures_event','fixtures_stats','fixtures_code','fixtures_id','fixtures_team_a','fixtures_team_h',
                                'fixtures_pulse_id','awayteam_id','awayteam_name','awayteam_position','awayteam_short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty',
                                'hometeam_id','hometeam_name','hometeam_position','hometeam_short_name',
                                'awayteam_strength','awayteam_strength_overall_home','awayteam_strength_overall_away','awayteam_strength_attack_home',
                                'awayteam_strength_attack_away','awayteam_strength_defence_home','awayteam_strength_defence_away',
                                'hometeam_strength','hometeam_strength_overall_home','hometeam_strength_overall_away','hometeam_strength_attack_home',
                                'hometeam_strength_attack_away','hometeam_strength_defence_home','hometeam_strength_defence_away',
                                'player_team_h_score','player_team_a_score','player_minutes','player_level_1','player_starts',
                               
                               'player_clearances_blocks_interceptions','player_recoveries',
                               'short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty']
        features = [col for col in goalkeepers_df.columns if col not in features_to_exclude]
        
        # Split the data into features (X) and target (y)
        X = goalkeepers_df[features]
        X = self.feature_engineering.add_features(X,self.full_players,1,False)
        X = X[self.goalkeeper_model.model.feature_names_in_]

        # X.to_csv(f"{ou}/goalkeepers_gw_{gw}_predict.csv", index=False)

        # Make and display predictions for the test set
        test_predictions = self.goalkeeper_model.predict(X)
        goalkeepers_df['predicted_points'] = test_predictions
        goalkeepers_df = goalkeepers_df.sort_values(by='predicted_points', ascending=False)[[ 'player_id','predicted_points']]
        return goalkeepers_df

    def train_outfielders(self,df,gw,defender):
        players = self.append_team(df)
        players = self.feature_engineering.add_features(players,self.full_players,3 if not defender else 2,True)
        df = players.copy()
        # Prepare data for the finished GW
        features_to_exclude = ['player_element_type','player_web_name','player_element','player_fixture','player_total_points','player_round'
                                ,'fixtures_finished','fixtures_event','fixtures_stats','fixtures_code','fixtures_id','fixtures_team_a','fixtures_team_h',
                                'fixtures_pulse_id','awayteam_id','awayteam_name','awayteam_position','awayteam_short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty',
                                'hometeam_id','hometeam_name','hometeam_position','hometeam_short_name','player_starts',
                                'awayteam_strength','awayteam_strength_overall_home','awayteam_strength_overall_away','awayteam_strength_attack_home',
                                'awayteam_strength_attack_away','awayteam_strength_defence_home','awayteam_strength_defence_away',
                                'hometeam_strength','hometeam_strength_overall_home','hometeam_strength_overall_away','hometeam_strength_attack_home',
                                'hometeam_strength_attack_away','hometeam_strength_defence_home','hometeam_strength_defence_away',
                                'player_team_h_score','player_team_a_score','player_minutes',

                               'short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty']
        features = [col for col in players.columns if col not in features_to_exclude]
        # Split the data into features (X) and target (y)
        X = players[features]
        Y = players['player_total_points']
        # Train the model
        if defender:
            self.defender_model.train(X,Y)
        else:
            self.attacker_model.train(X,Y)
        # X.to_csv(f"{ou}/outfielders_gw_{gw}_train.csv", index=False)
        
        # Prepare data for the new GW
        players = self.outfielders_append_for_predictions(df,gw)

        features_to_exclude = ['player_element_type','player_web_name','player_element','player_fixture','player_total_points','player_round'
                                ,'fixtures_finished','fixtures_event','fixtures_stats','fixtures_code','fixtures_id','fixtures_team_a','fixtures_team_h',
                                'fixtures_pulse_id','awayteam_id','awayteam_name','awayteam_position','awayteam_short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty',
                                'hometeam_id','hometeam_name','hometeam_position','hometeam_short_name','player_starts',
                                'awayteam_strength','awayteam_strength_overall_home','awayteam_strength_overall_away','awayteam_strength_attack_home',
                                'awayteam_strength_attack_away','awayteam_strength_defence_home','awayteam_strength_defence_away',
                                'hometeam_strength','hometeam_strength_overall_home','hometeam_strength_overall_away','hometeam_strength_attack_home',
                                'hometeam_strength_attack_away','hometeam_strength_defence_home','hometeam_strength_defence_away',
                                'player_team_h_score','player_team_a_score','player_minutes','player_level_1',
                               'short_name','fixtures_team_h_difficulty','fixtures_team_a_difficulty']
        
        features = [col for col in players.columns if col not in features_to_exclude]

        # Split the data into features (X) and target (y)
        X = players[features]
        if defender:
            X = self.feature_engineering.add_features(X,self.full_players,2,False)
            X = X[self.defender_model.model.feature_names_in_]
        else:
            X = self.feature_engineering.add_features(X,self.full_players,3,False)
            X = X[self.attacker_model.model.feature_names_in_]
        # X.to_csv(f"{ou}/outfielders_gw_{gw}_predict.csv", index=False)

        # Make and display predictions for the test set
        if defender:
            test_predictions = self.defender_model.predict(X)
        else:
            test_predictions = self.attacker_model.predict(X)
        players['predicted_points'] = test_predictions
        players = players.sort_values(by='predicted_points', ascending=False)[['player_id', 'predicted_points']]
        return players

    def run(self,gw_start=0,gw_end=0):
        deadlines = self.loader.load_data_api('https://fantasy.premierleague.com/api/bootstrap-static/','events')
        self.finished_gw = self.preprocessor.get_current_gw(deadlines) - 1
        
        # Set default range if not provided
        if gw_start == 0:
            gw_start = self.finished_gw + 1
        if gw_end == 0:
            gw_end = gw_start  # Single gameweek if no end specified

        self.fixtures = self.loader.load_data_api('https://fantasy.premierleague.com/api/fixtures/',None)
        player_stats = self.loader.load_data_api("https://fantasy.premierleague.com/api/bootstrap-static/",'elements')
        player_ids_names = player_stats.copy()
        player_ids_names = player_ids_names[['id', 'web_name','team']]


        self.team_stats = self.loader.load_data_api("https://fantasy.premierleague.com/api/bootstrap-static/",'teams')
        player_ids_names = pd.merge(player_ids_names, self.team_stats, left_on="team", right_on="id", how="inner")
        player_ids_names = player_ids_names[['id_x', 'web_name','team','name']]
        self.fixtures = self.preprocessor.fixtures_processing(self.fixtures)

        player_stats = self.preprocessor.players_processing(player_stats)

        history = pd.DataFrame()
        avg_points_list = []
        for _, p in player_stats.iterrows():
            pid = p["id"]
            url = f"https://fantasy.premierleague.com/api/element-summary/{pid}/"
            one_history = self.loader.load_data_api(url, 'history')
            past_seasons = self.loader.load_data_api(url, 'history_past')

            avg_points_last_3y = 0
            if past_seasons is not None and len(past_seasons) > 0:
                past_seasons_df = pd.DataFrame(past_seasons)
                past_seasons_df = past_seasons_df.sort_values("season_name", ascending=False).head(3)
                avg_points_last_3y = past_seasons_df["total_points"].mean()

            avg_points_list.append({"id": pid, "avg_points_last_3y": avg_points_last_3y})
            history = pd.concat([history, one_history], ignore_index=True)
            print(f'load player {player_stats['web_name'][player_stats['id']==pid]}')

        avg_points_df = pd.DataFrame(avg_points_list)
        history = pd.merge(history,avg_points_df, left_on='element', right_on="id", how="left")

        # history = pd.read_csv('all_players_neeew.csv') 
        history.drop(columns=['id'], inplace=True)

        player_stats = pd.merge(player_stats, history, left_on="id", right_on="element", how="inner")
        df,goalkeepers,defenders,midfielders,forwards = self.preprocessor.divide_by_position(player_stats)
        self.full_players = df

        self.team_stats = self.preprocessor.teams_processing(self.team_stats)

        # Initialize dictionaries to store predictions for each position across all gameweeks
        all_gk_predictions = {}
        all_def_predictions = {}
        all_mid_predictions = {}
        all_fwd_predictions = {}

        for gw in range(gw_start, gw_end + 1):
            print(f"Processing gameweek {gw}...")
            
            # Get predictions for all positions
            predicted_goalkeepers = self.train_goalkeepers(goalkeepers, gw)
            predicted_defenders = self.train_outfielders(defenders, gw, True)
            predicted_midfielders = self.train_outfielders(midfielders, gw, False)
            predicted_forwards = self.train_outfielders(forwards, gw, False)

            # Store predictions with gameweek as column name
            all_gk_predictions[f'gw_{gw}'] = predicted_goalkeepers[['player_id', 'predicted_points']]
            all_def_predictions[f'gw_{gw}'] = predicted_defenders[['player_id', 'predicted_points']]
            all_mid_predictions[f'gw_{gw}'] = predicted_midfielders[['player_id', 'predicted_points']]
            all_fwd_predictions[f'gw_{gw}'] = predicted_forwards[['player_id', 'predicted_points']]

            print(f"Gameweek {gw} completed!")
        
        # Create final dataframes for each position
        positions = [
            ('goalkeepers', all_gk_predictions),
            ('defenders', all_def_predictions), 
            ('midfielders', all_mid_predictions),
            ('forwards', all_fwd_predictions)
        ]
        
        # Dictionary to store the final dataframes
        position_dataframes = {}
        
        for position_name, predictions_dict in positions:
            if predictions_dict:
                # Start with the first gameweek data
                first_gw = list(predictions_dict.keys())[0]
                final_df = predictions_dict[first_gw].copy()
                final_df = final_df.rename(columns={'predicted_points': first_gw})
                
                # Add subsequent gameweeks
                for gw_key in list(predictions_dict.keys())[1:]:
                    gw_data = predictions_dict[gw_key]
                    final_df = final_df.merge(
                        gw_data.rename(columns={'predicted_points': gw_key}), 
                        on=['player_id'], 
                        how='outer'
                    )
                
                # Calculate total points (sum of all gameweek columns)
                gw_columns = [col for col in final_df.columns if col.startswith('gw_')]
                final_df['total_points'] = final_df[gw_columns].sum(axis=1).round(2)
                
                final_df = pd.merge(player_ids_names, final_df, left_on="id_x", right_on="player_id", how="inner")
                final_df = final_df.sort_values(by='total_points', ascending=False)

                # Save to CSV and store in dictionary
                # final_df.to_csv(f"{output_dir}/{position_name}_gw{gw_start}_to_gw{gw_end}.csv", index=False)
                position_dataframes[position_name] = final_df
            
        print(f"Pipeline completed")
        
        # Return the dataframes for each position
        return position_dataframes

    
