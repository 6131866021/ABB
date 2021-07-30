import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET

class Timedata:
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
                # print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)
                print("Clk Time: " + root.findall(findRoot.format(namespace))[i].text)
            return value[0] if len(value) != 0 else 0.0
        except ET.ParseError:
            pass 
