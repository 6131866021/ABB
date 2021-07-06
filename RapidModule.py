import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET

host = "http://192.168.1.113:80/"
auth = HTTPDigestAuth('Default User', 'robotics')
namespace = '{http://www.w3.org/1999/xhtml}'

def getRapidModule():
    meth = "rw/rapid/modules?task=T_ROB1"
    payload={}
    headers = {
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("GET", url+meth, headers=headers, data=payload, auth=auth)
    return print(response.text)
    # <li class="rap-module-info-li" title="T_ROB1/user">
    #     <span class="name">user</span>
    #     <span class="type">SysMod</span>
    # </li>
    # <li class="rap-module-info-li" title="T_ROB1/BASE">
    #     <span class="name">BASE</span>
    #     <span class="type">SysMod</span>
    # </li>
    # <li class="rap-module-info-li" title="T_ROB1/MainModule">
    #     <span class="name">MainModule</span>
    #     <span class="type">ProgMod</span>

def getRapidModuleAction():
    meth = "rw/rapid/modules?action=show"
    payload={}
    headers = {
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return print(response.text)
    # <a href="modules?action=show" rel="self"></a>
    # <form id="modify-all-position" method='post' action="modules?action=modify-all-position"></form>

def setModifyAllPositions():
    meth = "rw/rapid/modules?action=modify-all-position"
    payload='checklimit=false&checkdeactaxes=false'
    headers = {
    'Authorization': 'Basic RGVmYXVsdCBVc2VyOnJvYm90aWNz',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return print(response.text) # 204 No Content