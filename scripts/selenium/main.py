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
import datetime
from dotenv import load_dotenv
import argparse

load_dotenv()

today = datetime.datetime.now().strftime("%d%m%Y")

def switchToNewTab(driver):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

def switchToTab(driver, tab):
    driver.switch_to.window(driver.window_handles[tab])

parser = argparse.ArgumentParser()

parser.add_argument("-n", "--hostname", help = "hostname", required = True)
parser.add_argument("-p", "--port", help = "port", required = True)

# Read arguments from command line
args = parser.parse_args()
print(args)
exit()

chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
chrome_binary_path = os.getenv("CHROME_PATH")

chrome_options = Options()
chrome_options.binary_location = chrome_binary_path
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-allow-origins=*")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

chrome_options.add_argument('--proxy-server=http://%s:%s' % (hostname, port))

service = Service(chromedriver_path)
d = DesiredCapabilities.CHROME
driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=d)
driver.maximize_window()

#driver.get(data['url'])
driver.get("https://whatismyipaddress.com/")
try:
    wait = WebDriverWait(driver, 30)
    #element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[4]/div')))
    element = wait.until(EC.presence_of_element_located((By.ID, 'ipv4')))
    print("Element found")
    print(element.text)
    driver.quit()
    exit()
except Exception as e:
    driver.quit()
