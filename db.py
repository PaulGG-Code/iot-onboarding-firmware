
import urequests   
import json
from onboarding_auth_lib import ONBOARDING_RPC_URL

def dbWrite(data):
    print(data)

    # Write encrypted data to DB
    payload = json.dumps(data) 
    response = urequests.request("POST", ONBOARDING_RPC_URL+"/data", headers={'Content-Type': 'application/json'}, data=payload) 
    result = response.json()
    return result