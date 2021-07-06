import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET

host = "http://192.168.1.113:80/"
auth = HTTPDigestAuth('Default User', 'robotics')
namespace = '{http://www.w3.org/1999/xhtml}'

def getRapidExecution():
    url = "rw/rapid/execution"
    payload={}
    headers = {
    'Authorization': 'Basic RGVmYXVsdCBVc2VyOnJvYm90aWNz',
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("GET", host+url, headers=headers, data=payload, auth=auth)
    return print(response.text)
    # <li class="rap-execution" title="execution">
    #   <span class="ctrlexecstate">stopped</span>
    #   <span class="cycle">forever</span>
    # </li>

def startRapidExecution():
    url = "rw/rapid/execution?action=startprodentry"
    payload='regain=continue&execmode=continue&cycle=forever&condition=none&stopatbp=disabled&alltaskbytsp=false'
    headers = {
    'Content-Type': 'application/x-www-form-hostencoded',
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("POST", host+url, headers=headers, data=payload, auth=auth)
    return print(response.status_code) # 204 No Content

def stopRapidExecution():
    url = "rw/rapid/execution?action=stop"
    payload='regain=continue&execmode=continue&cycle=forever&condition=none&stopatbp=disabled&alltaskbytsp=false'
    headers = {
    'Content-Type': 'application/x-www-form-hostencoded',
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("POST", host+url, headers=headers, data=payload, auth=auth)
    return print(response.status_code) # 204 No Content

def setExecutionCycle(forever=True):
    url = "rw/rapid/execution?action=setcycle"
    payload = 'cycle=once' if forever == False else 'cycle=forever'
    headers = {
    'Authorization': 'Basic RGVmYXVsdCBVc2VyOnJvYm90aWNz',
    'Content-Type': 'application/x-www-form-hostencoded',
    'Cookie': '-http-session-=19::http.session::18ebde34f1bad88d578877dd44074e82; ABBCX=32'
    }
    response = requests.request("POST", host+url, headers=headers, data=payload, auth=auth)
    return print(response.status_code) # 204 No Content