import time
import re
import os
from datetime import date
import requests
import json
import bs4
import csv

# takes results in json file and desired filename and saves to CSV file. Will save to current working directory
def createReport(jsonReport, fileName):
    csvReport = open(fileName + '.csv', 'w')

    parsedReportData = jsonReport['Result']['Results']
    csv_writer = csv.writer(csvReport)

    count = 0

    for dat in parsedReportData:
        if count == 0:
            header = dat["Row"].keys()
            csv_writer.writerow(header)
            count +=1
        
        csv_writer.writerow(dat["Row"].values())

    csvReport.close()

#gather inputs. need URL, username, password (and eventually secret question)
print("Enter Idaptive client management portal (use format: 'https://CLIENTDOMAIN.my.centrify.com':")
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

#Set headers and payload to begin user authentication
headers = {
    "X-IDAPTIVE-NATIVE-CLIENT":"true",
    "Content-Type": "application/json"
}

payload = {
    "User": username,
    "Version": "1.0"
}

#authenticaton  is a two step process:
#   first /Security/StartAuthentication returns tenantId, SessionId, and mechanismId
#   pass that info on to /Security/AdvanceAuthentication to get the authentication token

#start new session
page = requests.Session()
res = page.post(idaptiveURL + '/Security/StartAuthentication', headers=headers, json=payload)
print(res)

## initial auth started. Save these variables:
json_page = json.loads(res.text) # convert to json
TenantId = json_page['Result']['TenantId'] # gets tenant id of client
SessionId = json_page['Result']['SessionId'] # gets the session id so authentication can be advanced
MechanismId = json_page['Result']['Challenges'][0]['Mechanisms'][0]['MechanismId'] #mechanism id:

# prep payload including username and pw for next auth sequence
authPayload = {
    "TenantId": TenantId,
    "SessionId": SessionId,
    "MechanismId": MechanismId,
    "Action": "Answer",
    "Answer": pw
}

# next auth sequesnce
authRequestPage = requests.Session()
res = authRequestPage.post(idaptiveURL + '/Security/AdvanceAuthentication', headers=headers, json=authPayload)
authRequestPage_json = json.loads(res.text)
print(authRequestPage_json['success'])
print(authRequestPage_json['Result']['AuthLevel'])
authToken = 'Bearer ' + authRequestPage_json['Result']['Auth']
print(authToken)

# update header to include authorization token
headers = {
    "X-IDAPTIVE-NATIVE-CLIENT":"true",
    "X-CENTRIFY-NATIVE-CLIENT":"true", #this is the required header the API doc doesn't tell you about
    "Content-Type": "application/json",
    'Authorization': authToken
}

dbQuery = {
    "Script":
    "SELECT User.DisplayName, User.Email, User.StatusEnum FROM User WHERE User.StatusEnum = 'Active' ORDER BY User.Email"
    }

# send api request including sql request of report needed
response = authRequestPage.post(idaptiveURL + '/Redrock/query', headers=headers, json=dbQuery)

report = json.loads(response.text)
print(report['Result']['Results'])

#pass results into function to save report to HDD
createReport(report, exportFileAs)