from logging import error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import argparse
import csv
import json
import selenium.common.exceptions
import os
chrome_options = Options()
chrome_options.add_argument("--headless")

################################################################
### INITIALIZE
################################################################
print("INITIALIZE ...")
url = "https://materialsforleed.ecomedes.com/?query="
driver = webdriver.Chrome(
            options=chrome_options, executable_path="/Users/nhannguyen/Documents/crawlerFB/chromedriver")
content = []
errorMessage= ""
################################################################
### WRITING FUNCTION
################################################################
def write2file():
    keys = []
    for obj in content:
        for key,value in obj.items():
            if key not in keys:
                keys.append(key)
    
    csv_file = "/Users/nhannguyen/Documents/crawlerFB/out.csv"
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for data in content:
                writer.writerow(data)
    except IOError:
        print("I/O error")
################################################################
### Crawl data
################################################################
def crawlFromPage():
    listOfPict = driver.find_element_by_class_name('search-results').find_elements_by_class_name('col-sm-4')
    for pict in listOfPict:
        productURL = pict.find_element_by_tag_name('a').get_attribute('href')
        driver.execute_script("window.open('" + productURL + "');")
        driver.switch_to.window(driver.window_handles[1])
        table = {}
        #THUC THI
        #TODO
        title = driver.find_element_by_class_name('product-header').find_element_by_tag_name('h3').text
        subtitle = driver.find_element_by_class_name('product-header').find_element_by_tag_name('small').text
        title = title.split(subtitle)[0]
        table['title'] = title
        table['subtitle'] = subtitle
        print(table['title'], table['subtitle'])
        
        try:
            category = driver.find_element_by_class_name('dl-horizontal').text.split('\n')[1]
            table['category'] = category
        except:
            table['category'] = ""
        try:
            Subcategory = driver.find_element_by_class_name('dl-horizontal').text.split('\n')[3]
            table['Subcategory'] = Subcategory
        except:
            table['Subcategory'] = ""
        try:
            description = driver.find_element_by_class_name('description').find_element_by_tag_name('p').text
            table['description'] = description
        except:
            table['description'] = ""

        infoTables = driver.find_element_by_class_name('product-lenses').find_elements_by_tag_name('table')
        #GENERAL
        try:
            general = infoTables[0].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            for row in general:
                key = row.find_elements_by_tag_name('td')[0].text
                data = row.find_elements_by_tag_name('td')[1].text
                if data == "External Linkgo":
                    table[key] = row.find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').get_attribute('href')
                else:
                    table[key] = data
        except:
            pass

        #VERIFY
        try:
            verify = infoTables[1].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            for row in verify:
                key = row.find_elements_by_tag_name('td')[0].text
                data = row.find_elements_by_tag_name('td')[1].text
                if data == "External Linkgo":
                    table[key] = row.find_elements_by_tag_name('td')[1].find_element_by_tag_name('a').get_attribute('href')
                else:
                    table[key] = data
        except:
            pass

        #TECH
        try:
            techinfo = infoTables[2].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            for row in techinfo:
                key = row.find_elements_by_tag_name('td')[0].text
                value = None
                try:
                    value = row.find_element_by_tag_name('a').get_attribute('href')
                except:
                    value = row.find_elements_by_tag_name('td')[1].text
                table[key] = value
        except:
            pass
        ##############
        content.append(table)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
################################################################
### MAIN
################################################################
print("GET LINK ...")
driver.get(url)
print("!!! START CRAWLING !!!")
noOfPages = 0
#detect pagination
while 1:
    noOfPages += 1
    crawlFromPage()
    pages = len(driver.find_element_by_class_name('pagination').find_elements_by_tag_name('li'))
    driver.find_element_by_class_name('pagination').find_elements_by_tag_name('li')[pages-1].find_element_by_tag_name('a').click()
    write2file()
    time.sleep(5)
    os.system('cls' if os.name == 'nt' else 'clear')

    if len(content) != (noOfPages*18):
        errorMessage += "Page "+ str(noOfPages) + " missing products!\n" 
    print("Crawled: " + str(len(content)) + " products")

driver.close()
