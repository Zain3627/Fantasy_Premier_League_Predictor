import pandas as pd
import requests
from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options



class DataLoader:
    def __init__(self):
        pass
    
    def load_data_selenium(_self, url, table_id):
        options = Options()
        options.add_argument('--headless')  # Run without GUI
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for the table to be loaded
            wait = WebDriverWait(driver, 10)
            table = wait.until(EC.presence_of_element_located((By.ID, table_id)))
            
            # Get the page source after JavaScript execution
            html = driver.page_source
            
            # Parse with pandas
            df = pd.read_html(html, attrs={"id": table_id})[0]
            return df
            
        except Exception as e:
            return None
            
        finally:
            if driver:
                driver.quit()

    def load_data(self, url, table_id):
        return pd.read_html(url, attrs={"id":table_id})[0]
    
    def load_data_header(self, url, table_id):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return pd.read_html(StringIO(response.text), attrs={"id": table_id})[0]
    
    def load_data_api(self, url,section):
        response = requests.get(url)
        data = response.json()
        # players_data = data['elements']
        if section != None:
            df = data[section]
        else:
            df = pd.DataFrame([data])

        if isinstance(df, list):
            return pd.DataFrame(df)

    # CASE 2: dict (scalar values) → single-row DataFrame
        if isinstance(df, dict):
            return pd.DataFrame([df])

        return df
    
    def load_live_team(self, url):
        response = requests.get(url).json()
        summary = {
            "player_name": response["player_first_name"] + " " + response["player_last_name"],
            "nationality": response["player_region_name"],
            "overall_points": response["summary_overall_points"],
            "event_points": response["summary_event_points"],
            "rank": response["summary_overall_rank"],
            "event_rank": response["summary_event_rank"],
        }
        df = pd.DataFrame([summary])
        return df

