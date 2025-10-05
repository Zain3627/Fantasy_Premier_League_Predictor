import numpy as np
class FeatureEngineering:
    def __init__(self):
        pass

    def add_features(self,players,full_df,position,train): #goalkeeper = 1, defender = 2, mid/attacker = 3
        players = self.all_positions_common(players)
        if position == 1:
            players = self.goalkeepers_cross_features(players,full_df)
        else:
            players = self.outfielders_cross_features(players,full_df)
        if train:
            if position == 1:
                players = self.goalkeepers_train(players, full_df)
            else:
                players = self.outfielders_train(players, full_df)

        return players
    
    def goalkeepers_train (self,df,full_df):
        df['saves_per_goal_conceded'] = df['player_saves'] / (df['player_goals_conceded'] + 1)
        df['saves_per_match'] = df['player_saves'] / (df['player_starts'] + 1)
        df['clean_sheets_per_match'] = df['player_clean_sheets'] / (df['player_starts'] + 1)
        df['player_recoveries_per_match'] = df['player_recoveries'] / (df['player_starts'] + 1)

        numerator = full_df.groupby(['team','fixture'])['defensive_contribution'].transform('sum')
        denominator = full_df.groupby(['team','fixture'])['goals_conceded'].transform('max')
        df['team_defense_efficiency'] = numerator / (denominator + 1e-6)

        return df
    
    def outfielders_train(self,df,full_df):
        df['clean_sheets_per_match'] = df['player_clean_sheets'] / (df['player_starts'] + 1)
        df['goals_per_match'] = df['player_goals_scored'] / (df['player_starts'] + 1)
        df['assists_per_match'] = df['player_assists'] / (df['player_starts'] + 1)
        df['recoveries_per_match'] = df['player_recoveries'] / (df['player_starts'] + 1)
        df['tackles_per_match'] = df['player_tackles'] / (df['player_starts'] + 1)
        df['interceptions_per_match'] = df['player_clearances_blocks_interceptions'] / (df['player_starts'] + 1)
        df['DC_per_match'] = df['player_defensive_contribution'] / (df['player_starts'] + 1)
        
        numerator = full_df.groupby(['team','fixture'])['defensive_contribution'].transform('sum')
        denominator = full_df.groupby(['team','fixture'])['goals_conceded'].transform('max')
        df['team_defense_efficiency'] = numerator / (denominator + 1e-6)

        return df
    
    def all_positions_common(self,df):
        df['diff_strength'] = df['player_team_strength'] - df['opponent_team_strength']
        df['diff_strength_2'] = df['player_team_strength_overall'] - df['opponent_team_strength_overall']
        df['diff_att_def'] = df['player_team_strength_attack'] - df['opponent_team_strength_defence']
        df['diff_def_att'] = df['player_team_strength_defence'] - df['opponent_team_strength_attack']
        
        df['sqrt_diff_strength'] = np.sqrt(np.abs(df['diff_strength']))
        df['sqrt_diff_strength_2'] = np.sqrt(np.abs(df['diff_strength_2']))
        df['sqrt_diff_att_def'] = np.sqrt(np.abs(df['diff_att_def']))
        df['sqrt_diff_def_att'] = np.sqrt(np.abs(df['diff_def_att']))

        df['ratio_att_def'] = df['player_team_strength_attack'] / (df['opponent_team_strength_defence'] + 1)
        df['ratio_def_att'] = df['player_team_strength_defence'] / (df['opponent_team_strength_attack'] + 1)
        df['ratio_strength'] = df['player_team_strength'] / (df['opponent_team_strength'] + 1)

        df['home_attack_strength'] = df['player_team_strength_attack'] * df['player_was_home']
        df['home_defence_strength'] = df['player_team_strength_defence'] * df['player_was_home']
        df['home_overall_strength'] = df['player_team_strength_overall'] * df['player_was_home']

        df['team_balance'] = df['player_team_strength_attack'] - df['player_team_strength_defence']
        df['opponent_balance'] = df['opponent_team_strength_attack'] - df['opponent_team_strength_defence']
        df['balance_diff'] = df['team_balance'] - df['opponent_balance']

        # players against attacking threats(XG,XG,ICT) / match
        # players against defensive contributions

        return df
    
    def goalkeepers_cross_features(self, df, full_df):
        # Add attacking threat features for goalkeepers based on opponent teams
        
        # Create a mapping of team to total goals scored by that team
        team_goals_scored = full_df.groupby('team')['goals_scored'].sum().reset_index()
        team_goals_scored.columns = ['opponent_team', 'opponent_team_total_goals']
        
        # Merge this information with the goalkeepers dataframe
        df = df.merge(team_goals_scored, left_on='player_opponent_team', right_on='opponent_team', how='left')
        
        # Drop the temporary opponent_team column if it was created
        if 'opponent_team' in df.columns:
            df = df.drop('opponent_team', axis=1)
        
        return df
    
    def outfielders_cross_features(self, df, full_df):
        # Add defensive performance features for outfielders based on opponent teams
        
        # Create a mapping of team to maximum goals conceded and clean sheets by that team
        team_defensive_stats = full_df.groupby('team').agg({
            'goals_scored': 'sum',
            'goals_conceded': 'sum',
            'clean_sheets': 'sum',
            'saves': 'sum'
        }).reset_index()
        team_defensive_stats.columns = ['opponent_team', 'opponent_team_total_goals_scored', 'opponent_team_total_goals_conceded','opponent_team_total_clean_sheets','opponent_team_total_saves']

        # Merge this information with the outfielders dataframe
        df = df.merge(team_defensive_stats, left_on='player_opponent_team', right_on='opponent_team', how='left')
        
        # Drop the temporary opponent_team column if it was created
        if 'opponent_team' in df.columns:
            df = df.drop('opponent_team', axis=1)
        
        return df