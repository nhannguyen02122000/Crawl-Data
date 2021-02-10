from logging import error
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import argparse
import csv
import json
import selenium.common.exceptions
from typing_extensions import final
chrome_options = Options()
chrome_options.add_argument("--headless") #Comment this to run on UI

print("Initialize ...")
driver = webdriver.Chrome(options=chrome_options, executable_path="/Users/nhannguyen/Documents/crawlerFB/chromedriver")

content = []
countPro = 0
linklist = []
driver.get("https://www.transparencycatalog.com/search?number=&q=")

############################################################
### Write to file
############################################################
def write2file():
    keys = []
    for obj in content:
        for key,value in obj.items():
            if key not in keys:
                keys.append(key)
    
    csv_file = "/Users/nhannguyen/Documents/crawlerFB/out2.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for data in content:
                writer.writerow(data)
    except IOError:
        print("I/O error")

############################################################
### GET ALL OF LINKS
############################################################
while 1:
    cnt = 0
    options = driver.find_elements_by_tag_name('select')[0].find_elements_by_tag_name('option')
    time.sleep(6)
    for opt in options:
        try:
            if (opt.get_attribute('value')!= ''):
                here = "https://www.transparencycatalog.com/search?number=" + opt.get_attribute('value') + "&q="
                linklist.append(here)
        except:
            print(cnt, "doesnt have value")
        finally:
            cnt += 1

    if len(linklist)==0:
        print("Error happend due to network connection. Try to reconnect!")
        driver.get("https://www.transparencycatalog.com/search?number=&q=")
    else:
        print("Number of links: " + str(len(linklist)))
        break

############################################################
### Function to get data each page
############################################################
def getDataFromCompanies():
    companies = driver.find_element_by_class_name('filtering-products').find_elements_by_class_name('tabs-body-table')
    #iterate on each products
    for company in companies:
        try:
            headerName, headerExpired = company.find_element_by_tag_name('thead').text.split('\n')
            link2Com = company.find_element_by_tag_name('thead').find_element_by_tag_name('a').get_attribute('href')
        except:
            table = {}
            headerName, headerExpired = company.find_element_by_tag_name('tbody').text.split('\n')
            global countPro
            countPro+=1
            table['company_name'] = headerName
            table['header_expired'] = headerExpired
            table['link to company_name'] = company.find_element_by_tag_name('th').find_element_by_tag_name('a').get_attribute('href')
            content.append(table)
            continue
        
        products = company.find_elements_by_tag_name('tbody')
        for x in products:
            inRows = x.find_elements_by_tag_name('tr')[1:]
            for row in inRows:
                obj = {}
                obj['company_name'] = headerName
                obj['header_expired'] = headerExpired
                obj['link to company_name'] = link2Com
                obj["BRAND|PRODUCT"] = row.find_element_by_tag_name('th').text
                countPro+=1
                print(obj["BRAND|PRODUCT"])
                try:
                    obj["Link to BRAND|PRODUCT"] = row.find_element_by_tag_name('th').find_element_by_tag_name('a').get_attribute('href')
                except:
                    obj["Link to BRAND|PRODUCT"] = ""
                try:
                    obj["PROGRAM_ENV"] = row.find_elements_by_tag_name('td')[0].find_element_by_class_name('type').text
                except:
                    obj["PROGRAM_ENV"] = ""
                try:
                    obj["SCOPE, REGION, CO2E, IND AVG_ENV"] = row.find_elements_by_tag_name('td')[0].find_element_by_class_name('scope').text
                except:
                    obj["SCOPE, REGION, CO2E, IND AVG_ENV"] = ""
                try:   
                    obj["EXPIRE_ENV"] = row.find_elements_by_tag_name('td')[0].find_element_by_class_name('expires').text
                except:
                    obj["EXPIRE_ENV"] = ""

                try:
                    obj["PROGRAM_MAT"] = row.find_elements_by_tag_name('td')[1].find_element_by_class_name('program').text
                except:
                    obj["PROGRAM_MAT"] = ""
                try:
                    obj["SCOPE/RESULT_MAT"] = row.find_elements_by_tag_name('td')[1].find_element_by_class_name('results').text
                except:
                    obj["SCOPE/RESULT_MAT"] = ""
                try:
                    obj["EXPIRE_MAT"] = row.find_elements_by_tag_name('td')[1].find_element_by_class_name('expires').text
                except:
                    obj["EXPIRE_MAT"] = ""

                content.append(obj)

############################################################
### BUSY WAITING
############################################################
def busyWaiting():
    isReady = False
    while(not isReady):
        if (driver.find_elements_by_class_name('loading-text')[1].get_attribute('style') == 'display: none;'):
            isReady = True
############################################################
### BUSY WAITING
### Return 1 if end of pagination
############################################################
def nextPageClick():
    lenOfPages = len(driver.find_element_by_class_name('pagination').find_elements_by_tag_name('li'))
    if driver.find_element_by_class_name('pagination').find_elements_by_tag_name('li')[lenOfPages-2].text != "Next":
        return 1
    driver.find_element_by_class_name('pagination').find_elements_by_tag_name('li')[lenOfPages-2].find_element_by_tag_name('a').click()
    return 0
############################################################
### MAIN FUNCTION
############################################################
print("!!!!Starting to crawl data from website!!!!")
countLink = 0
for url in linklist[:5]:
    driver.get(url)
    #loading
    busyWaiting()
    #check if there exists paginatin
    paginTimes = 0
    try:
        paginTimes = len(driver.find_element_by_class_name('pagination').find_elements_by_tag_name('li'))-2
    except:
        paginTimes = 0

    if (paginTimes == 0):
        getDataFromCompanies()
        #print report
        os.system('cls' if os.name == 'nt' else 'clear')
        print(countPro)
        print("Crawling link number " + str(countLink+1) + " of " + str(len(linklist)))
    else:
        #Iterating on pagination
        while True:
            getDataFromCompanies()
            #print report
            os.system('cls' if os.name == 'nt' else 'clear')
            print(countPro)
            print("Crawling link number " + str(countLink+1) + " of " + str(len(linklist)))
            #click to next iter
            if nextPageClick() == 1:
                break
            #wait for loading
            busyWaiting()
    
    write2file()
    countLink+=1
driver.close()
print("Crawl Successful!")