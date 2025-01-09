import serial 
import time 
 
class DalyBMSUART: 
    XFER_BUFFER_LENGTH = 13  # 전송/수신 버퍼 길이 
 
    # Daly BMS 명령어 정의 
    COMMAND = { 
        'VOUT_IOUT_SOC': 0x90, 
        'MIN_MAX_CELL_VOLTAGE': 0x91, 
        'MIN_MAX_TEMPERATURE': 0x92, 
        'DISCHARGE_CHARGE_MOS_STATUS': 0x93, 
        'STATUS_INFO': 0x94, 
        'CELL_VOLTAGES': 0x95, 
        'CELL_TEMPERATURE': 0x96, 
        'CELL_BALANCE_STATE': 0x97, 
        'FAILURE_CODES': 0x98, 
        'DISCHRG_FET': 0xD9, 
        'CHRG_FET': 0xDA, 
        'BMS_RESET': 0x00 
    } 
 
    def __init__(self, port, baudrate=9600): 
        """ UART 포트 초기화 """ 
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=1) 
        self.tx_buffer = [0] * DalyBMSUART.XFER_BUFFER_LENGTH 
        self.rx_buffer = [0] * DalyBMSUART.XFER_BUFFER_LENGTH 
        self.init_tx_buffer() 
 
    def init_tx_buffer(self): 
        """전송 버퍼 초기화""" 
        self.tx_buffer[0] = 0xA5  # 시작 플래그 
        self.tx_buffer[1] = 0x40  # PC 주소 
        self.tx_buffer[3] = 0x08  # 데이터 길이 (8바이트 고정) 
 
        # 데이터 내용 (5~11 바이트는 0으로 채움) 
        for i in range(4, 12): 
            self.tx_buffer[i] = 0x00 
 
    def calculate_checksum(self, data): 
        """체크섬 계산: 모든 바이트의 합계에서 하위 바이트만 반환""" 
        checksum = sum(data) & 0xFF 
        return checksum 
 
    def send_command(self, cmd_id): 
        """BMS에 명령어 전송""" 
        self.tx_buffer[2] = cmd_id  # 명령어 설정 
 
        # 체크섬 계산 후 추가 
        checksum = self.calculate_checksum(self.tx_buffer[:12]) 
        self.tx_buffer[12] = checksum 
 
        # 명령어 전송 
        self.serial.write(bytearray(self.tx_buffer)) 
        print(f"Sent: {self.tx_buffer}")
        
 
    def receive_data(self): 
        """BMS로부터 데이터 수신""" 
        time.sleep(1)  # 응답 대기 
        if self.serial.in_waiting > 0: 
            self.rx_buffer = self.serial.read(DalyBMSUART.XFER_BUFFER_LENGTH) 
            print(f"Received: {self.rx_buffer}") 
            if self.validate_checksum(): 
                return self.rx_buffer 
            else: 
                print("Checksum failed.") 
        else: 
            print("No response received.") 
        return None 
 
    def validate_checksum(self): 
        """수신된 데이터의 체크섬 검증""" 
        checksum = sum(self.rx_buffer[:12]) & 0xFF 
        return checksum == self.rx_buffer[12] 
 
    def get_pack_measurements(self): 
        """전압, 전류, SOC 데이터를 BMS로부터 요청""" 
        self.send_command(DalyBMSUART.COMMAND['VOUT_IOUT_SOC']) 
        data = self.receive_data() 
        if data: 
            pack_voltage = ((data[4] << 8) | data[5]) / 10.0  # 전체 팩 전압 (0.1V 단위) 
            pack_current = (((data[8] << 8) | data[9]) - 30000) / 10.0  # 팩 전류 (0.1A 단위) 
            pack_soc = ((data[10] << 8) | data[11]) / 10.0  # 팩 SOC (0.1% 단위) 
            print(f"Pack Voltage: {pack_voltage}V, Pack Current: {pack_current}A, SOC: {pack_soc}%") 
            return pack_voltage, pack_current, pack_soc 
        return None 
 
    def get_min_max_cell_voltage(self): 
        """최소/최대 셀 전압 데이터를 BMS로부터 요청""" 
        self.send_command(DalyBMSUART.COMMAND['MIN_MAX_CELL_VOLTAGE']) 
        data = self.receive_data() 
        if data: 
            max_cell_voltage = (data[4] << 8) | data[5]  # 최대 셀 전압 (mV) 
            min_cell_voltage = (data[7] << 8) | data[8]  # 최소 셀 전압 (mV) 
            print(f"Max Cell Voltage: {max_cell_voltage}mV, Min Cell Voltage: {min_cell_voltage}mV") 
            return max_cell_voltage, min_cell_voltage 
        return None 
 
    def get_pack_temperature(self): 
        """팩 온도 데이터를 BMS로부터 요청""" 
        self.send_command(DalyBMSUART.COMMAND['MIN_MAX_TEMPERATURE']) 
        data = self.receive_data() 
        if data: 
            max_temp = data[4] - 40  # 최대 온도 
            min_temp = data[6] - 40  # 최소 온도 
            print(f"Max Temp: {max_temp}°C, Min Temp: {min_temp}°C") 
            return max_temp, min_temp 
        return None
    
    def log_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

    def close(self): 
        """포트 닫기""" 
        self.serial.close()
        
        
 
if __name__ == "__main__":
    bms = DalyBMSUART(port='/dev/ttyUSB1', baudrate=9600)
    csv_file = 'bms_data_log.csv'
    
    # CSV 파일에 헤더 추가 (처음 실행 시에만 필요)
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Pack Voltage', 'Pack Current', 'SOC', 'Max Cell Voltage', 'Min Cell Voltage', 'Max Temp', 'Min Temp'])

    try:
        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 각 데이터를 수집하고 CSV에 기록
            pack_data = bms.get_pack_measurements()
            cell_voltage_data = bms.get_min_max_cell_voltage()
            temp_data = bms.get_pack_temperature()

            if pack_data and cell_voltage_data and temp_data:
                data = [timestamp, *pack_data, *cell_voltage_data, *temp_data]
                log_to_csv(csv_file, data)
                print(f"Data logged: {data}")
            else:
                print("No complete data received.")

            time.sleep(180)  # 3분마다 데이터 수집

    except KeyboardInterrupt:
        bms.close()
        print("프로그램 종료. UART 연결 닫힘.")