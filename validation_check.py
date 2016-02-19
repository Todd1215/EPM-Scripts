#!/usr/bin/python

# imports
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import httplib2
import requests
import sys
import thread

components = {} #maintain a dictionary of components and their properties
                #accessible via components[component_name][property]

red='\033[31m'
yellow='\033[33m'
green='\033[32m'
reset='\033[0m'

threshold_good=5   #in seconds
threshold_warning_low=6    #in seconds
threshold_warning_high=10   #in seconds
threshold_bad=11    #in seconds

def load_registry( file ):
    "Load registry dictionary"
    soup = BeautifulSoup(open(file))
    divs = soup.find_all("div", {"class":"info"})
    for div in divs:
        if div.find("a", id=True):
            component_name = div("b")[0]
            component_name = component_name.string
            table = div.find_next("table", {"class":"properties"})
            rows = table.find_all("tr", {"class":None})
            rowd = {}
            for row in rows:
                cells = row.find_all("td")
                rowd[cells[0].text] = cells[1].text
                components[component_name] = rowd
    return

def check_requests_url( url ):
    "check the URL and report status and timings using requests module"
    r = requests.get( url )
    return (r.status_code, r.reason, r.elapsed.total_seconds())

try:
    registry_file = sys.argv[1]
    print("Loading registry file: " + registry_file)
    load_registry(registry_file)
    t = PrettyTable(['Elapsed','Status','Message','URL'])
    t._align['URL'] = 'l'
    t.header_style = 'title'
    for component in components:
        if ('validationContext') in components[component]:
            validation_context = components[component]["validationContext"]
            validation_contexts = validation_context.split()
            for validation_context in validation_contexts:
              url_string = "http://" + components["WORKSPACE_LWA"]["host"] + ":" + components["WORKSPACE_LWA"]["port"] + "/" + validation_context
              (status, reason,elapsed) = check_requests_url(url_string)
              if status != 200:
                  t.add_row([elapsed, red + str(status) + reset, reason, url_string])
              else:
                  if elapsed < threshold_good:
                      t.add_row([elapsed, green + str(status) + reset, reason, url_string])
                  elif elapsed > threshold_warning_low and elapsed < threshold_warning_high:
                      t.add_row([yellow + str(elapsed) + reset, status, reason, url_string])
                  elif elapsed > threshold_bad:
                      t.add_row([red + str(elapsed) + reset, status, reason, url_string])
    print (t)
except:
    print('pass the registry file on the command line to process validation URLs')
