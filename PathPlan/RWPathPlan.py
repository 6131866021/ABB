from numpy import random
from numpy.core.defchararray import array
import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import urllib.parse
import numpy as np

import time
# import tensorflow as tf

# Fix Status Code 401 Unauthorized

class Login:
    def __init__(self, host, username, password, namespace):
        self.host = host
        self.username = username
        self.password = password
        self.namespace = namespace
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.session = requests.Session()

    def localLogin(self):
        print("In FlexPendant, Toggle 'Enable Button' for 3 times")
        url = self.host + "users?action=set-locale"
        payload='type=local'
        headers = {
            'Content-Type': 'application/x-www-form-hostencoded',
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        if response.status_code == 200:
            return True
        else:
            print("Try to toggle 'Enable Button' again") 
            return False
    
    def requestMastership(self):
        url = self.host + "rw/mastership?action=request"
        payload='type=local'
        headers = {
        'Content-Type': 'application/x-www-form-hostencoded',
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        if response.status_code == 204:
            return True
        else:
            print("Fail to request mastership") 
            return False

class SymbolData:
    def __init__(self, host, username, password, namespace, robtargetA, robtargetB, robtargetC, count):
        self.host = host
        self.username = username
        self.password = password
        self.namespace = namespace
        self.robtargetA = robtargetA
        self.robtargetB = robtargetB
        self.robtargetC = robtargetC
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.session = requests.Session()
        self.count = count # Sample

    def getSymbolData(self):
        host = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/"
        robtarget = [self.robtargetA, self.robtargetB, self.robtargetC]
        url = [host + str(rb) for rb in robtarget]
        payload={}
        headers = {
            'Content-Type': 'application/x-www-form-hostencoded',
        }
        response = [self.session.request("GET", url[0], headers=headers, data=payload, auth=self.digest_auth),
                    self.session.request("GET", url[1], headers=headers, data=payload, auth=self.digest_auth),
                    self.session.request("GET", url[2], headers=headers, data=payload, auth=self.digest_auth)]
        self.valueA = extract_value(print_event(response[0].text, self.namespace, liclass="rap-data", spanclass="value")[0][1:-1].split(',')) if response[0].status_code == 200 else False
        self.valueB = extract_value(print_event(response[1].text, self.namespace, liclass="rap-data", spanclass="value")[0][1:-1].split(',')) if response[1].status_code == 200 else False
        self.valueC = extract_value(print_event(response[2].text, self.namespace, liclass="rap-data", spanclass="value")[0][1:-1].split(',')) if response[2].status_code == 200 else False
        self.changevalue = extract_value(print_event(response[2].text, self.namespace, liclass="rap-data", spanclass="value")[0][1:-1].split(',')) if response[2].status_code == 200 else False
        return response[0].status_code == 200 and response[1].status_code == 200 and response[2].status_code == 200

    def urlencode(self):
        encodevalue = "[["  
        for x in range(3):
            ylistlen = len(self.changevalue[x])
            for y in range(ylistlen):
                if y+1 == ylistlen:
                    encodevalue = encodevalue + str(self.changevalue[x][y]) + '],['
                else:
                    encodevalue = encodevalue + str(self.changevalue[x][y]) + ','
        encodevalue = encodevalue + "9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]]"
        self.encodevalue = urllib.parse.quote_plus(encodevalue)
        print(self.encodevalue)

    def changeData(self):
        # self.changevalue[0][0] = self.changevalue[0][0] + 1
        # self.changevalue[0][1] = self.changevalue[0][1] + 1
        # self.changevalue[0][2] = self.changevalue[0][0] + 2
        # self.changevalue = np.random.randn
        self.changevalue[0][0] = random.uniform(self.valueA[0][0], self.valueB[0][0])
        self.changevalue[0][1] = random.uniform(self.valueA[0][1], self.valueB[0][1])
        self.changevalue[0][2] = random.uniform(self.valueA[0][2], self.valueB[0][2])
        self.count = self.count + 1

    def validateSymbolData(self):
        url = self.host + "rw/rapid/symbol/data?action=validate"
        payload='task=T_ROB1&value=' + self.encodevalue + '&datatype=robtarget'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        print(response.status_code)
        if response.status_code == 204:
            print("Validate symbol data")
            return True
        else:
            print("Error validate symbol data --> Check the changed position '" + str(self.changevalue) + "'") 
            return False

    def updateSymbolData(self):
        url = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.robtarget + "?action=setInitValue"
        payload = 'value=' + self.encodevalue
        print(self.robtarget, payload, self.digest_auth)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        print(response.status_code)
        if response.status_code == 204:
            print("Update symbol data for robtarget '" + self.robtarget + "'")
            return True
        else:
            print("Error update symbol data") 
            return False

class Execution:
    def __init__(self, host, username, password, namespace, once):
        self.host = host
        self.username = username
        self.password = password
        self.namespace = namespace
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.once = once
        self.session = requests.Session()

    def getExecution(self):
        url = self.host + "rw/rapid/execution"
        payload={}
        response = self.session.request("GET", url, data=payload, auth=self.digest_auth)
        return print(response.text)
        # <li class="rap-execution" title="execution">
        #   <span class="ctrlexecstate">stopped</span>
        #   <span class="cycle">forever</span>
        # </li>

    def setExecutionCycle(self):
        url = self.host + "rw/rapid/execution?action=setcycle"
        payload = 'cycle=once' if self.once == True else 'cycle=forever'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': '-http-session-=224::http.session::97bbc6b6cdc2dc5d85a7a02ecbf962e1; ABBCX=12'
        }
        response = requests.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        print(payload, response.text)
        if response.status_code == 204:
            print("Simulation " + payload)
            return True
        else:
            print("Fail to set execution cycle")
            return False
            
    def startExecution(self):
        url = self.host + "rw/rapid/execution?action=startprodentry"
        payload='regain=continue&execmode=continue&cycle=forever&condition=none&stopatbp=disabled&alltaskbytsp=false'
        headers = {
            'Content-Type': 'application/x-www-form-hostencoded',
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        if response.status_code == 204:
            print("Start Rapid Execution")
            return True
        else:
            print("Fail to start execution")
            return False
    
    def stopExecution(self):
        url = self.host + "rw/rapid/execution?action=stop"
        payload='regain=continue&execmode=continue&cycle=forever&condition=none&stopatbp=disabled&alltaskbytsp=false'
        headers = {
            'Content-Type': 'application/x-www-form-hostencoded',
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=auth)
        if response.status_code == 204:
            print("Stop Rapid Execution")
            return True
        else:
            print("Fail to stop execution")
            return False

def print_event(evt, namespace, liclass="", spanclass=""):
    """Extract the API response in the XML format
    with requirement of liclass or spanclass name"""

    root = ET.fromstring(evt)
    data = []
    span = spanclass
    spanclass = "[@class='" + spanclass + "']" if len(spanclass) > 0 else ''
    findRoot = ".//{0}li[@class='" + liclass + "']/{0}span" + spanclass
    for i in range(len(root.findall(findRoot.format(namespace)))):
        data.append(root.findall(findRoot.format(namespace))[i].text)
        print(liclass + " " + span + ": " + root.findall(findRoot.format(namespace))[i].text)
    return data

def extract_value(evt):
    """Get the robtarget value for a function() 
    getSymbolData in class SymbolData"""

    arr = []
    for data in evt:
        removeBracket = [data.find('['), data.find(']')]
        if removeBracket[0] == 0:
            arr.append(float(data[1:]))
        elif removeBracket[1] > 0:
            arr.append(float(data[:-1]))
        else:
            arr.append(float(data))

    return np.array([[arr[0], arr[1], arr[2]], 
                    [arr[3], arr[4], arr[5], arr[6]], 
                    [arr[7], arr[8], arr[9], arr[10]], 
                    [arr[11], arr[12], arr[13], arr[14], arr[15], arr[16]]], dtype=object)

def main():
    """Main function to execute the class and methods"""

    host = "http://192.168.1.113:80/"
    username = 'Default User'
    password = 'robotics'
    namespace = '{http://www.w3.org/1999/xhtml}'

    # login = Login(host, username, password)
    # if login.localLogin():
    #     login.requestMastership()

    symbolData = SymbolData(host, username, password, namespace, 'Target_10', 'Target_30', 'Target_50', 0)
    if symbolData.getSymbolData():
        symbolData.urlencode()
        symbolData.changeData()
        # print(symbolData.changevalue)
    #     if symbolData.validateSymbolData():
    #         symbolData.updateSymbolData()
    # else:
    #     print("Wrong Entry")

    # exe = Execution(host, username, password, once=False)
    # exe.startExecution()

    # clk = SymbolData(host, username, password, 'time', 0)
    # clk.getSymbolData()

if __name__ == "__main__":
     main()