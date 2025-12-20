from unittest import loader
from numpy import info
import pandas as pd


class LiveStats:
    def __init__(self,loader,preprocessor):
        self.loader = loader
        self.preprocessor = preprocessor
    
    def get_team_info(self, url):
        df = self.loader.load_data_api(url,'picks')
        players = self.loader.load_data_api("https://fantasy.premierleague.com/api/bootstrap-static/",'elements')
        players= players[['id', 'web_name','team','event_points','selected_by_percent','transfers_in_event','transfers_out_event']]
        df = df.merge(players, left_on='element', right_on='id', how='left')
                
        # Double points for captain
        df["final_points"] = df["event_points"]
        df.loc[df['multiplier'] > 1, "final_points"] = df["event_points"] * df['multiplier']

        # Split squad based on multiplier
        starting_xi = df[df['multiplier'] > 0].reset_index(drop=True)
        starting_xi.index += 1
        bench = df[df['multiplier'] == 0].reset_index(drop=True)
        bench.index += 1
        print(starting_xi.columns)
        return starting_xi, bench
    
    def load_top_players(self, n=50):
        url = "https://fantasy.premierleague.com/api/leagues-classic/314/standings/"
        overall_standings = self.loader.load_data_api(url, 'standings')
        overall_standings = overall_standings['results'].iloc[0]
        
        # Extract top n players
        top_10_players = [{"id": player["entry"], "name": player["player_name"]} for player in overall_standings[:n]]
        
        # Create a list of names
        names = [player["name"] for player in top_10_players]
        
        # Create a dictionary of name-id pairs
        name_id_dict = {player["name"]: player["id"] for player in top_10_players}
        
        return names, name_id_dict
    
    def run(self, team_id):
        deadlines = self.loader.load_data_api('https://fantasy.premierleague.com/api/bootstrap-static/','events')
        self.finished_gw = self.preprocessor.get_current_gw(deadlines) - 1
        # get team picks for the last finished gw
        url1 = f"https://fantasy.premierleague.com/api/entry/{team_id}/"
        url2 = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{self.finished_gw}/picks/"
        # url2 = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/15/picks/"
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
    