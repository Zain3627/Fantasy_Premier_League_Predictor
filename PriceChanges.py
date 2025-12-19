class PriceChanges:
    def __init__(self,loader,preprocessor):
        self.loader = loader
        self.preprocessor = preprocessor

    def run(self):
        players = self.loader.load_data_api("https://fantasy.premierleague.com/api/bootstrap-static/",'elements')
        
        total_transfers = players['transfers_in_event'].sum() 
        print("Total Transfers In This GW: " + str(total_transfers))
        
        # Group players by position and calculate total transfers for each position
        position_transfers = players.groupby("element_type")["transfers_in_event"].sum().reset_index()

        # Rename the column for clarity
        position_transfers.rename(columns={"transfers_in_event": "total_transfers"}, inplace=True)

        # Print the total transfers for each position
        print("Total Transfers by Position:")
        print(position_transfers)