from selenium import webdriver
import time
import threading
import re
import os
from datetime import date

#gather inputs. need URL, username, password (and eventually secret question)
print("Enter Idaptive client management portal (format: 'https://CLIENTDOMAIN.my.centrify.com/manage':")
idaptiveURL = input()
print("Enter username:")
username = input()
print("Enter password:")
pw = input()

# regex to pull just the first part of domain to be used to save file as later
domainRegEx = re.compile(r'(?<=\//)(.*?)(?=\.)')
clientFromURL = domainRegEx.search(idaptiveURL)

#Save excel file as "date_clientdomain"
exportFileAs = str(date.today()) + '_' + str(clientFromURL.group())
print(exportFileAs)

#custom Firefox profile (for autodownloading: https://selenium-python.readthedocs.io/faq.html#how-to-auto-save-files-using-custom-firefox-profile
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList",2)
fp.set_preference("browser.download.manager.showWhenStarting",False)
fp.set_preference("browser.download.dir", os.getcwd())
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

browser = webdriver.Firefox(firefox_profile=fp)
browser.get(idaptiveURL)

#used for inputting text into webpage. Will retry x number of times. 
def waitForPageLoad(attemptsToTry, element, entry):
    try:
        foundElement = browser.find_element_by_css_selector(element)
        print('true!')
        foundElement.click()
        foundElement.send_keys(entry)

    except:
        print('not loaded ' + element + '. ' + str(attemptsToTry) + ' attempts left')
        if attemptsToTry > 0:
            time.sleep(3)
            waitForPageLoad(attemptsToTry - 1, element, entry)
        else:
            return False

#used for inputting click events to webpage. Will retry x number of times
def clickNext(attemptsToTry, element):
    try:
        next = browser.find_element_by_css_selector(element)
        next.click()
    except:
        print('not loaded ' + element + '. ' + str(attemptsToTry) + ' attempts left')
        if attemptsToTry > 0:
            time.sleep(3)
            clickNext(attemptsToTry - 1, element)
        else:
            return False

#not need at this time
def findByText(attemptsToTry, element):
    try:
        xPathSearch = "//*[text()='" + element + "']"
        print('searching ' + xPathSearch)
        next = browser.find_element_by_xpath(xpathSearch)
        next.click()
    except:
        print('not loaded ' + element + '. ' + str(attemptsToTry) + ' attempts left')
        if attemptsToTry > 0:
            time.sleep(6)
            clickNext(attemptsToTry - 1, element)
        else:
            return False


#stops for walking through Idaptive webpage to download custom report
waitForPageLoad(6, '#usernameForm > div:nth-child(3) > div:nth-child(1) > input:nth-child(2)', username) #username login
clickNext(3, '#usernameForm > div.button-wrapper > button') #username click next
waitForPageLoad(5, '#passwordForm > div.form-field-container > div > input[type=password]', pw) #pw entry
clickNext(3, '#passwordForm > div:nth-child(4) > button:nth-child(2)') #pw click next
clickNext(3, '#nav-part-Reporting-Reports > td:nth-child(1) > div:nth-child(1) > a:nth-child(4)') #click on 'report'
clickNext(3, '.x-grid-row-checker') #click the custom report
clickNext(3, "a[buttontext='Actions']") #click 'action' button
clickNext(3, "div[test-text='Export Report']") #export report
clickNext(3, "input[inputvalue='Excel']") #'Excel' radio button
waitForPageLoad(5, 'input[name="fileName"]', exportFileAs) #save file as
clickNext(3, "a[buttontext='OK']") # click 'ok'



