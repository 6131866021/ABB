import requests
from ws4py.client.threadedclient import WebSocketClient
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

from robtarget import *
from model import Model
from timedata import Time

host = "http://192.168.1.113:80/"
username = 'Default User'
password = 'robotics'
digest_auth = HTTPDigestAuth(username, password)
robtargets = [['pPickTemp', 'pPlaceTemp', 'pGetMid'], ['pPickTemp', 'pPlaceTemp', 'pMidP']]

robtargets_1 = Robtarget(host, username, password, robtargets[0])
robtargets_2 = RobtargetList(host, username, password, robtargets[1])
time = Time(host, username, password, 'time')
model = Model()

prediction = list()
train_data = list()

df = pd.read_csv('rws_predict.csv')
count = list()

# Track robtargets_1 data
track = list()


class Subscriber:
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
        print("Web Socket connection established")

    def closed(self, code, reason=None):
        # save_df = pd.DataFrame(track, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Time"])
        # save_df.to_csv(r'C:\Users\_\Desktop\ABB\PathOptimizer\rws_test_palletizing.csv', header=True)
        print("Closed down", code, reason)

    def received_message(self, event_xml):
        if event_xml.is_text:
            self.state = self.extract_value(event_xml.data.decode("utf-8"))
            if self.state == '1':
                # changedata_usingpredict(len(count) * 10)
                count.append(1)
            elif self.state == '0':
                track_time()
        else:
            print("Received Illegal Event")

    def extract_value(self, response):

        """Extract the value of time from API response in the XML format"""

        # To extract value from XML response, liclass and spanclass names are required
        namespace = '{http://www.w3.org/1999/xhtml}'
        liclass ="ios-signalstate-ev"
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

        # liclass = "rap-value-ev"

        # try:
        #     root = ET.fromstring(response)
        #     value = list()
        #     spanclass = "[@class='" + spanclass + "']" if len(spanclass) > 0 else ''
        #     findRoot = ".//{0}li[@class='" + liclass + "']/{0}span" + spanclass

        #     # This loop extracts only values from li-spanclass that are required from the XML response 
        #     for i in range(len(root.findall(findRoot.format(namespace)))):
        #         value.append(root.findall(findRoot.format(namespace))[i].text)
        #         print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
        #     return value[0]

        # except ET.ParseError:
        #     pass


def changedata_usingpredict(c):
    prediction = list()
    for i in range(10):
        row = df.iloc[c + i]
        prediction.append([row['C_X'], row['C_Y'], row['C_Z']])
    if robtargets_2.getSymbol_data():
        robtargets_2.changeC_listdata(prediction)
        if robtargets_2.updateC_listdata():
            print(f"Change Data Row: {c}\n")


def train_Data():
    X_test = list()
    if robtargets_1.getSymbol_data():
        d = list()
        for a in range(3):
            d.append(robtargets_1.valueA[0][a])
        for b in range(3):
            d.append(robtargets_1.valueB[0][b])
        # Real C value
        for c in range(3):
            d.append((robtargets_1.valueA[0][c] + robtargets_1.valueB[0][c])/2)
        X_test.append(d)   
        for i in range(100):
            data = list()
            robtargets_1.randomC_data()
            for a in range(3):
                data.append(robtargets_1.valueA[0][a])
            for b in range(3):
                data.append(robtargets_1.valueB[0][b])
            for c in range(3):
                data.append(robtargets_1.changeC[0][c])
            X_test.append(data)
    
    X_test = pd.DataFrame(X_test, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z"])
    y_preds = add_ypreds(X_test, model.predict(X_test))
    y_preds.sort_values('Predict Time', inplace=True)

    prediction.append(y_preds.iloc[10]['C_X'])
    prediction.append(y_preds.iloc[10]['C_Y'])
    prediction.append(y_preds.iloc[10]['C_Z'])

    print(prediction)


def retrieve_Data():
    data = list()
    if robtargets_2.getSymbol_data():
        for i in range(len(robtargets_2.valueA[0])):
            data.append(robtargets_2.valueA[0][i])
        for i in range(len(robtargets_2.valueB[0])):
            data.append(robtargets_2.valueB[0][i])
    train_data.append(data)


def changeData():
    # X_test = list()

    # valueA = [1670.0,-880.0,1205.0]
    # valueB = [210.0,-2675.0,672.0]
    # 1670.0,-880.0,1205.0,2.58

    print('Change Data')
    if robtargets_2.getSymbol_data():
    #     d = list()
    #     for a in range(3):
    #         d.append(robtargets_1.valueA[0][a])
    #     for b in range(3):
    #         d.append(robtargets_1.valueB[0][b])
    #     # Real C value
    #     for c in range(3):
    #         d.append((robtargets_1.valueA[0][c] + robtargets_1.valueB[0][c])/2)
    #     X_test.append(d)

    #     for i in range(100):
    #         data = list()
    #         robtargets_2.randomC_data()
    #         for a in range(3):
    #             data.append(robtargets_2.valueA[0][a])
    #         for b in range(3):
    #             data.append(robtargets_2.valueB[0][b])
    #         for c in range(3):
    #             data.append(robtargets_2.changeC[0][c])
    #         X_test.append(data)
    
    # X_test = pd.DataFrame(X_test, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z"])
    # y_preds = add_ypreds(X_test, model.predict(X_test))
    # y_preds.sort_values('Predict Time', inplace=True)
    
    # changeC = [y_preds.iloc[0]['C_X'], y_preds.iloc[0]['C_Y'], y_preds.iloc[0]['C_Z']]
    
        robtargets_2.changeC_data(prediction)

        if robtargets_2.validateC_data():
            robtargets_2.updateC_data()


def add_ypreds(X_test, y_preds):
    df = list()
    for i in range(len(X_test)):
        row = list(X_test.iloc[i])
        row.append(np.mean(y_preds[i]))
        df.append(row)
    return pd.DataFrame(df, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Predict Time"])


def show_time():
    time.getTime_data()


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


def track_time():
    print('track time')
    if len(count) != 0:
        data = list()
        if robtargets_1.getSymbol_data():
            time.getTime_data()
            for i in range(len(robtargets_1.valueA[0])):
                data.append(robtargets_1.valueA[0][i])
            for i in range(len(robtargets_1.valueB[0])):
                data.append(robtargets_1.valueB[0][i])
            for i in range(len(robtargets_1.valueC[0])):
                data.append(robtargets_1.valueC[0][i])
            data.append(float(time.time))
        track.append(data)


# def save_track():



# def palletizing():
#     for i in range(30):
#         data = []
#         print(f"Episodes: {i}")
#         # symbol_data.append(robtargets_2(host, username, password, namespace, 'pPickTemp', 'pPlaceTemp', 'pMidP', 'time', 0))
#         robtargets_2 = robtargets_2(host, username, password, namespace, 'pPickTemp', 'pPlaceTemp', 'pMidP', 'time', 0)
#         if robtargets_2.getrobtargets_2():
#             robtargets_2.getrobtargets_2(datatype="clock")
#             for i in range(len(robtargets_2.valueA[0])):
#                 data.append(robtargets_2.valueA[0][i])
#             for i in range(len(robtargets_2.valueB[0])):
#                 data.append(robtargets_2.valueB[0][i])
#             for i in range(len(robtargets_2.changevalue[0])):
#                 data.append(robtargets_2.changevalue[0][i])
#             data.append(float(robtargets_2.time[0]))
#             train_data.append(data)
#             time.sleep(4.0)

#     for j in range(len(train_data)):
#         print(train_data[j])

#     df = pd.DataFrame(train_data, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "time"])
#     df.to_csv(r'C:\Users\_\Desktop\ABB\PathPlan\rws_train3_palletizing.csv', header=True)

#      print(df)