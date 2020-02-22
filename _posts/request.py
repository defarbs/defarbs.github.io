#!/usr/bin/env python3

import requests
import re
import time

def makeRequest():
    url = ''
    msg = input("Please enter the endpoint to which you would like to make a request: ")
    if(msg = re.match([A-Za-z0-9])):
        print("Making request...")
        exit()
        # make the request
    else:
        print("Illegal characters identified: ")
        time.sleep(0.5)
        makeRequest()
    requests.get(url, allow_redirects=False) # line incomplete

makeRequest()
