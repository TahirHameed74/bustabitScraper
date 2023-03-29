from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import json
import time
import pandas as pd
from datetime import datetime
from selenium.webdriver.chrome.options import DesiredCapabilities, Options
from selenium.webdriver.common.proxy import Proxy, ProxyType


# Add path to your WebDriver according to the browser you are using
# PATH = "E:\SeleniumProject\chromedriver.exe"

url = "https://www.bustabit.com/play"
chrome_options = Options()


def getResults(driver):
    # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 20)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "lxml")
    try:
        tr = soup.find("div", class_="table-responsive").table.tr
    except Exception as e:
        print(e)

    gameId = []
    bustNumber = []
    for td in tr.find_all("td"):
        bustNumber.append(str(td.find("a").get_text()))
        gameId.append(str(td.find("a", href=True)["href"]))

    getLen = len(bustNumber)

    temp = datetime.now().strftime("%m/%d/%Y %H:%M:%S %f")
    timeStamp = [temp] * getLen
    driver.quit()
    return (gameId, bustNumber, timeStamp)


def saveResult(timeStamp, gameId, bustNumber):
    dataTuples = list(zip(timeStamp, gameId, bustNumber))
    df = pd.DataFrame(dataTuples, columns=["Time Stamp", "GameID", "Bust Number"])
    df.to_csv("data.csv", mode="a", header=False)


def mycodehere(driver):
    while True:
        gameId, bustNumber, timeStamp = getResults(driver)
        saveResult(timeStamp, gameId, bustNumber)


co = webdriver.ChromeOptions()
co.add_argument("log-level=3")
co.add_argument("--headless")


def get_proxies(co=co):
    driver = webdriver.Chrome(options=co)
    driver.get("https://free-proxy-list.net/")

    PROXIES = []
    proxies = driver.find_elements_by_css_selector("tr[role='row']")
    for p in proxies:
        result = p.text.split(" ")

        if result[-1] == "yes":
            PROXIES.append(result[0] + ":" + result[1])

    driver.close()
    return PROXIES


ALL_PROXIES = get_proxies()


def proxy_driver(PROXIES, co=co):
    prox = Proxy()

    if PROXIES:
        pxy = PROXIES[-1]
    else:
        print("--- Proxies used up (%s)" % len(PROXIES))
        PROXIES = get_proxies()

    prox.proxy_type = ProxyType.MANUAL
    prox.http_proxy = pxy

    prox.ssl_proxy = pxy

    capabilities = webdriver.DesiredCapabilities.CHROME
    prox.add_to_capabilities(capabilities)

    driver = webdriver.Chrome(options=co, desired_capabilities=capabilities)

    return driver


# --- YOU ONLY NEED TO CARE FROM THIS LINE ---
# creating new driver to use proxy
proxyDriver = proxy_driver(ALL_PROXIES)

# code must be in a while loop with a try to keep trying with different proxies
running = True

while running:
    try:
        mycodehere(proxyDriver)

        # if statement to terminate loop if code working properly
        # something()

        # you
    except:
        new = ALL_PROXIES.pop()

        # reassign driver if fail to switch proxy
        proxyDriver = proxy_driver(ALL_PROXIES)
        print("--- Switched proxy to: %s" % new)
        time.sleep(1)
