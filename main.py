# main.py -- put your code here! 
from onboarding_auth_lib import authenticateDevice, getCipherFromKey, encryptData, ONBOARDING_RPC_URL
import time 
import machine  
from ubinascii import hexlify
from db import dbWrite

DEVICE_ID = "0x06Cea043b0Bd7E79D5e8457b513063EA9Bb64e83" 

# Authenticate and get the cipher key
onboarding_key_hex = authenticateDevice(DEVICE_ID) 
cipher = getCipherFromKey(onboarding_key_hex)  # Use the cipher to encrypt and decrypt data

# IOT LOGIC
# Initialize ADC for ESP32
# Note: ADC(0) might not be valid on ESP32. Use a specific pin number, e.g., 32.
# Adjust the pin number based on your actual sensor connection.
#ldr = machine.ADC(0)
adc_pin = machine.Pin(32)
ldr = machine.ADC(adc_pin)

# Configure ADC attenuation for full range of readings
ldr.atten(machine.ADC.ATTN_11DB)

while(True): 
    # Read value from the sensor
    sensorData = ldr.read() 
    encrypted_sensor_value = encryptData(cipher, sensorData) 
    
    # Prepare data for storage or transmission
    data = {
        "sensorValue": hexlify(encrypted_sensor_value),
        "deviceId": "" + DEVICE_ID
    } 
    print(data)
    
    # Write encrypted data to DB    
    dbWrite(data)
    
    # Wait for 2 seconds
    time.sleep(2) 