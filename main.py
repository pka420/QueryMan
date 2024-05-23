import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException
import json
import os
from mail import Mailer
curdir = os.getcwd()

with open('targets.json', 'r') as f:
    data = json.load(f)
    print(data)

def switchToNewTab(driver):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

def switchToTab(driver, tab):
    driver.switch_to.window(driver.window_handles[tab])


chromedriver_path = curdir + "/chromedriver"
chrome_binary_path = curdir + "/chrome-linux/chrome"

chrome_options = Options()
chrome_options.binary_location = chrome_binary_path
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-allow-origins=*")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

service = Service(chromedriver_path)
d = DesiredCapabilities.CHROME
driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=d)
driver.maximize_window()

driver.get(data['url'])
mailer = Mailer(data['sender_email'], data['receiver_email'])
try:
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_351MY')))
    ads = element.text.split(' ')[0]
    print(ads)
    # convert to integer
    if int(ads) < 6:
        print("Ads are less than 6")
        mailer.send_mail("Dyson AirWrap Ads are decreased.", f"Current ads: {ads}")
    driver.quit()
    exit()
except Exception as e:
    print(e)
    print("Element not found")
    driver.quit()
