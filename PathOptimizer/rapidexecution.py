import requests
from param import Data

ws = Data()

def startExecution():
    url = ws.host + "rw/rapid/execution?action=startprodentry"
    payload='regain=continue&execmode=continue&cycle=once&condition=none&stopatbp=disabled&alltaskbytsp=false'
    headers = {
        'Content-Type': 'application/x-www-form-hostencoded',
    }
    response = requests.request("POST", url, headers=headers, data=payload, auth=ws.digest_auth)
    if response.status_code == 204:
        print("Start Rapid Execution")
        return True
    else:
        print("Fail to Start Execution")
        return False
    
def stopExecution():
    url = ws.host + "rw/rapid/execution?action=stop"
    payload='regain=continue&execmode=continue&cycle=forever&condition=none&stopatbp=disabled&alltaskbytsp=false'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.request("POST", url, headers=headers, data=payload, auth=ws.digest_auth)
    if response.status_code == 204:
        print("Stop Rapid Execution")
        return True
    else:
        print("Fail to Stop Execution")
        return False

def keylessOnMotor():
    url = ws.host + "rw/cfg?action=keyless"
    payload='state=run'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.request("POST", url, headers=headers, data=payload, auth=ws.digest_auth)
    if response.status_code == 204:
        print("Set Motor On")
        return True
    else:
        print("Fail to Set Motor On")
