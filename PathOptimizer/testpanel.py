import requests
from ws4py.client.threadedclient import WebSocketClient
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import pandas as pd
from param import Data

ws = Data()

class TestSubscriber:
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
        Subscribe on IO that used to trigger
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
        if len(ws.test_data) != 0:
            save_df = pd.DataFrame(ws.test_data, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Time"])
            save_df.to_csv(ws.test_file, header=True, index=False)

class RobWebSocketClient(WebSocketClient):
    def opened(self):
        """This class encapsulates the Web Socket Callbacks functions"""
        print("\n-- Start Testing the model --")
        print("Web Socket connection established")

    def closed(self, code, reason=None):
        print("Closed down", code, reason)

    def received_message(self, event_xml):
        """Automatically sends back the provided message to its originating endpoint."""
        if event_xml.is_text:
            self.state = self.extract_value(event_xml.data.decode("utf-8"))
            if self.state == '1':
                updateC_listdata(len(ws.test_round) * ws.save_random)
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
                print("State: " + root.findall(findRoot.format(namespace))[i].text)
                # print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
            return value[0]

        except ET.ParseError:
            pass

def updateC_listdata(test_round):
    """Update values of the robtargetC List by predicted values"""
    df = pd.read_csv(ws.predict_file)
    prediction = list()
    for i in range(ws.save_random):
        row = df.iloc[test_round + i]
        prediction.append([row['C_X'], row['C_Y'], row['C_Z']])
    if ws.robtargetlist.getSymbol_data():
        ws.robtargetlist.changeC_listdata(prediction)
        print(f"\nTest Round: {int(test_round/ws.save_random)+1}")
        if ws.robtargetlist.updateC_listdata():
            ws.test_round.append(1)

def get_data():
    """
    Get RAPID Symbol Data of robtargetA, robtargetB, and robtargetC
    that has been used in the motion
    """
    if len(ws.test_round) != 0:
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
        ws.execute_data.append(row)
