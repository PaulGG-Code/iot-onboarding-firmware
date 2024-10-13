import machine
from binascii import hexlify, unhexlify
import uos   
import urequests  
import cryptolib 
import json

#ONBOARDING_RPC_URL = "http://192.168.1.2:5000"
ONBOARDING_RPC_URL = "https://iot-onboarding.adaptable.app"


# Helper functions start here
def hashify(contents):
    # Send these token ingredients and get the onboarding key from the main server
    payload = json.dumps({
        "contents": contents
    })
    response = urequests.request("POST",ONBOARDING_RPC_URL+"/hashify", headers={'Content-Type': 'application/json'}, data=payload) 
    hash = "0x"+ response.json().get("hash")  
    return hash
# Helper functions end here 

def getCipherFromKey(onboarding_key_hex):
    # Convert the hex key string to bytes
    onboarding_key_bytes = unhexlify(onboarding_key_hex[2:])
    onboardingKey = hexlify(onboarding_key_bytes)  
    # Create Ciphers
    cipher = cryptolib.aes(onboardingKey, 1) # 1 for (ECB) 
    return cipher

def encryptData(cipher, sensorData):
    # Convert the sensor value to padded bytes
    sensor_value_bytes = bytes(str(sensorData), 'utf-8') 
    # Pad the sensor value to a multiple of 16 bytes (AES block size)
    sensor_value_bytes_padded = sensor_value_bytes + b'\0' * (16 - (len(sensor_value_bytes) % 16)) 
    # Encrypt the padded sensor value
    encrypted_sensor_value = cipher.encrypt(sensor_value_bytes_padded) 
    return encrypted_sensor_value

def decryptData(cipher, encrypted_sensor_value):
    # Decrypt the encrypted sensor value
    decrypted_sensor_value = cipher.decrypt(encrypted_sensor_value) 
    # Remove the padding from the decrypted sensor value
    decrypted_sensor_value = decrypted_sensor_value.rstrip(b'\0') 
    # Convert the decrypted sensor value to string
    decrypted_sensor_value = decrypted_sensor_value.decode('utf-8') 
    return decrypted_sensor_value


def getFirmwareHash():
    # Get file contents sof main.py 
    with open("main.py", "r") as file:
        sourceCode = file.read()
        sourceCode = sourceCode.replace(" ", "")
        sourceCode = sourceCode.replace("\r", "")
    return hashify(sourceCode)    


def getDeviceDataHash(): 
    # Get the firmware version
    sys_name = uos.uname().sysname # 'esp32'
    fw_release = uos.uname().release # 1.22.2
    fw_version = uos.uname().version # v1.22.2 on 2024-02-22
    machine_name = uos.uname().machine # Generic ESP32 module with OTA with ESP32
    chip_id = hexlify(machine.unique_id()).decode('utf-8') # 3c71bfab1a64
    device_data = sys_name.encode() + fw_release.encode() + fw_version.encode() + machine_name.encode() + chip_id
    # print("Device data: ", device_data)
    # Get hash of concatenated string of device data
    return hashify(device_data)

def getDeviceGroupIdHash():
    return hashify("dg_3".encode())

def authenticateDevice(deviceId):
    print("Authenticating device...") 
    firmwareHash = getFirmwareHash() 
    deviceDataHash = getDeviceDataHash() 
    deviceGroupIdHash = getDeviceGroupIdHash()  
    payload = json.dumps({
    "firmwareHash": firmwareHash,
    "deviceDataHash": deviceDataHash, 
    "deviceGroupIdHash": deviceGroupIdHash, 
    "deviceId": deviceId,
    "chainId": "2442"
    })

    print("Sending token ingredients: ", payload)
    # Send these token ingredients and get the onboarding key from the main server
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(ONBOARDING_RPC_URL + "/generate-onboarding-key-for-device", headers=headers, data=payload)
    # response = urequests.request("POST", ONBOARDING_RPC_URL+"/generate-onboarding-key-for-device", headers={'Content-Type': 'application/json'}, json=payload) 
    if response.status_code == 200:
        key = response.json().get("key")
        print("Received Onboarding Key:", key)
        if key is None:
            raise Exception("Invalid Onboarding Key")
        response.close()
        return key
    else:
        print("Error:", response.text)
        response.close()
        raise Exception("Failed to authenticate device")
 