from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import sys
import argparse
import csv
import json
import selenium.common.exceptions
import os
chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')

################################################################
### INITIALIZE
################################################################
print("INITIALIZE ...")

fromPage = int(sys.argv[1])
toPage = int(sys.argv[2])
url = "https://origin.build/#/materials?p=P&locale=en&page=0&gacreditid=100000060&q="
driver = webdriver.Chrome(
            options=chrome_options, executable_path="/Users/nhannguyen/Documents/crawlerFB/chromedriver")
content = []
errorMessage= ""

print("CRAWLING FROM PAGE " + str(fromPage) + " TO PAGE " +str(toPage))