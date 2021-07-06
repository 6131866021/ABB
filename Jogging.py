import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import DigestAuth as Fa
import Main as Main

requests = Fa.requests
url = Fa.url
auth = Fa.auth
namespace = Fa.namespace

def ccount():
    meth = "rw/motionsystem?resource=change-count"
    payload={}
    headers = {
    'Cookie': '-http-session-=17::http.session::12f5ab6f9062411b4ec75ad3f3ddc864; ABBCX=27'
    }
    response = requests.request("GET", url+meth, headers=headers, data=payload, auth=auth)
    Fa.print_event(response.text, liclass='ms')