from unittest import loader
from numpy import info
import pandas as pd


class LiveStats:
    def __init__(self,loader,preprocessor):
        self.loader = loader
        self.preprocessor = preprocessor

    def run(self, team_id):
        deadlines = self.loader.load_data_api('https://fantasy.premierleague.com/api/bootstrap-static/','events')
        self.finished_gw = self.preprocessor.get_current_gw(deadlines) - 1

        # get team picks for the last finished gw
        url1 = f"https://fantasy.premierleague.com/api/entry/{team_id}/"
        url2 = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{self.finished_gw}/picks/"
        self.info = self.loader.load_live_team(url1) 
        # print(self.info["player_name"])

        self.team_entry_history = self.loader.load_data_api(url2, 'entry_history')
        team_value = (self.team_entry_history['value']*1.0 / 10.0).iloc[0]
        # print("value " + str(team_value))
        
        self.team_picks = self.loader.load_data_api(url2, 'picks')
        players = self.loader.load_data_api("https://fantasy.premierleague.com/api/bootstrap-static/",'elements')
        player_ids_names = players.copy()
        self.players_stats = player_ids_names[['id', 'web_name','team','event_points','selected_by_percent','transfers_in_event','transfers_out_event']]
        self.team_picks = self.team_picks.merge(self.players_stats, left_on='element', right_on='id', how='left')
        # print(f"Team Picks for GW{self.finished_gw}: ")
        # print(self.team_picks)
    