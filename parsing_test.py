from matplotlib.gridspec import GridSpec 
import matplotlib.pyplot as plt 
from datetime import datetime 
import pandas as pd 
import requests 
import warnings 
import serial 
import time 
import os 


warnings.filterwarnings('ignore') 
 
######csv data save hyper parameter setting######
temp_start, temp_end = 1, 6 
humidity_start, humidity_end = 6, 11 
ws_start, ws_end = 11, 15 
wd_start, wd_end = 15, 18 
north_direction_start, north_direction_end = 18, 23 
atmospheric_pressure_start, atmospheric_pressure_end = 23, 29 
rainfall_start, rainfall_end = 29, 36 
voltage_start, voltage_end = 36, 40 


#####folder data save name (csv file, graph.png)#####
DEV_ID = 'dev_06' 

########data save root###########
current_dir = os.path.dirname(os.path.realpath(__file__))
user_dir = f'sensor_data/{DEV_ID}.csv'
DATA_PATH = os.path.join(current_dir, user_dir)
#DATA_PATH = f'/home/tbcrew/Document/work_folder/sensor_data/{DEV_ID}.csv' 


print("Connecting to sensor...") 
device = serial.Serial('/dev/ttyUSB0', 9600, timeout=2) #atmosphere sensor serial uart setting 
message = bytes("AT+AutoSend=60".encode()) #데이터 60초 마다 자동으로 전송하라는 의미, 바이트코드로 형식변환
length = device.write(message) #변환된 바이트 코드 센서에 전송 
result = device.read(100)  # 더 긴 데이터 길이로 설정해볼 수 있습니다. (시리얼 포트를 통해 100바이트의 데이터 읽어오기)

print('디바이스 상태:',device)
print('result 값:',result)

#통신포트 상태출력
if device.is_open:
	print("Serial port is open.")
else:
	print("Serial port is closed.")


if result:  
	print("Connected") 
print(datetime.now())

