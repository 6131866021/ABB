"""
environment = robot studio
agent = robotics
simulate steps = changeData, executeRapid
reward = if move and collision activate = negative
reset = put back the inital robtargetC value

plot the graph of time with epochs

Requirement:
tensorflow > 2.0.0
numpy > ...
"""

from operator import sub
import requests
from ws4py.client.threadedclient import WebSocketClient
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import urllib.parse
import numpy as np
import pandas as pd
import time

host = "http://192.168.1.113:80/"
username = 'Default User'
password = 'robotics'
namespace = '{http://www.w3.org/1999/xhtml}'
digest_auth = HTTPDigestAuth(username, password)
execution = True
train_data = []

class RobWebSocketClient(WebSocketClient):
    def opened(self):
        print("Web Socket connection established")
        startExecution()

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, message):
        if message.is_text:
            stopExecution()
            self.close()
            # print_event(message, '{http://www.w3.org/1999/xhtml}', liclass="ios-signalstate-ev", spanclass="lvalue")
        else:
            print("Received Illegal Event")

class Subscription:
    def __init__(self, host, username, password, resources, priority):
        self.host = host
        self.username = username
        self.password = password
        self.resources = resources
        self.priority = priority
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.subscription_url = self.host + "subscription"
        self.session = requests.Session()

    def subscribe(self):
        rs = len(self.resources)
        resources = [str(i+1) for i in range(rs)]
        payload = {'resources': resources}
        for i in range(rs):
            payload.update({resources[i]:self.resources[i], 
                            resources[i]+'-p':self.priority[i]})
  
        response = self.session.post(self.subscription_url, auth=self.digest_auth, data=payload)
        if response.status_code == 201:
            self.location = response.headers['Location']
            self.cookie = '-http-session-={0}; ABBCX={1}'.format(response.cookies['-http-session-'], response.cookies['ABBCX'])
            return True
        else:
            print('Error subscribing ' + str(response.status_code))
            return False
        
    def start_recv_events(self):
        self.header = [('Cookie', self.cookie)]
        self.ws = RobWebSocketClient(self.location, 
                                    protocols=['robapi2_subscription'], 
                                    headers=self.header)
        self.ws.connect()
        self.ws.run_forever()

    def close(self):
        self.ws.close()

class SymbolData:
    def __init__(self, host, username, password, namespace, robtargetA, robtargetB, robtargetC, clk, episodes):
        self.host = host
        self.username = username
        self.password = password
        self.namespace = namespace
        self.robtargetA = robtargetA
        self.robtargetB = robtargetB
        self.robtargetC = robtargetC
        self.clk = clk
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.session = requests.Session()
        self.episodes = episodes

    def getSymbolData(self, datatype="robtarget"):
        if datatype == "clock":
            url = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.clk
            payload ={}
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = self.session.request("GET", url, headers=headers, data=payload, auth=self.digest_auth)
            # print_event(response.text, self.namespace, liclass="rap-data", spanclass="value")
            self.time = print_event(response.text, self.namespace, liclass="rap-data", spanclass="value")
            return response.status_code == 200
        else:
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

    def changeData(self):
        invalid, randomPoint = True, []
        mean, std = [(self.valueA[0][i]+self.valueB[0][i])/2 for i in range(3)], [abs(self.valueA[0][i]-self.valueB[0][i])/4 for i in range(3)]
        sm = abs(self.valueA[0][2]-self.valueB[0][2])/4
        mean[2] = self.valueA[0][2] + sm if self.valueA[0][2] > self.valueB[0][2] else self.valueB[0][2] + sm
        while invalid:
            randomPoint = [np.random.normal(loc=mean[i], scale=std[i]) for i in range(3)]
            x1, x2 = self.valueA[0][0], self.valueB[0][0]
            y1, y2 = self.valueA[0][1], self.valueB[0][1]
            z1, z2 = self.valueA[0][2], self.valueB[0][2]
            x_valid = (x1 < randomPoint[0] < x2) or (x2 < randomPoint[0] <x1)
            y_valid = (y1 < randomPoint[1] < y2) or (y2 < randomPoint[1] <y1)
            # z_valid = (z1 < randomPoint[2] < z2) or (z2 < randomPoint[2] <z2) 
            # invalid = not(x_valid and y_valid and z_valid)
            # z_valid = (z1 < randomPoint[2] < z2) or (z2 < randomPoint[2] <z2) 
            invalid = not(x_valid and y_valid)

        # When random values are valid, assign to changevalue
        for i in range(3):
            self.changevalue[0][i] = np.round(randomPoint[i], 2)

        self.episodes = self.episodes + 1
        self.urlencode()

    def validateSymbolData(self):
        url = self.host + "rw/rapid/symbol/data?action=validate"
        payload='task=T_ROB1&value=' + self.encodevalue + '&datatype=robtarget'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        if response.status_code != 204:
            print("Error validate symbol data --> Check the changed position '" + str(self.changevalue) + "'") 
        return response.status_code == 204

    def updateSymbolData(self):
        url = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.robtargetC + "?action=setInitValue"
        payload = 'value=' + self.encodevalue
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        if response.status_code == 204:
            print("Update symbol data for robtarget '" + self.robtargetC + "'")
            return True
        else:
            print("Error update symbol data") 
            return False

class Signal:
    def __init__(self, host, username, password, namespace, signal):
        self.host = host
        self.username = username
        self.password = password
        self.namespace = namespace
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.signal = signal
        self.session = requests.Session()
    
    def getSignal(self):
        print()
        # url = self.host + "rw/iosystem/signals/" + self.signal
        # payload={}
        # headers = {
        #     'Content-Type': 'application/x-www-form-urlencoded',
        #     'Cookie': '-http-session-=27::http.session::cd42c3a9ac8c8b0e0a2202a1cfc94a23; ABBCX=40'
        # }
        # response = self.session.request("GET", url, headers=headers, data=payload, auth=self.digest_auth)
        # self.signalvalue = 0
        # print(response.text)
        # # print_event(response.text, self.namespace, liclass="ios-signal", spanclass="lvalue")
        # return response.status_code == 200
    
    def updateSignal(self):
        print('updateSignal')
        # url = self.host + "rw/iosystem/signals/" + self.signal + "?action=set"
        # payload = 'lvalue=1' if self.signalvalue == 0 else 'lvalue=0'
        # headers = {
        # 'Content-Type': 'application/x-www-form-urlencoded'
        # }
        # response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        # return response.status_code == 204

class Execution:
    def __init__(self, host, username, password, namespace, once=False):
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
        payload='regain=continue&execmode=continue&cycle=once&condition=none&stopatbp=disabled&alltaskbytsp=false'
        headers = {
            'Content-Type': 'application/x-www-form-hostencoded',
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
        if response.status_code == 204:
            # print("Start Rapid Execution")
            return True
        else:
            print("Fail to start execution")
            return False
    
    def stopExecution(self):
        url = self.host + "rw/rapid/execution?action=stop"
        payload='regain=continue&execmode=continue&cycle=forever&condition=none&stopatbp=disabled&alltaskbytsp=false'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
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

def startExecution():
    url = host + "rw/rapid/execution?action=startprodentry"
    payload='regain=continue&execmode=continue&cycle=once&condition=none&stopatbp=disabled&alltaskbytsp=false'
    headers = {
        'Content-Type': 'application/x-www-form-hostencoded',
    }
    response = requests.request("POST", url, headers=headers, data=payload, auth=digest_auth)
    if response.status_code == 204:
        print("Start Rapid Execution")
        return True
    else:
        print("Fail to start execution")
        return False
    
def stopExecution():
    url = host + "rw/rapid/execution?action=stop"
    payload='regain=continue&execmode=continue&cycle=forever&condition=none&stopatbp=disabled&alltaskbytsp=false'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.request("POST", url, headers=headers, data=payload, auth=digest_auth)
    if response.status_code == 204:
        print("Stop Rapid Execution")
        return True
    else:
        print("Fail to stop execution")
        return False

def main():
    """Main function to execute class and methods
    > Move to main.py
    """

    host = "http://192.168.1.113:80/"
    username = 'Default User'
    password = 'robotics'
    namespace = '{http://www.w3.org/1999/xhtml}'
    signal = [['/rw/iosystem/signals/di0;state', '/rw/iosystem/signals/di1;state'], ['2', '2']]

    t = [['Target_340', 'Target_350', 'Target_360'], ['Target_370', 'Target_380', 'Target_390']]
    subscriber = Subscription(host, username, password, signal[0], signal[1])
    # symbolData = SymbolData(host, username, password, namespace, 'Target_30', 'Target_310', 'Target_330', 'time', 0)
    # signalData = Signal(host, username, password, namespace, signal)
    rapidExe = Execution(host, username, password, namespace)

    for j in range(2):
        symbolData = SymbolData(host, username, password, namespace, t[j][0], t[j][1], t[j][2], 'time', 0)
        for i in range(100):
            data = []
            print(f"\nEpisodes: {i}")
            if symbolData.getSymbolData():
                symbolData.changeData()
                if symbolData.validateSymbolData():
                    time.sleep(1)
                    symbolData.updateSymbolData()
                    if rapidExe.startExecution():
                        time.sleep(10)
                        rapidExe.stopExecution()
                        symbolData.getSymbolData(datatype="clock")
                        for i in range(len(symbolData.valueA[0])):
                            data.append(symbolData.valueA[0][i])
                        for i in range(len(symbolData.valueB[0])):
                            data.append(symbolData.valueB[0][i])
                        for i in range(len(symbolData.changevalue[0])):
                            data.append(symbolData.changevalue[0][i])
                        data.append(float(symbolData.time[0]))
            train_data.append(data)

    print("\n")
    for j in range(len(train_data)):
        print(train_data[j])


    # for i in range(100):
    #     data = []
    #     print(f"\nEpisodes: {i}")
    #     if symbolData.getSymbolData():
    #         symbolData.changeData()
    #         if symbolData.validateSymbolData():
    #             time.sleep(1)
    #             symbolData.updateSymbolData()
    #             if rapidExe.startExecution():
    #                 time.sleep(10)
    #                 rapidExe.stopExecution()
    #                 symbolData.getSymbolData(datatype="clock")
    #                 for i in range(len(symbolData.valueA[0])):
    #                     data.append(symbolData.valueA[0][i])
    #                 for i in range(len(symbolData.valueB[0])):
    #                     data.append(symbolData.valueB[0][i])
    #                 for i in range(len(symbolData.changevalue[0])):
    #                     data.append(symbolData.changevalue[0][i])
    #                 data.append(float(symbolData.time[0]))
    #     train_data.append(data)

    # print("\n")
    # for j in range(len(train_data)):
    #     print(train_data[j])

    df = pd.DataFrame(train_data, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "time"])
    df.to_csv(r'C:\Users\_\Desktop\ABB\rws_train_9.csv', header=True)

    print(df)

    # try:
    #     if subscriber.subscribe():
    #         subscriber.start_recv_events()
    #         if symbolData.getSymbolData():
    #             while symbolData.episodes < 5:
    #                 print(f"\nEpisodes: {symbolData.episodes}")
    #                 symbolData.changeData()
    #             if symbolData.validateSymbolData():
    #                 symbolData.updateSymbolData()
    #                 startExecution()
    #                 symbolData.getSymbolData(datatype="clock")
    #                 c = []
    #                 for i in range(len(symbolData.changevalue[0])):
    #                     c.append(symbolData.changevalue[0][i])
    #                     t = symbolData.time
    #                     # if signalData.signalvalue != 1:
    #                     #     data.append([t, c])
    #                     data.append([t, c])
    #         data.sort()
    #         print(data)
    # except KeyboardInterrupt:
    #     subscriber.close()

    # if symbolData.getSymbolData():
    #     while symbolData.episodes < 5:
    #         print(f"\nEpisodes: {symbolData.episodes}")
    #         symbolData.changeData()
    #         if symbolData.validateSymbolData():
    #             symbolData.updateSymbolData()
    #             try:
    #                 if subscriber.subscribe():
    #                     subscriber.start_recv_events()
    #             except KeyboardInterrupt:
    #                 subscriber.close()
    #             symbolData.getSymbolData(datatype="clock")
    #             # signalData.getSignal()
    #             c = []
    #             for i in range(len(symbolData.changevalue[0])):
    #                 c.append(symbolData.changevalue[0][i])
    #                 t = symbolData.time
    #                         # if signalData.signalvalue != 1:
    #                         #     data.append([t, c])
    #                 data.append([t, c])

    # data.sort()
    # for i in range(5):
    #     print(data[i])

if __name__ == "__main__":
     main()





# class Login:
#     def __init__(self, host, username, password, namespace):
#         self.host = host
#         self.username = username
#         self.password = password
#         self.namespace = namespace
#         self.digest_auth = HTTPDigestAuth(self.username, self.password)
#         self.session = requests.Session()

#     def localLogin(self):
#         print("In FlexPendant, Toggle 'Enable Button' for 3 times")
#         url = self.host + "users?action=set-locale"
#         payload='type=local'
#         headers = {
#             'Content-Type': 'application/x-www-form-hostencoded',
#         }
#         response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
#         if response.status_code == 200:
#             return True
#         else:
#             print("Try to toggle 'Enable Button' again") 
#             return False
    
#     def requestMastership(self):
#         url = self.host + "rw/mastership?action=request"
#         payload='type=local'
#         headers = {
#         'Content-Type': 'application/x-www-form-hostencoded',
#         }
#         response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
#         if response.status_code == 204:
#             return True
#         else:
#             print("Fail to request mastership") 
#             return False
# class Signal:
#     def __init__(self, host, username, password, namespace, signal):
#         self.host = host
#         self.username = username
#         self.password = password
#         self.namespace = namespace
#         self.digest_auth = HTTPDigestAuth(self.username, self.password)
#         self.signal = signal
#         self.session = requests.Session()
    
#     def getSignal(self):
#         url = self.host + "rw/iosystem/signals/" + self.signal
#         payload={}
#         headers = {
#             'Content-Type': 'application/x-www-form-urlencoded',
#             'Cookie': '-http-session-=27::http.session::cd42c3a9ac8c8b0e0a2202a1cfc94a23; ABBCX=40'
#         }
#         response = self.session.request("GET", url, headers=headers, data=payload, auth=self.digest_auth)
#         self.signalvalue = 0
#         print(response.text)
#         # print_event(response.text, self.namespace, liclass="ios-signal", spanclass="lvalue")
#         return response.status_code == 200
    
#     def updateSignal(self):
#         url = self.host + "rw/iosystem/signals/" + self.signal + "?action=set"
#         payload = 'lvalue=1' if self.signalvalue == 0 else 'lvalue=0'
#         headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#         }
#         response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)
#         return response.status_code == 204
