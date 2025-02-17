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

temp_start, temp_end = 1, 6
humidity_start, humidity_end = 6, 11
ws_start, ws_end = 11, 15
wd_start, wd_end = 15, 18
north_direction_start, north_direction_end = 18, 23
atmospheric_pressure_start, atmospheric_pressure_end = 23, 29
rainfall_start, rainfall_end = 29, 36
voltage_start, voltage_end = 36, 40

DEV_ID = 'dev_04'
# 월별 폴더 생성 및 일별 파일 경로 설정 
today = datetime.now().strftime('%Y-%m-%d') 
year_month = datetime.now().strftime('%Y-%m')  # YYYY-MM 형식 
day = datetime.now().strftime('%d')  # 일자만 추출 
 
# 월별 폴더 경로 설정 
current_dir = os.path.dirname(os.path.realpath(__file__))
user_dir = f'sensor_data/{DEV_ID}/{year_month}'

#folder_path = f'/home/pi/work_folder/sensor_data/{DEV_ID}/{year_month}' 
folder_path = os.path.join(current_dir, user_dir) 
# 월별 폴더가 없으면 생성 
if not os.path.exists(folder_path): 
    os.makedirs(folder_path) 
 
# 일별 파일 경로 설정 
DATA_PATH = f'{folder_path}/{DEV_ID}_{today}.csv' 

# DATA_PATH = f'/home/pi/work_folder/sensor_data/{DEV_ID}.csv'
# SERVER, PORT = '27.96.135.220', 4465 # 네이버 클라우드
#SERVER, PORT = '54.180.106.155', 4465 # AWS
SERVER, PORT = '35.216.42.131', 4465 #GCP
url = f'http://{SERVER}:{PORT}/api/{DEV_ID}'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def initialize():
    time.sleep(5)
    print("Initilizing...")
    while True:
        try:
            ip = requests.get("http://api64.ipify.org").text
            break
        except ConnectionError:
            print("No Internet Connection")
            time.sleep(10)
            
    while True:
        try:
            print("Connecting to sensor...")
            device = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
            message = bytes("AT+AutoSend=60".encode())
            length = device.write(message)
            result = device.read(100)  # 더 긴 데이터 길이로 설정해볼 수 있습니다.
            if result: 
                print("Connected")
                break
        except Exception as e:
            print(f"Error: {e}")
            print('Sensor not Reachable')
            time.sleep(10)
    print(ip, result)
    time.sleep(3)
    
    if not os.path.exists(DATA_PATH):
        columns = 'timestamp,ip,temp,humidity,ws,wd,north_direction,atmospheric_pressure,rainfall,voltage'
        with open(DATA_PATH, mode='a') as f:
            f.writelines(f"{columns}\n")
    
    for _ in range(2): # ignore 2 old data
        try:
            _ = parse(device, ip) 
        except:
            time.sleep(3)
    return device, ip

def parse(device, ip):
    ret = device.read(43).decode()
    if len(ret) and ret.startswith('$'):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = {
                'timestamp': timestamp,
                'ip': ip,
                'temp': float(ret[temp_start:temp_end]),
                'humidity': float(ret[humidity_start:humidity_end]),
                'ws': float(ret[ws_start:ws_end]),
                'wd': int(ret[wd_start:wd_end]),
                'north_direction': float(ret[north_direction_start:north_direction_end]),
                'atmospheric_pressure': float(ret[atmospheric_pressure_start:atmospheric_pressure_end]),
                'rainfall': float(ret[rainfall_start:rainfall_end]),
                'voltage': float(ret[voltage_start:voltage_end])
            }
        except IndexError:
            data = parse(device, ip)
    else:
        data = parse(device, ip)
    return data

def write(data):
    line = ''
    for value in data.values():
        line += str(value) + ','
    with open(DATA_PATH, mode='a') as f:
        f.writelines(f"{line[:-1]}\n") # removing the last char ','
    return

def remove_old():
    with open(DATA_PATH, mode='r+') as f:
        lines = f.readlines()
        if len(lines) > 1440 * 90:
            del lines[1:1+1440] # removing 1 day
            f.seek(1)
            f.truncate()
            for line in lines:
                f.writelines(line)
    return

def make_plot():
    # 오늘 날짜에 맞는 파일 경로 설정
    today = datetime.now().strftime('%Y-%m-%d')
    #data_path_today = f'/home/pi/work_folder/sensor_data/{DEV_ID}/{year_month}/{DEV_ID}_{today}.csv'
    data_path_today = os.path.join(folder_path,f'{DEV_ID}_{today}.csv')
    
    # 해당 날짜의 데이터 파일 읽기
    if os.path.exists(data_path_today):
        data = pd.read_csv(data_path_today)
    else:
        print(f"No data available for {today}")
        return
    
    if len(data) > 180:
        data = data[-180:]
    gs = GridSpec(3, 3)
    plt.rcParams['figure.figsize'] = [18, 12]
    fontdict = {'fontsize': 16, 'fontweight': 'bold'}
    _xticks = list(range(0, 181, 20))
    _xlim = [-10, 190]
    
    time = datetime.now().strftime("%Y-%m-%d %H:%M")
    plt.suptitle(f'Last Update: {time}', fontweight='bold', fontsize=24)

    temp = data['temp'].values
    plt.subplot(gs[0, 0])
    plt.title("Temperature ('C)", fontdict=fontdict)
    plt.xlim(_xlim)
    plt.xticks(_xticks)
    plt.plot(temp, color='C3')

    humidity = data['humidity'].values
    plt.subplot(gs[0, 1])
    plt.title("Humidity (%)", fontdict=fontdict)
    plt.xlim(_xlim)
    plt.xticks(_xticks)
    plt.plot(humidity, color='C0')

    ws = data['ws'].values
    plt.subplot(gs[0, 2])
    plt.title("Wind Speed (m/s)", fontdict=fontdict)
    plt.xlim(_xlim)
    plt.xticks(_xticks)
    plt.plot(ws, color='C1')

    wd = data['wd'].values
    plt.subplot(gs[1, 0])
    plt.title("Wind Direction", fontdict=fontdict)
    plt.xlim(_xlim)
    plt.xticks(_xticks)
    plt.plot(wd, color='C2')

    hpa = data['atmospheric_pressure'].values
    plt.subplot(gs[1, 1])
    plt.title("Atmospheric Pressure (hPa)", fontdict=fontdict)
    plt.xlim(_xlim)
    plt.xticks(_xticks)
    plt.plot(hpa, color='C4')

    rainfall = data['rainfall'].values
    plt.subplot(gs[1, 2])
    plt.title("Rainfall (mm)", fontdict=fontdict)
    plt.xlim(_xlim)
    plt.xticks(_xticks)
    rainfall_min, rainfall_max = rainfall.min(), rainfall.max()
    space = (rainfall_max - rainfall_min + 1e-2) / 20
    rainfall_ylim = [rainfall_min - space, rainfall_max + space]
    plt.ylim(rainfall_ylim)    
    plt.plot(rainfall, color='C9')

    power_generation = data['ws'].values * 20
    plt.subplot(gs[2, :])
    plt.title("Power Generation (Wh)", fontdict=fontdict)
    plt.xlim(_xlim)
    plt.xticks(_xticks)
    plt.plot(power_generation, color='r')
    
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    # plt.savefig(f'sensor_data/{DEV_ID}.jpg', dpi=150)
    plt.savefig(f'/home/pi/work_folder/display_server/static/{DEV_ID}.jpg', dpi=150)
    return

if __name__ == '__main__':
    # initilizing
    device, ip = initialize()

    # start parsing
    while True:
        try:
            data = parse(device, ip)
        except:
            time.sleep(3)
            continue
        remove_old()
        write(data)
        make_plot()
        print(data)
        try:
            requests.post(url, headers=headers, json=data, timeout=5)
        except:
            print("Destination not Reachable")
            time.sleep(10)                                                                                                                 
