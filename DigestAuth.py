import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import Main as Fa

host = "http://192.168.1.113:80/"
auth = HTTPDigestAuth('Default User', 'robotics')
namespace = '{http://www.w3.org/1999/xhtml}'

# Print format
def print_event(evt, liclass="", spanclass=""):
    root = ET.fromstring(evt)
    spanclass = "[@class='" + spanclass + "']" if len(spanclass) > 0 else ''
    findRoot = ".//{0}li[@class='" + liclass + "']/{0}span" + spanclass
    for i in range(len(root.findall(findRoot.format(namespace)))):
        print(liclass + " " + spanclass + ": " + root.findall(findRoot.format(namespace))[i].text)

def local_login(status=False):
    if status == False:
        print("In FlexPendant, Toggle 'Enable Button' for 3 times")
    else: 
        url = "users?action=set-locale"
        payload='type=local'
        headers = {
            'Content-Type': 'application/x-www-form-hostencoded',
            'Cookie': '-http-session-=14::http.session::8d791de984ff92e56e439ade66c49acf; ABBCX=24'
        }
        response = requests.request("POST", host+url, headers=headers, data=payload, auth=auth, timeout=300)
        print(response.status_code)

def request_mastership(status=False):
    if(status==False):
        print("Request Mastership Error")
    else:
        url = "rw/mastership?action=request"
        payload='type=local'
        headers = {
        'Content-Type': 'application/x-www-form-hostencoded',
        'Cookie': '-http-session-=17::http.session::12f5ab6f9062411b4ec75ad3f3ddc864; ABBCX=27'
        }
        response = requests.request("POST", host+url, headers=headers, data=payload, auth=auth)
        return print(response.status_code)

# def main():
#     login_status = True if local_login() == 200 else False
#     # mastership_status = request_mastership(status=login_status)

# def task():
#     url = "rw/rapid/tasks/T_ROB1/pcp"
#     payload={}
#     headers = {
#     'Cookie': '-http-session-=17::http.session::3138ad323c64f0c163027a370876083d; ABBCX=37'
#     }
#     response = requests.request("GET", host+url, headers=headers, data=payload, auth=auth)
#     txt = response.text
#     print(txt.find("li"), txt.rfind("li"))
#     print(txt[297:805] + "\n")
#     # print_event(response.text, liclass='pcp-info')
#     # print_event(response.text, liclass='pcp-info', spanclass='beginposition')
#     print_event(response.text, liclass='pcp-info', spanclass='endposition')
#     print_event(response.text, liclass='pcp-info', spanclass='modulemame')
#     print_event(response.text, liclass='pcp-info', spanclass='routinename')

# task()

# def pathsupervision():
#     url = "rw/motionsystem/pathsupervision?mechunit=ROB_1"
#     payload={}
#     headers = {
#     'Authorization': 'Basic RGVmYXVsdCBVc2VyOnJvYm90aWNz',
#     'Cookie': '-http-session-=7::http.session::496fb47549df1f6b7a32487f1858965d; ABBCX=26'
#     }
#     response = requests.request("GET", host+url, headers=headers, data=payload, auth=auth)
#     print_event(response.text, liclass='ms-pathsupervision')