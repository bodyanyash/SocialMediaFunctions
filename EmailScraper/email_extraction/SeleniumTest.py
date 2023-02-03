import csv
import json
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import scrapeEmail
#Setup the selenium web driver
PATH = "chromedriver.exe"
#options = Options()
#options.add_argument("--headless")
driver = webdriver.Chrome(PATH)

def getSingleLocationDetails(url):
    # dict to hold the info for each location
    details = {'name': '', 'address': '', 'website': '', 'phone': '', 'plus-code': '', 'emails': '', 'sent': '0', 'dateSent': '', 'followUp':'0'}

    driver.execute_script(f"window.open('new_window')")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    # wait for the page to load and find the location title
    try:
        locationName = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'header-title-title')]"))
        )
        print("got location title")
    except:
        print("Error getting location details")
        # driver.quit()
        locationName = ''
    details['name'] = locationName.text
    try:
        attributes = driver.find_element_by_class_name("AeaXub")
        try:
            details['address'] = attributes.find_element_by_xpath("//button[starts-with(@aria-label, 'Address')]").text
        except:
            print('no address found')
        try:
            details['website'] = attributes.find_element_by_xpath("//button[starts-with(@aria-label, 'Website')]").text
        except:
            print('no website found')
        try:
            details['phone'] = attributes.find_element_by_xpath("//button[starts-with(@aria-label, 'Phone')]").text
        except:
            print('no phone found')
        try:
            details['plus-code'] = attributes.find_element_by_xpath("//button[starts-with(@aria-label, 'Plus')]").text
        except:
            print('no plus code found')

    except:
        print('error getting details pane')

        print(details)
        time.sleep(2)
        driver.find_element_by_xpath("//button/span[text()='Back to results']").click()
        # driver.back()
        # break
    driver.close();
    driver.switch_to.window(driver.window_handles[0])
    return details

#wait for results to populate and look for main scroll box containing the locations and scroll to get all 20 results
def findMainScrollBox():
    try:
        mainScrollBox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@aria-label='Results for {keyword}']"))
        )
    except:
        driver.quit()
    return mainScrollBox

def ScrollElement(mainScrollBox):
    try:
        pause_time = 1
        max_count = 5
        x = 0

        while (x < max_count):
            # scrollable_div = driver.find_element_by_css_selector(
            #    'div.section-layout.section-scrollbox.scrollable-y.scrollable-show')
            try:
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', mainScrollBox)
            except:
                print("can't scroll")
            time.sleep(pause_time)
            x = x + 1
    except:
        driver.quit()

#Pick a url to start driving
driver.get("https://www.google.com/maps/@36.1482448,-86.7557737,11.25z")
print(driver.title)

#search for keyword in area that url points to
search = driver.find_element_by_id("searchboxinput")
keyword = "General Contractor"
search.send_keys(keyword)
search.send_keys(Keys.RETURN)

#array to hold all the locations
AllDeets = []

#how many pages of results to scrape
pages = 50
for x in range(pages):
    #get the list of the results. Probably need to implement some sort of scrolling to get the reults to load more
    mainScrollBox = findMainScrollBox()

    #scroll the locations to load all 20
    ScrollElement(mainScrollBox)

    #grab all the location in the results array (should be 20 per page)
    results = mainScrollBox.find_elements_by_class_name("a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd")
    print(len(results))

    #click on each result and get the basic info
    for result in results:
        print(result.get_attribute('href'))
        AllDeets.append(getSingleLocationDetails(result.get_attribute('href')))

    try:
        driver.find_element_by_xpath("//button[contains(@jsaction, 'pane.paginationSection.nextPage')]").click()
    except:
        break


print(AllDeets)
driver.quit()
websites = []
for i in range(len(AllDeets)):
    print(i, ' : ', AllDeets[i]['website'])
    if AllDeets[i]['website'] != '':
        websites.append(AllDeets[i]['website'])

scrapeEmail.scrapeEmail(websites)

for i in range(len(AllDeets)):
    if os.path.exists('emailsTemp/'+AllDeets[i]['website']+'.csv'):
        f = open('emailsTemp/'+AllDeets[i]['website']+'.csv', 'r')
        AllDeets[i]['emails'] = f.read().split(',')
        f.close()
    else:
        pass

print(AllDeets)
jsonString = json.dumps(AllDeets)
jsonFile = open("GeneralContractors.json", "w")
jsonFile.write(jsonString)
jsonFile.close()



#remove all temp email files

dir = 'emailsTemp'
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

#do email to clients


#a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd
#rogA2c
#rogA2c HY5zDd
#QSFF4-text gm2-body-2

#time.sleep(5)
#driver.quit()