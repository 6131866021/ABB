import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import Main as Fa

host = "http://192.168.1.113:80/"
auth = HTTPDigestAuth('Default User', 'robotics')
namespace = '{http://www.w3.org/1999/xhtml}'

# Test to subscribe
def subscribe():
    url = "subscription?action=show"
    payload={}
    headers = {
    'Cookie': '-http-session-=9::http.session::bc6016f4291930dbd779c59dccddd88c; ABBCX=19'
    }
    response = requests.request("GET", host+url, headers=headers, data=payload, auth=auth)
    print(response.text)