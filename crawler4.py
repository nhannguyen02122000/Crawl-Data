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

lastPagePath = "lastPage4.txt"
chromePath = "chromedriver"
savePath = "out4\out4_from"
url = "https://spot.ul.com/main-app/products/catalog/?keywords=LEED"
driver = webdriver.Chrome(options=chrome_options, executable_path=chromePath)
################################################################
### INITIALIZE
################################################################
print("INITIALIZE ...")
f = open(lastPagePath, "r")
fromPage = int(f.read())+1
amountToCrawl = int(sys.argv[1])
toPage = fromPage + amountToCrawl -1
content = []
errorMessage= ""
print("CRAWLING FROM PAGE " + str(fromPage) + " TO PAGE " +str(toPage))
################################################################
### WRITING FUNCTION
################################################################
def write2file():
    keys = []
    for obj in content:
        for key,value in obj.items():
            if key not in keys:
                keys.append(key)
    
    csv_file = savePath +str(fromPage)+"_to_"+str(toPage)+".csv"
    try:
        with open(csv_file, 'w', encoding="utf-8", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(content)
    except IOError:
        print("I/O error")
################################################################
### INIT BUSY WAIT
################################################################
def initBusyWait():
    isWait = True
    while isWait:
        try:
            if driver.find_elements_by_css_selector('.main-app .preloader-block')[0].get_attribute('hidden'):
                isWait = False
            else:
                isWait = True
        except:
                isWait = True
################################################################
### GET NEXT ITEMS
################################################################
def getNextItems(i):
    if i==1:
        try:
            driver.find_element_by_css_selector('.more>button').click()
        except:
            pass
    else:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        driver.execute_script("document.querySelector('.scroll-top-element').click()")
    time.sleep(1)
    # isWait = True
    # while isWait:
    #     try:
    #         if driver.find_elements_by_css_selector('.main-app .preloader-block')[1].get_attribute('hidden'):
    #             isWait = False
    #         else:
    #             isWait = True
    #     except:
    #             isWait = True
    print("Number of products on page: ",len(driver.find_element_by_css_selector('.results-and-filters .results').find_elements_by_css_selector('.row > .card-container')))
################################################################
### CRAWLING
################################################################
def crawlingPage(i):
    listPro = driver.find_element_by_css_selector('.results-and-filters .results').find_elements_by_css_selector('.row > .card-container')[12*(i-1):12*i]

    while (len(listPro)==0):
        print("Crawl more!")
        getNextItems(2)
        listPro = driver.find_element_by_css_selector('.results-and-filters .results').find_elements_by_css_selector('.row > .card-container')[12*(i-1):12*i]

    for pro in listPro:
        url = pro.find_element_by_css_selector('.info-container-ttl>a').get_attribute('href')
        driver.execute_script("window.open('" + url + "');")
        driver.switch_to.window(driver.window_handles[1])
        initBusyWait()
        table = {}

        try:
            table['title'] = driver.find_element_by_css_selector('.product-detail > .header >h1').text
            print(table['title'])
        except:
            table['title'] = ""
        
        try:
            table['manufacturer'] = driver.find_element_by_css_selector('.manufacturer-info > h2').text
        except:
            table['manufacturer'] = ""
        
        try:
            table['information'] = driver.find_element_by_css_selector('.text-and-images>.paragraph p').text
        except:
            table['information'] = ""

        #certi
        try:
            certifi = driver.find_element_by_css_selector('.documents-box').find_elements_by_css_selector('.col-lg-4')
            certData = ""
            for cert in certifi:
                try:
                    certData += (cert.find_element_by_css_selector('.document-ttl').text+";")
                except:
                    pass
            table['certification_declaration'] = certData
        except:
            table['certification_declaration'] = ""
        
        #category
        category = driver.find_element_by_css_selector('.categories').find_elements_by_css_selector('.list-single')
        for cate in category:
            res = ""
            data = cate.text
            try:
                cate.find_element_by_css_selector('.list-trigger').click()
                List = cate.find_element_by_css_selector('ul').find_elements_by_css_selector('li')
                for li in List:
                    res += (li.text+";")
            except:
                pass
            table[data]=res

        content.append(table)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
################################################################
### MAIN
################################################################
print("GET LINK ...")
driver.get(url)
print("INIT BUSY WAIT ...")
initBusyWait()
time.sleep(5)
print("Required products "+ str(fromPage*12))
#JUMP
print("JUMPING TO PAGE "+ str(fromPage))
for i in range(1,fromPage):
    getNextItems(i)

#Crawl
print("Start crawling ...")
for i in range(fromPage,toPage+1):
    crawlingPage(i)
    write2file()

    os.system('cls' if os.name == 'nt' else 'clear')

    if len(content) != ((i-fromPage+1)*12):
        errorMessage += "Page "+ str(i) + " missing products!\n" 
    print("CRAWLING FROM PAGE " + str(fromPage) + " TO PAGE " +str(toPage))
    print("Crawled: " + str(len(content)) + " products")
    print("Crawled: " + str(i) + " pages")

    f = open(lastPagePath, "w")
    f.write(str(i)) #i
    f.close()

    getNextItems(2)
driver.close()