import serial
import time

# USB 포트에 맞게 수정 (예: /dev/ttyUSB0)
uart = serial.Serial('/dev/ttyUSB1', baudrate=9600, timeout=1)

try:
    while True:
        # 전송할 데이터
        message = 'Hello UART\n'
        
        # 데이터 전송
        uart.write(message.encode())  # 문자열을 바이트로 인코딩하여 전송
        print(f"Sent: {message.strip()}")  # 전송된 데이터 출력 (엔터 제거 후)
        
        # 대기 시간 (1초)
        time.sleep(1)

        # 수신된 데이터 읽기
        if uart.in_waiting > 0:  # UART 버퍼에 수신된 데이터가 있는지 확인
            data = uart.read(uart.in_waiting)  # 수신된 모든 데이터 읽기
            print(f"Received: {data}")
        else:
            print("No data received.")
        
        # 대기 시간 (1초)
        time.sleep(1)

except KeyboardInterrupt:
    uart.close()
    print("Closed UART connection.")
