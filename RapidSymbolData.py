import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import Main as Fa
import urllib.parse

host = "http://192.168.1.113:80/"
auth = HTTPDigestAuth('Default User', 'robotics')
namespace = '{http://www.w3.org/1999/xhtml}'

def getSymbolData(data=''):
    if len(data) == 0:
        return("Error")
    else:
        url = "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + data
        payload={}
        headers = {
        'Content-Type': 'application/x-www-form-hostencoded',
        'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
        }
        response = requests.request("GET", host+url, headers=headers, data=payload, auth=auth)
        return print(response.text)

def updateSymbolData(data=''):
    url = "rw/rapid/symbol/data/RAPID/T_ROB1/Module1/" + data + "?action=setInitValue"
    # payload = 'value=%5B%5B2%2C2%2C2%5D%2C%5B0%2C0%2C1%2C0%5D%2C%5B0%2C0%2C-2%2C0%5D%2C%5B9E%2B9%2C9E%2B9%2C9E%2B9%2C9E%2B9%2C9E%2B9%2C9E%2B9%5D%5D'
    v = str([[5,5,5],[0,0,1,0],[0,0,-2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]])
    value = urllib.parse.quote_plus(v)
    payload = 'value=' + value
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("POST", host+url, headers=headers, data=payload, auth=auth)
    print(response.status_code)

def validateVariable(value):
    if len(value) == 0:
        return("Value hasn't been entered")
    else:
        print(value, type(value))
        url = "rw/rapid/symbol/data?action=validate"
        value = urllib.parse.quote_plus(str(value))
        payload='task=T_ROB1&value=' + value
        headers = {
        'Content-Type': 'application/x-www-form-hostencoded',
        'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
        }
        response = requests.request("POST", host+url, headers=headers, data=payload, auth=auth)
        return print(response.status_code)

validateVariable([[5,5,5],[0,0,1,0],[0,0,-2,0],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]])
updateSymbolData(data='Target_50')