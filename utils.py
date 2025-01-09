from datetime import datetime
import orjson
import os


# FOR RPI
KEYS = ['timestamp', 'ip', 'temp', 'humidity', 'ws', 'wd',
        'north_direction', 'atmospheric_pressure', 'rainfall', 'voltage']
TYPES = [int, str, float, float, float, int, float, float, float, float]

def check_data(dev_id, data):
    if list(data.keys()) != KEYS or not dev_id.startswith('dev_'):
        return False
    else:
        for k, t in zip(KEYS, TYPES):
            if type(data[k]) is not t:
                return False
        return True

def read_data(dev_id):
    yyyy_mm = datetime.now().strftime('%Y-%m')
    data_path = f'sensor_data/{yyyy_mm}/{dev_id}.csv'
    with open(data_path, mode='r') as f:
        lines = f.readlines()
    values = lines[-1].strip().split(',')
    data = {}
    for key, value in zip(KEYS, values):
        data[key] = value
    return orjson.dumps(data)

def update_data(dev_id, data):
    yyyy_mm = datetime.now().strftime('%Y-%m')
    data_path = f'sensor_data/{yyyy_mm}/{dev_id}.csv'
    if not os.path.exists(data_path):
        os.makedirs(f'sensor_data/{yyyy_mm}', exist_ok=True)
        columns = ''
        for key in data.keys():
            columns += key + ',' 
        with open(data_path, mode='a') as f:
            f.writelines(f"{columns[:-1]}\n") # removing the last char ','
    line = ''
    for value in data.values():
        line += str(value) + ','        
    with open(data_path, mode='a') as f:
        f.writelines(f"{line[:-1]}\n") # removing the last char ','
    return