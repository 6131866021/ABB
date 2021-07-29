import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
from ws4py.client.threadedclient import WebSocketClient
import pandas as pd

from robtarget import *

host = "http://192.168.1.113:80/"
username = 'Default User'
password = 'robotics'
digest_auth = HTTPDigestAuth(username, password)
robtargets = [['pPickTemp', 'pPlaceTemp', 'pGetMid'], ['pPickTemp', 'pPlaceTemp', 'pMidP']]

robtargets_1 = Robtarget(host, username, password, robtargets[0])

# Track robtargets_1 data
track = list()

class Time:
    def __init__(self, host, username, password, timevar):
        """Define Time attribute"""
        self.host = host
        self.username = username
        self.password = password
        self.timevar = timevar
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.session = requests.Session()
    
    def getTime_data(self):
        """GET the data of time by requesting Robot Web Services"""

        # Prepare request params
        url = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.timevar
        payload ={}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = self.session.request("GET", url, headers=headers, data=payload, auth=self.digest_auth)

        # Assign the response value to Time attribute
        self.time = self.extract_value(response.text)
        return response.status_code == 200

    def extract_value(self, response):
        """Extract the value of time from API response in the XML format"""

        # To extract value from XML response, liclass and spanclass names are required
        namespace = '{http://www.w3.org/1999/xhtml}'
        liclass ="rap-data"
        spanclass = "value"

        try:
            root = ET.fromstring(response)
            value = list()
            spanclass = "[@class='" + spanclass + "']" if len(spanclass) > 0 else ''
            findRoot = ".//{0}li[@class='" + liclass + "']/{0}span" + spanclass

            # This loop extracts only values from li-spanclass that are required from the XML response 
            for i in range(len(root.findall(findRoot.format(namespace)))):
                value.append(root.findall(findRoot.format(namespace))[i].text)
                print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
            
            return value[0] if len(value) != 0 else 0.0

        except ET.ParseError:
            pass 

class TimeSubscriber:
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
        """
        Subscribe on RAPID persistent variable on Robot Web Services
        """

        # Prepare request params
        rs = len(self.resources)
        resources = [str(i+1) for i in range(rs)]
        payload = {'resources': resources}
        for i in range(rs):
            payload.update({resources[i]:self.resources[i], 
                            resources[i]+'-p':self.priority[i]})
    
        # Request using POST Methods
        response = self.session.post(self.subscription_url, auth=self.digest_auth, data=payload)
        if response.status_code == 201:
            self.location = response.headers['Location']
            self.cookie = '-http-session-={0}; ABBCX={1}'.format(response.cookies['-http-session-'], response.cookies['ABBCX'])
            self.header = [('Cookie', self.cookie)]
            return True
        else:
            print('Error subscribing ' + str(response.status_code))
            return False
        
    def start_recv_events(self):
        self.ws = RobWebSocketClient(self.location, 
                                     protocols=['robapi2_subscription'], 
                                     headers=self.header)
        self.ws.connect()
        self.ws.run_forever()

    def close(self):
        self.ws.close()
        if len(track) != 0:
            save_df = pd.DataFrame(track, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Time"])
            save_df.to_csv(r'C:\Users\_\Desktop\ABB\PathOptimizer\rws_test_palletizing.csv', header=True)

# This class encapsulates the Web Socket Callbacks functions
class RobWebSocketClient(WebSocketClient):
    def opened(self):
        print("Web Socket connection established (Time)")

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, event_xml):
        if event_xml.is_text:
            print(event_xml)
            track_time(self.extract_value(event_xml.data.decode("utf-8")))
        else:
            print("Received Illegal Event")

    def extract_value(self, response):

        """Extract the value of time from API response in the XML format"""

        # To extract value from XML response, liclass and spanclass names are required
        namespace = '{http://www.w3.org/1999/xhtml}'
        liclass ="rap-value-ev"
        spanclass = "lvalue"

        try:
            root = ET.fromstring(response)
            value = list()
            spanclass = "[@class='" + spanclass + "']" if len(spanclass) > 0 else ''
            findRoot = ".//{0}li[@class='" + liclass + "']/{0}span" + spanclass

            # This loop extracts only values from li-spanclass that are required from the XML response 
            for i in range(len(root.findall(findRoot.format(namespace)))):
                value.append(root.findall(findRoot.format(namespace))[i].text)
                print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
            return value[0]

        except ET.ParseError:
            pass

def track_time(time):
    data = list()
    if robtargets_1.getSymbol_data():
        for i in range(len(robtargets_1.valueA[0])):
            data.append(robtargets_1.valueA[0][i])
        for i in range(len(robtargets_1.valueB[0])):
            data.append(robtargets_1.valueB[0][i])
        for i in range(len(robtargets_1.valueC[0])):
            data.append(robtargets_1.valueC[0][i])
        data.append(float(time))
    print(data)
    track.append(data)