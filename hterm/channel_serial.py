import threading

import serial
import serial.tools.list_ports

from channel_pty import PtyChannel


class SerialChannel(PtyChannel):
    """串口通道"""
    def __init__(self, port: str, baud: int):
        super().__init__()
        self.port = port
        self.baud = baud
        self._running = True
    
    def connect(self) -> None:
        self.ser = serial.Serial(
            port=self.port,      # 串口名称
            baudrate=self.baud,    # 波特率
            bytesize=serial.EIGHTBITS, # 数据位
            parity=serial.PARITY_NONE, # 校验位
            stopbits=serial.STOPBITS_ONE, # 停止位
            timeout=1         # 读取超时设置
        )
        self.is_connected = True
        self.connected.emit(f'\r\nSerialChannel: {self.port} connected.\r\n')
        
        self._thread = threading.Thread(target=self.receive_loop, daemon=True)
        self._thread.start()
        
    def disconnect(self) -> None:
        self.is_connected = False
        self.disconnected.emit("User requested disconnect.")
        self._running = False
        self.ser.close()
        self._thread.join()

    def send_data(self, data: str) -> None:
        data_bytes = data.encode()
        self.ser.write(data_bytes)

    def receive_loop(self):
        while self._running:
            data_bytes = self.ser.read(1024)
            if data_bytes:
                data_str = data_bytes.decode("utf-8", "replace")
                self.received.emit(data_str)


def list_available_ports():
    """
    列出系统中所有可用的串行端口，并打印详细信息。
    """
    print("--- 正在查找可用的串口 ---")
    
    # 获取所有可用端口的列表
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("未检测到任何串口设备。")
        return
    
    # 遍历并打印每个端口的信息
    for port, desc, hwid in sorted(ports):
        # port: 端口名称 (如 'COM3', '/dev/ttyUSB0')
        # desc: 端口描述，通常包含设备制造商和型号信息
        # hwid: 硬件ID，更详细的设备标识符
        
        print("-" * 30)
        print(f"端口名: {port}")
        print(f"描 述: {desc}")
        print(f"硬件ID: {hwid}")
        
    print("-" * 30)
    print(f"总共找到 {len(ports)} 个串口设备。")


if __name__ == '__main__':
    list_available_ports()