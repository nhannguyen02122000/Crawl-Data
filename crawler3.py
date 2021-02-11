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
chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')

lastPagePath = "/Users/nhannguyen/Documents/Crawl-Data/lastPage3.txt"
chromePath = "/Users/nhannguyen/Documents/crawlerFB/chromedriver"
savePath = "/Users/nhannguyen/Documents/CRAWL-DATA/out3_from"
url = "https://origin.build/#/materials?p=P&locale=en&page=0&gacreditid=100000060&q="
################################################################
### INITIALIZE
################################################################
print("INITIALIZE ...")
f = open(lastPagePath, "r")
fromPage = int(f.read())+1
amountToCrawl = int(sys.argv[1])
toPage = fromPage + amountToCrawl -1
driver = webdriver.Chrome(options=chrome_options, executable_path=chromePath)
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
            text = driver.find_elements_by_class_name('material-count-info')[1].find_elements_by_tag_name('span')[0].text
            print(text)
            isWait = False
        except:
            isWait = True
################################################################
### NEW WEB BUSY WAIT
################################################################
def initNewWebWait():
    isWait = True
    while isWait:
        try:
            driver.find_element_by_class_name('detail-container-main-content-body')
            isWait = False
        except:
            isWait = True
################################################################
### SET LISTVIEW FUNC
################################################################
def setListView():
    driver.find_elements_by_class_name('giga-action-button')[0].click()
    time.sleep(5)
################################################################
### CRAWL FUNC
################################################################
def crawlFromPage(index):
    table = driver.find_element_by_class_name('manual-data-table__table').find_elements_by_tag_name('tbody')[index] #First page
    for row in table.find_elements_by_tag_name('tr')[1:]:
        table = {}
        link = row.find_elements_by_tag_name('td')[2].find_element_by_tag_name('a').get_attribute('href')
        driver.execute_script("window.open('" + link + "');")
        driver.switch_to.window(driver.window_handles[1])
        initNewWebWait()

        #getdata
        try:
            table['title'] = driver.find_element_by_class_name('material-company-info').find_element_by_tag_name('h3').text
            print(table['title'])
        except:
            table['title'] = ""
        try:
            table['subtitle'] = driver.find_element_by_class_name('material-company-info').find_element_by_tag_name('p').text
        except:
            table['subtitle'] = ""
        try:
            table['subtitle_link'] = driver.find_element_by_class_name('material-company-info').find_element_by_tag_name('p').find_element_by_tag_name('a').get_attribute('href')
        except:
            table['subtitle_link'] = ""
        #body
        body = driver.find_element_by_class_name('detail-container-main-content-body')
        #section1
        section1 = body.find_elements_by_tag_name('section')[0].find_element_by_tag_name('article').find_elements_by_class_name('single-material-attribute')
        for row in section1:
            key = row.find_elements_by_tag_name('div')[0].text
            value = row.find_elements_by_tag_name('div')[1].text
            if (value == "Link"):
                value = row.find_elements_by_tag_name('div')[1].find_element_by_tag_name('a').get_attribute('href')
            table[key] = value
        #section2
        section2 = body.find_elements_by_tag_name('section')[1].find_element_by_tag_name('tbody')
        for row in section2.find_elements_by_tag_name('tr')[1:]:
            key = "Qualifier_" + row.find_elements_by_tag_name('td')[0].text
            value = row.find_elements_by_tag_name('td')[1].text
            table[key] = value
        #contact
        try:
            contact = driver.find_element_by_id('contacts-section')
            contact.click()
            listOfContact = contact.find_element_by_tag_name('article').find_element_by_class_name('panel-group').find_elements_by_class_name('panel-default')
            i = 0
            for con in listOfContact:
                i+=1
                data = ""
                con.click()
                para = con.find_element_by_class_name('panel-collapse').find_element_by_class_name('panel-body').find_elements_by_tag_name('p')
                for p in para:
                    if (p.text == "Company Page"):
                        data += (p.find_element_by_tag_name('a').get_attribute('href') +",")
                    else:
                        data += (p.text +",")
                table["contact_"+str(i)] = data
        except:
            pass
        #feature
        try:
            feature = driver.find_element_by_id('features-section')
            feature.click()
            listOfFeature = driver.find_elements_by_css_selector('.detail-content-features-list>div')[:-1]
            for feat in listOfFeature:
                key = feat.find_element_by_class_name('key-value-cell-key').text
                value = feat.find_element_by_class_name('key-value-cell-value').text
                table[key] = value
        except:
            pass
        #certification
        try:
            certification = driver.find_element_by_css_selector('#certifications-section>article').find_elements_by_css_selector('.material-detail-info-block')[0]
            listOfCerti = certification.find_elements_by_css_selector('section>.material-detail-certification-block')
            value = ""
            for certi in listOfCerti:
                name = certi.find_elements_by_css_selector('.key-value-row>.key-value-cell-value')[0].text
                value += (name+",")
            table['certifications'] = value
        except:
            pass
        #declarations
        try:
            declaration = driver.find_element_by_css_selector('#certifications-section>article').find_elements_by_css_selector('.material-detail-info-block')[1]
            listOfDecl = declaration.find_elements_by_css_selector('section>.material-detail-certification-block')
            value = ""
            for decl in listOfDecl:
                name = decl.find_elements_by_css_selector('.key-value-row>.key-value-cell-value')[0].text
                value += (name+",")
            table['declaration'] = value
        except:
            pass
        content.append(table)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
################################################################
### MAIN
################################################################
print("GET LINK ...")
driver.get(url)
initBusyWait()
setListView()

#jump to page
for i in range(1,fromPage):
    #Load more
    driver.find_element_by_css_selector('.manual-datatable__load-more-cell>a').click() 
    isWait = True
    while isWait:
        try:
            driver.find_element_by_class_name('manual-data-table__table').find_elements_by_tag_name('tbody')[i+2]
            isWait = False
        except:
            isWait = True

for i in range(fromPage,toPage+1):
    crawlFromPage(i)
    #Load more
    driver.find_element_by_css_selector('.manual-datatable__load-more-cell>a').click() 
    isWait = True
    while isWait:
        try:
            driver.find_element_by_class_name('manual-data-table__table').find_elements_by_tag_name('tbody')[i+2]
            isWait = False
        except:
            isWait = True
    #Print report
    os.system('cls' if os.name == 'nt' else 'clear') 
    print("CRAWLING FROM PAGE " + str(fromPage) + " TO PAGE " +str(toPage))
    print("Crawled: " + str(len(content)) + " products")
    print("Crawled: " + str(i) + " pages")
    f = open(lastPagePath, "w")
    f.write(str(i))
    f.close()
driver.close()
write2file()