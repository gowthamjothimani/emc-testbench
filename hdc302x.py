import time
import board
import busio
from datetime import datetime

i2c = busio.I2C(board.SCL, board.SDA)
HDC302x_ADDRESS = 0x47

def HDC302xReset():
    soft_reset_cmd = bytes([0x30, 0xA2])
    i2c.writeto(HDC302x_ADDRESS, soft_reset_cmd)
    time.sleep(0.04)  

def HDC302xRead():
    trigger_cmd = bytes([0x24, 0x00])
    i2c.writeto(HDC302x_ADDRESS, trigger_cmd)
    time.sleep(0.040)  
    data = bytearray(6)
    i2c.readfrom_into(HDC302x_ADDRESS, data)

    temp_raw = (data[0] << 8) | data[1]
    hum_raw  = (data[3] << 8) | data[4]

    temperature_c = ((temp_raw / 65535.0) * 175.0) - 45.0
    humidity = (hum_raw / 65535.0) * 100.0

    return temperature_c, humidity
