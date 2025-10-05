import pandas as pd
import requests
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
    
    def load_data_api(self, url,section):
        response = requests.get(url)
        data = response.json()
        # players_data = data['elements']
        if section != None:
            df = pd.DataFrame(data[section])
        else:
            df = pd.DataFrame(data)
        return df

 