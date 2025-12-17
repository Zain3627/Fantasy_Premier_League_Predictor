import pandas as pd
import numpy as np
import DataLoader as dl
import xgboost as xgb
from sklearn.model_selection import RandomizedSearchCV

class FantasyModel:
    def __init__(self,position):
        self.position = position
        self.loader = dl.DataLoader()
        self.model = xgb.XGBRegressor()

    def train(self, X, y):
        # Convert object columns to numeric
        for col in X.columns:
            if X[col].dtype == "object":
                X[col] = pd.to_numeric(X[col], errors="coerce")

        if self.position != 1:
            if self.position == 3:
                y = np.clip(y, None, np.percentile(y, 96))
            else:
                y = np.clip(y, None, np.percentile(y, 96))

        # apply grid search for the following parameters
        param_dist = { 
            'n_estimators': [600, 800, 1000], 
            'learning_rate': [0.001, 0.005, 0.01, 0.05, 0.1], 
            'max_depth': [4, 6, 8], 'subsample': [0.2, 0.4, 0.6, 0.8, 1.0], 
            'colsample_bytree': [0.8, 0.9, 1.0], 
            'gamma': [0], 
            'reg_alpha': [0, 0.5, 1], 
            'reg_lambda': [0, 0.5, 1] 
        }
        
        random_search = RandomizedSearchCV(self.model, param_distributions=param_dist, n_iter=40, cv=3, n_jobs=-1, verbose=2, random_state=27)
        random_search.fit(X, y)
        self.model = random_search.best_estimator_

    def predict(self, X):
        for col in X.columns:
            if X[col].dtype == "object":
                X[col] = pd.to_numeric(X[col], errors="coerce")
        Y = np.round(self.model.predict(X), 2)
        added_numbers = pd.DataFrame()
        if self.position == 1:
            for idx, row in X.iterrows():
                clean_sheets_per_match = row['clean_sheets_per_match']
                diff_def_att = row['diff_def_att']
                if diff_def_att < 0:
                    added_numbers.loc[idx, 'expected_CS_points'] = -1*(1-clean_sheets_per_match) * 3
                else:
                    added_numbers.loc[idx, 'expected_CS_points'] = clean_sheets_per_match * 3
            Y = Y + added_numbers['expected_CS_points']
            # Y = Y * X['player_will_play']

        elif self.position == 2:
            for idx, row in X.iterrows():
                clean_sheets_per_match = row['clean_sheets_per_match']
                diff_def_att = row['diff_def_att']
                if diff_def_att < 0:
                    added_numbers.loc[idx, 'expected_CS_points'] = -1*(1-clean_sheets_per_match) * 2
                else:
                    added_numbers.loc[idx, 'expected_CS_points'] = clean_sheets_per_match * 2
            Y = Y + added_numbers['expected_CS_points']
            # Y = Y * X['player_will_play']

        elif self.position == 3:
            for idx, row in X.iterrows():
                goal_involvements = row['goals_per_match'] + row['assists_per_match']
                diff_att_def = row['diff_att_def']
                if diff_att_def < 0:
                    added_numbers.loc[idx, 'expected_CS_points'] = -1*(1-goal_involvements) * 1
                else:
                    added_numbers.loc[idx, 'expected_CS_points'] = goal_involvements * 2
            Y = Y + added_numbers['expected_CS_points']
            # Y = Y * X['player_will_play']
        else:
            for idx, row in X.iterrows():
                goal_involvements = row['goals_per_match'] + row['assists_per_match']
                diff_att_def = row['diff_att_def']
                if diff_att_def < 0:
                    added_numbers.loc[idx, 'expected_CS_points'] = -1*(1-goal_involvements) * 1
                else:
                    added_numbers.loc[idx, 'expected_CS_points'] = goal_involvements * 3
            Y = Y + added_numbers['expected_CS_points']
        
        X['player_will_play'] = X['player_will_play'].round()
        Y = Y * X['player_will_play']
        Y = Y.clip(lower=0)

        player_stats = self.loader.load_data_api("https://fantasy.premierleague.com/api/bootstrap-static/",'elements')
        status_map = dict(zip(player_stats['id'], player_stats['status']))
        for idx, row in X.iterrows():
            if status_map.get(row['player_id']) != 'a':
                Y.loc[idx] = 0
        return np.round(Y, 2)
