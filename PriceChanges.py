import datetime

class PriceChanges:
    def __init__(self,loader,preprocessor):
        self.loader = loader
        self.preprocessor = preprocessor

    def run(self):
        players = self.loader.load_data_api("https://fantasy.premierleague.com/api/bootstrap-static/",'elements')
        
        players['net_transfers'] = players['transfers_in_event'] - players['transfers_out_event']
        players['selected_by_percent'] = players['selected_by_percent'].astype(float) / 100.0
        players['timestamp'] = datetime.datetime.now()
        players.to_csv("fpl_snapshots.csv", mode='a', index=False)

        