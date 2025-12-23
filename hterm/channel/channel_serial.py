import serial
import serial.tools.list_ports

from hterm.channel.channel_pty import PtyChannel


class SerialChannel(PtyChannel):
    """ 串口通道 """
    def __init__(self, port: str, baud: int):
        super().__init__()
        self.port = port
        self.baud = baud
    
    def connect_impl(self):
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.01         # 读取超时设置
        )

    def disconnect_impl(self):
        self.ser.close()

    def send_impl(self, data: str):
        data_bytes = data.encode()
        self.ser.write(data_bytes)

    def recv_non_blocking_impl(self, size):
        try:
            data = self.ser.read(1024).decode()
            return data
        except Exception as e:
            return None

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