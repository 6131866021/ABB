import numpy as np
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import urllib.parse
import numpy as np

# Below function change robtargetA and robtargetB in order to train the robot

def changeTrainData(self, valueA, valueB):
    for i in range(3):
        self.valueA[0][i] = valueA[i]
        self.valueB[0][i] = valueB[i]
    constant = "],[0,0.707106781,0.707106781,0],[0,0,0,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]]"
    self.encodevalues = [urllib.parse.quote_plus("[[" + str(valueA[0]) + "," + str(valueA[1]) + "," + str(valueA[2]) + constant),
                         urllib.parse.quote_plus("[[" + str(valueB[0]) + "," + str(valueB[1]) + "," + str(valueB[2]) + constant)]

def updateTrainSymbolData(self):
    url = [self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.robtargetA + "?action=setInitValue",
           self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.robtargetB + "?action=setInitValue"]
    payload = ['value=' + encode for encode in self.encodevalues]
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = [requests.request("POST", url[1], headers=headers, data=payload[1], auth=self.digest_auth),
                requests.request("POST", url[0], headers=headers, data=payload[0], auth=self.digest_auth)]
    if response[0].status_code == 204 and response[1].status_code == 204:
        return True
    else:
        print("Error update train symbol data") 
        return False