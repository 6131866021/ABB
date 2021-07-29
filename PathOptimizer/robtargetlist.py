import numpy as np
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import urllib.parse
import numpy as np

class RobtargetList:
    def __init__(self, host, username, password, robtargets):
        """Define all Robtarget class's attributes"""
        self.host = host
        self.username = username
        self.password = password
        self.robtargetA = robtargets[0]
        self.robtargetB = robtargets[1]
        self.robtargetC = robtargets[2]
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.session = requests.Session()
        self.episodes = 0
        self.robcount = 0

    def getSymbol_data(self):
        """GET the data of robtarget A, B, and C by requesting Robot Web Services"""

        # Prepare request params
        host = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/"
        robtargets = [self.robtargetA, self.robtargetB, self.robtargetC]
        urls = [host + str(robtarget) for robtarget in robtargets]
        payload={}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Request using GET Methods
        responses = [self.session.request("GET", urls[0], headers=headers, data=payload, auth=self.digest_auth),
                     self.session.request("GET", urls[1], headers=headers, data=payload, auth=self.digest_auth),
                     self.session.request("GET", urls[2], headers=headers, data=payload, auth=self.digest_auth)]

        # Assign the response values to the Robtarget class's attributes
        self.valueA = self.extract_value(responses[0].text)
        self.valueB = self.extract_value(responses[1].text)
        self.valueC = self.extract_listvalue(responses[2].text)
        self.changeC = self.extract_listvalue(responses[2].text)

        # True if all responses are returned 200
        return responses[0].status_code == 200 and responses[1].status_code == 200 and responses[2].status_code == 200

    def extract_value(self, response):
        """Extract the value of Robtarget from API responses in the XML format"""

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
                # print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
            
            arr = list() # return list

            # This loop appends value in the return list in the correct Robtarget's format
            for data in value[0][1:-1].split(','):
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

        except ET.ParseError:
            pass

    def extract_listvalue(self, response):
        """Extract the value of Robtarget from API responses in the XML format"""

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
                # print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
            
            arr = list() # return list

            # This loop appends value in the return list in the correct Robtarget's format
            for data in value[0][1:-1].split(','):
                removeBracket = [data.find('[['), data.find(']]'), data.find('['), data.find(']')]
                if removeBracket[0] == 0:
                    arr.append(float(data[2:]))
                elif removeBracket[1] > 0:
                    arr.append(float(data[:-2]))
                elif removeBracket[2] == 0:
                    arr.append(float(data[1:]))
                elif removeBracket[3] > 0:
                    arr.append(float(data[:-1]))
                else:
                    arr.append(float(data))
            
            re_arr = list()
            for i in range(10):
                re_arr.append(np.array([[arr[0*i], arr[1*i], arr[2*i]], 
                                        [arr[3*i], arr[4*i], arr[5*i], arr[6*i]], 
                                        [arr[7*i], arr[8*i], arr[9*i], arr[10*i]], 
                                        [arr[11*i], arr[12*i], arr[13*i], arr[14*i], arr[15*i], arr[16*i]]], dtype=object))
            
            return re_arr

        except ET.ParseError:
            pass

    def randomC_data(self):
        """
        Random self.changeC value using normal distribution where
        mean is the point at the center of point A and point B,
        standard deviation is the difference between pointA and pointB
        divided by 8 in each respective coordinate (X, Y, Z)
        """

        validPoint = False
        randomPoint = list()
        mean = [(self.valueA[0][i]+self.valueB[0][i])/2 for i in range(3)]
        std = [abs(self.valueA[0][i]-self.valueB[0][i])/8 for i in range(3)]

        while not validPoint:
            randomPoint = [np.random.normal(loc=mean[i], scale=std[i]) for i in range(3)]
            x1, x2 = self.valueA[0][0], self.valueB[0][0]
            y1, y2 = self.valueA[0][1], self.valueB[0][1]
            z1, z2 = self.valueA[0][2], self.valueB[0][2]
            x_valid = (x1 < randomPoint[0] < x2) or (x2 < randomPoint[0] < x1)
            y_valid = (y1 < randomPoint[1] < y2) or (y2 < randomPoint[1] < y1)
            z_valid = (z1 < randomPoint[2] < z2) or (z2 < randomPoint[2] < z1) 
            validPoint = x_valid and y_valid and z_valid

        # When randomPoint values are valid, change self.changeC
        for i in range(3):
            self.changeC[0][i] = np.round(randomPoint[i], 2)

        # Update traning rounds
        self.episodes = self.episodes + 1

        # URL encode the payload params before POST the request         
        self.encodeC_data()

    def changeC_data(self, value):
        """Use in real case"""
        for i in range(3):
            self.changeC[0][i] = np.round(value[i], 2)

        self.encodeC_data()

    def changeC_listdata(self, value):
        """Change List Data"""
        for i in range(10):
            for j in range(3):
                self.changeC[i][0][j] = np.round(value[i][j], 2)
        self.encodeC_listdata()

    def encodeC_data(self):
        """
        From headers = {'Content-Type': 'application/x-www-form-urlencoded'}, 
        we should urlencode self.changeC before sending the request
        """

        encodevalue = "[["

        # In robtarget values there are 4 lists, but the last one which consisted of constant values is broken
        for i in range(3):
            listlen = len(self.changeC[i])
            for j in range(listlen):
                if j+1 == listlen:  # last value in the list
                    encodevalue = encodevalue + str(self.changeC[i][j]) + '],['
                else:
                    encodevalue = encodevalue + str(self.changeC[i][j]) + ','

        # Since the last list in robtarget is constant, we added them manually
        encodevalue = encodevalue + "9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]]"

        # URL encoded method
        self.encodeC = urllib.parse.quote_plus(encodevalue)

    def encodeC_listdata(self):
        """
        From headers = {'Content-Type': 'application/x-www-form-urlencoded'}, 
        we should urlencode self.changeC before sending the request
        """

        # default = '[[0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0,0,0]]'

        encodevalue = "["

        for i in range(9):
            encodevalue += ("[[" +  str(self.changeC[i][0][0]) + "," + 
                                    str(self.changeC[i][0][1]) + "," +
                                    str(self.changeC[i][0][2]) + 
                                    "],[0,0,0,0],[0,0,0,0],[0,0,0,0,0,0]],")

        encodevalue += ("[[" +  str(self.changeC[9][0][0]) + "," + 
                                str(self.changeC[9][0][1]) + "," +
                                str(self.changeC[9][0][2]) + 
                                "],[0,0,0,0],[0,0,0,0],[0,0,0,0,0,0]]]")

        # URL encoded method
        self.encodeC = urllib.parse.quote_plus(encodevalue)

    def validateC_data(self):
        """
        This method is used to check that self.changeC values are validated in Robot Studio
        """
        
        url = self.host + "rw/rapid/symbol/data?action=validate"
        payload='task=T_ROB1&value=' + self.encodeC + '&datatype=robtarget'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = self.session.request("POST", url, headers=headers, data=payload, auth=self.digest_auth)

        # Response should return 204 (No Content)
        if response.status_code != 204:
            print(f"Error validate symbol data --> Check the position again\n{self.changeC}") 
        return response.status_code == 204

    def updateC_data(self):
        """Update the random values of self.robtargetC to Robot Web Services"""

        # Prepare request params
        url = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.robtargetC + "?action=set"
        payload = 'value=' + self.encodeC
        response = object()

        if self.robcount == 0:
            response = requests.request("POST", url, data=payload, auth=self.digest_auth)
            self.headers = {
                'Cookie': '-http-session-={0}; ABBCX={1}'.format(response.cookies['-http-session-'], response.cookies['ABBCX'])
            }
        else:
            response = requests.request("POST", url, headers=self.headers, data=payload, auth=self.digest_auth)

        # Response should return 204 (No Content)
        if response.status_code == 204:
            print(f"Update '{self.robtargetC}'")
            self.robcount += 1
            return True
        else:
            print(f"Error update '{self.robtargetC}'\nResponse: {response.text}\nself.changeC: {self.changeC}")
            return False

    def updateC_listdata(self):
        """Update the random values of List self.robtargetC via Robot Web Services"""

        url = self.host + "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + self.robtargetC + "?action=set"
        payload = 'value=' + self.encodeC
        response = object()

        if self.robcount == 0:
            response = requests.request("POST", url, data=payload, auth=self.digest_auth)
            self.headers = {
                'Cookie': '-http-session-={0}; ABBCX={1}'.format(response.cookies['-http-session-'], response.cookies['ABBCX'])
            }
        else:
            response = requests.request("POST", url, headers=self.headers, data=payload, auth=self.digest_auth)

        # Response should return 204 (No Content)
        if response.status_code == 204:
            print(f"Update List '{self.robtargetC}'")
            self.robcount += 1
            return True
        else:
            print(f"Error update '{self.robtargetC}'\nResponse: {response.text}\nself.changeC: {self.changeC}")
            return False
