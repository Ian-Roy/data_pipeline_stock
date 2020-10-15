import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def get_min_for(symb):
    r=requests.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{symb}?region=US&lang=en-US&includePrePost=false&interval=2m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance')
    chart_data = r.json()
    try:
        min_val =min([
            min([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['low']if i ]),
            min([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['high']if i ]),
            min([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['open']if i ]),
            min([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['close']if i ]),
        ])

       
    except:
        return r
    return min_val

def get_max_for(symb):
    r=requests.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{symb}?region=US&lang=en-US&includePrePost=false&interval=2m&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance')
    chart_data = r.json()
    try:

        max_val =max([
                max([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['low']if i ]),
                max([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['high']if i ]),
                max([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['open']if i ]),
                max([ i for i in chart_data['chart']['result'][0]['indicators']['quote'][0]['close']if i ]),
            ])
        
    except:
        return r
    return  max_val
    


def get_data_for_url(url):
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.set_headless()
    driver = webdriver.Firefox(firefox_options=fireFoxOptions)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.ID , 'quote-summary')))
    html=driver.page_source
    driver.close()
    return html



def get_min_max_from_html(input_html):
    soup = BeautifulSoup(input_html, 'html.parser')
    return soup.find(attrs={"data-test":"DAYS_RANGE-value"}).text