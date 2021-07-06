import sys, argparse
import xml.etree.ElementTree as ET
from ws4py.client.threadedclient import WebSocketClient
import requests
from requests.auth import HTTPDigestAuth

import DigestAuth as DigestAuth
import RapidExecution as RapidExecution
import RapidSymbolData as RapidSymbolData

class UserService:
    def __init__(self, host, user, passcode):
        self.host = host
        self.auth = auth
        self.status = status

    def login(self):
        if self.status != 409:
            self.status = DigestAuth.local_login()
    
    def request_mastership(self):
        if self.status == 200:
            DigestAuth.request_mastership()

def setup():
    host = "http://192.168.1.113:80/"
    auth = HTTPDigestAuth('Default User', 'robotics')
    userService = UserService(host, auth, None)
    status =  userService.login()
    masterstatus = userService.request_mastership() if userService.status == 200 else userService.login()
    return masterstatus

# def execute():
#     # RapidSymbolData.validateVariable([[5,5,5],[0,0,1,0],[0,0,-2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]])
#     # RapidSymbolData.updateSymbolData(data='Target_50')
#     # RapidExecution.startRapidExecution()

# # execute()