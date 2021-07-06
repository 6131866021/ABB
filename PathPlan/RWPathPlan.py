import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import urllib.parse

# Fix Status Code 401 Unauthorized

class Login:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
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
    def __init__(self, host, username, password, robtarget, count):
        self.host = host
        self.username = username
        self.password = password
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.robtarget = robtarget
        self.session = requests.Session()
        self.count = count # Sample

    def getSymbolData(self):
        url = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + str(self.robtarget)
        payload={}
        headers = {
        'Content-Type': 'application/x-www-form-hostencoded',
        'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
        }
        response = self.session.request("GET", url, headers=headers, data=payload, auth=self.digest_auth)
        if response.status_code == 200:
            self.initvalue = [[6,6,6],[0,0,1,0],[0,0,-2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]] # Sample
            self.changevalue = [[6,6,6],[0,0,1,0],[0,0,-2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]] # Sample
            print(response.text)
            return True
            # print this <li class="rap-data" title="RAPID/T_ROB1/user/reg1"> <span class="value">0</span>
        else:
            print("Error get symbol data --> robtarget '" + self.robtarget + "'")
            return False
    
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
        self.changevalue[0][0] = self.changevalue[0][0] + 1
        self.changevalue[0][1] = self.changevalue[0][1] + 1
        self.changevalue[0][2] = self.changevalue[0][0] + 2
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
    def __init__(self, host, username, password, once):
        self.host = host
        self.username = username
        self.password = password
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

def main():
    host = "http://192.168.1.113:80/"
    username = 'Default User'
    password = 'robotics'

    symbolData = SymbolData(host, username, password, 'Target_50', 0)
    # if symbolData.getSymbolData():
    #     symbolData.urlencode()
    #     if symbolData.validateSymbolData():
    #         symbolData.updateSymbolData()
    # else:
    #     print("Wrong Entry")

    exe = Execution(host, username, password, once=False)
    exe.startExecution()

    clk = SymbolData(host, username, password, 'time', 0)
    clk.getSymbolData()

if __name__ == "__main__":
     main()