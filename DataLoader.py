import pandas as pd
import requests

class DataLoader:
    def __init__(self):
        pass

    def load_data(self, url, table_id):
        return pd.read_html(url, attrs={"id":table_id})[0]
    
    def load_data_api(self, url,section):
        response = requests.get(url)
        data = response.json()
        # players_data = data['elements']
        if section != None:
            df = pd.DataFrame(data[section])
        else:
            df = pd.DataFrame(data)
        return df
