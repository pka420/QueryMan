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
import datetime
from dotenv import load_dotenv
import argparse

load_dotenv()


def switchToNewTab(driver):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

def switchToTab(driver, tab):
    driver.switch_to.window(driver.window_handles[tab])

def clickOnSignIn(driver):
    i=0
    while i<3:
        wait = WebDriverWait(driver, 30)
        try:
            element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div[1]/div[1]/div/div[3]/div[4]/a')))
            if element:
                element.click()
                return False
            else:
                print("Attempt", i, "sign in not found \n")
                driver.quit()
                exit(1)
        except Exception as e:
            print(e)

        driver.get("https://x.com")

    return True

def checkForUnusualActivity(driver):
    time.sleep(5)
    try:
        elements = driver.find_elements(By.CLASS_NAME, "css-175oi2r")
        for element in elements:
            if "There was unusual login activity on your account" in element.text:
                return True
    except Exception as e:
        print(e)
        return False

    return False


def checkForWrongPassword(driver):
    time.sleep(5)
    try:
        elements = driver.find_elements(By.CLASS_NAME, "css-1jxf684")
        for element in elements:
            if "Enter your Password" in element.text:
                return True
    except Exception as e:
        print(e)
        return False

def enterUsername(driver):
    wait = WebDriverWait(driver, 30)
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')))
    if element:
        element.send_keys("AmanRajGil13322")
    else:
        print("unable to find username input field")
        return False

    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/button')))
    if element:
        element.click()
    else:
        print("unable to find next button")
        return False

    return True

def removeModals(driver):
    # I am not able to reproduce the modal, so I am just writing the code to close the modal
    time.sleep(5)
    try:
        element = driver.find_element(By.XPath, "")
        if element:
            element.click();
        else:
            print("no modal opened by x")
    except Exception as e:
        print(e)
        return False

def clickOnExplore(driver):
    wait = WebDriverWait(driver, 30)
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[2]/div')))
    if element:
        element.click()
    else:
        print("explore not found")
        driver.quit()
        exit(1)

def clickOnTrending(driver):
    wait = WebDriverWait(driver, 30)
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a')))
    if element:
        element.click()
    else:
        print("trending not found")
        driver.quit()
        exit(1)

def getTrendingTopicsList(driver):
    trending_topics = []
    wait = WebDriverWait(driver, 30)
    topics = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-b88u0q.r-1bymd8e')))
    if not topics:
        print("No trending topics found")
        driver.quit()
        exit(1)

    print("Trending topics found")
    for topic in topics:
        trending_topics.append(topic.text)
    return trending_topics

def get_ip(driver):
    driver.get("https://ipv4.icanhazip.com/")
    try:
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/pre')))
        return element.text
    except Exception as e:
        print("Unable to get ip")
        driver.quit()
        exit(1)


parser = argparse.ArgumentParser()

parser.add_argument("-n", "--hostname", help = "hostname", required = True)
parser.add_argument("-p", "--port", help = "port", required = True)
parser.add_argument("-t", "--test", help = "test", required = False, action='store_true', default=False)

# Read arguments from command line
args = parser.parse_args()

chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
chrome_binary_path = os.getenv("CHROME_PATH")

chrome_options = Options()                                                                                                                                                                                     
chrome_options.binary_location = chrome_binary_path                                                                                                                                                            
chrome_options = Options()
chrome_options.binary_location = chrome_binary_path
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--remote-allow-origins=*")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--crash-dumps-dir=/tmp")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

print("Proxy: %s:%s" % (args.hostname, args.port))
chrome_options.add_argument('--proxy-server=http://%s:%s' % (args.hostname, args.port))

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()

if args.test:
    print("Test mode")
    get_ip(driver)
    driver.quit()
    exit(0)
else:
    data = {}
    ip_address = get_ip(driver)
    data["ip"] = ip_address
    driver.get("https://x.com")

    try:
        clickOnSignIn(driver)

        # click on email
        wait = WebDriverWait(driver, 30)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[4]/label/div/div[2]/div/input')))
        if element:
            element.send_keys(os.environ.get("EMAIL"))
        else:
            print("email input not found")

        # click on next
        wait = WebDriverWait(driver, 30)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/button[2]')))
        if element:
            element.click()
        else:
            print("next button not found")

        check_for_unusual_activity = checkForUnusualActivity(driver)
        if check_for_unusual_activity:
            print("Unusual activity detected, account may be locked.")
            username_entered = enterUsername(driver)
            if not username_entered:
                print("Unable to enter username")
                driver.quit()
                exit(1)
        else:
            print("No unusual activity detected")

        # enter password
        wait = WebDriverWait(driver, 30)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input')))
        if element:
            element.send_keys(os.environ.get("PASSWORD"))
        else:
            print("password input not found")

        # click on sign in
        wait = WebDriverWait(driver, 30)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/button')))
        if element:
            element.click()
        else:
            print("sign in button not found")
            driver.quit()
            exit(1)

        check_for_wrong_password = checkForWrongPassword(driver)
        if check_for_wrong_password:
            print("Wrong password, account may be locked.")
            driver.quit()
            exit(1)

        print("Logged in successfully")

        #removeModals(driver)

        clickOnExplore(driver)
        clickOnTrending(driver)
        trending_topics = getTrendingTopicsList(driver)

        #format into ddmmyyyyhhmmss
        today = datetime.datetime.now().strftime("%d%m%Y%H%M%S")

        data["date"] = today
        topics = {}
        for i in range(len(trending_topics)):
            if trending_topics[i].strip() == "":
                continue
            topics["nameOfTrend{}".format(i)] = trending_topics[i]

        data["topics"] = topics
        with open("trending_topics.json", "w") as file:
            file.write(json.dumps(data))

        driver.quit()
        exit(0)
    except Exception as e:
        print(e)
        driver.quit()
        exit(1)

