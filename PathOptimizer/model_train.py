import requests
from ws4py.client.threadedclient import WebSocketClient
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import pandas as pd

from robtarget import *
from model import *
from timedata import *
from data import Data

ws = Data()

class ModelTrainSubscriber:
    def __init__(self, host, username, password, resources, priority):
        """Define all Execute Subscriber's attributes."""
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
        Subscribe on IO that used to trigger.
        https://developercenter.robotstudio.com/api/rwsApi/ios_signal_subscribe_page.html
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
        """
        Start receiving events when subscribing the WebSocketClient on Robot Web Services.
        """
        self.ws = RobWebSocketClient(self.location, 
                                     protocols=['robapi2_subscription'], 
                                     headers=self.header)
        self.ws.connect()       # Connects this websocket and starts the upgrade handshake with the remote endpoint.
        self.ws.run_forever()   # Simply blocks the thread until the websocket has terminated.

    def close(self):
        self.ws.close()
        if len(ws.model_train_data) != 0:
            save_df = pd.DataFrame(ws.model_train_data, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Time"])
            save_df.to_csv(ws.model_train_file, header=True, index=False)

class RobWebSocketClient(WebSocketClient):
    def opened(self):
        """This class encapsulates the Web Socket Callbacks functions"""
        print("Web Socket connection established")

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, event_xml):
        """Automatically sends back the provided message to its originating endpoint."""
        if event_xml.is_text:
            self.state = self.extract_value(event_xml.data.decode("utf-8"))
            if self.state == '1':
                get_listdata(len(ws.model_train_round) * ws.save_random)
                ws.model_train_round.append(1)
            elif self.state == '0':
                get_data()
        else:
            print("Received Illegal Event")

    def extract_value(self, response):
        """
        Extract the value of time from API response in the XML format, 
        liclass and spanclass names are required.
        """
        namespace = '{http://www.w3.org/1999/xhtml}'
        liclass ="ios-signalstate-ev"
        spanclass = "lvalue"

        try:
            root = ET.fromstring(response)
            value = list()
            spanclass = "[@class='" + spanclass + "']" if len(spanclass) > 0 else ''
            findRoot = ".//{0}li[@class='" + liclass + "']/{0}span" + spanclass

            # This loop extracts the value from specific li-spanclass in the XML response 
            for i in range(len(root.findall(findRoot.format(namespace)))):
                value.append(root.findall(findRoot.format(namespace))[i].text)
                print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
            return value[0]

        except ET.ParseError:
            pass

def get_listdata(model_train_round):
    if ws.robtargetlist.getSymbol_data():
        random = list()
        for i in range(ws.save_random):
            random.append(randomC_data(ws.robtargetlist.valueA[0], ws.robtargetlist.valueB[0]))
        ws.robtargetlist.changeC_listdata(random)
        print(f"Round {int(model_train_round/ws.save_random)}")
        if ws.robtargetlist.updateC_listdata():
            print('\n')

def randomC_data(a, b):
    """
    This function is the same as in robtarget.py
    Random self.changeC value using normal distribution where
    mean is the point at the center of point A and point B,
    standard deviation is the difference between pointA and pointB
    divided by 8 in each respective coordinate (X, Y, Z)
    """
    validPoint = False
    randomPoint = list()
    mean = [(a[i]+b[i])/2 for i in range(3)]
    std = [abs(a[i]-b[i])/8 for i in range(3)]
    
    # Change Z-Axis Normal Distribution Params
    std[2] = abs(a[2]-b[2])/6
    mean[2] = ((a[2]+b[2])/2)+std[2]

    # While True Loop that will exit when values in X, Y, Z axis are valid
    while not validPoint:
        randomPoint = [np.random.normal(loc=mean[i], scale=std[i]) for i in range(3)]
        x1, x2 = a[0], b[0]
        y1, y2 = a[1], b[1]
        # z1, z2 = a[2], b[2]
        x_valid = (x1 < randomPoint[0] < x2) or (x2 < randomPoint[0] < x1)
        y_valid = (y1 < randomPoint[1] < y2) or (y2 < randomPoint[1] < y1)
        # z_valid = (z1 < randomPoint[2]-std[2] < z2) or (z2 < randomPoint[2]-std[2] < z1) 
        validPoint = x_valid and y_valid
        return_randomC = [np.round(randomPoint[i], 2) for i in range(3)]

    return return_randomC

def get_data():
    """
    Get RAPID Symbol Data of robtargetA, robtargetB, and robtargetC
    that has been used in the motion
    """
    if len(ws.model_train_round) != 0:
        row = list()
        if ws.robtarget.getSymbol_data():
            ws.time.getTime_data()
            for i in range(len(ws.robtarget.valueA[0])):
                row.append(ws.robtarget.valueA[0][i])
            for i in range(len(ws.robtarget.valueB[0])):
                row.append(ws.robtarget.valueB[0][i])
            for i in range(len(ws.robtarget.valueC[0])):
                row.append(ws.robtarget.valueC[0][i])
            row.append(float(ws.time.time))
        ws.model_train_data.append(row)

