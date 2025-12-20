from PySide6.QtCore import Signal, QObject


class PtyChannel(QObject):
    """伪终端通道基类"""
    # 当从远端或本地PTY接收到数据时发射
    received = Signal(str)
    
    # 当连接成功建立时发射
    connected = Signal(str)
    
    # 当连接断开或发生错误时发射
    disconnected = Signal(str)
        
    def connect(self) -> None:
        """
        尝试建立连接（例如：启动SSH握手或打开串口）。
        连接成功后，必须发射 connected 信号。
        """
        raise NotImplementedError

    def disconnect(self) -> None:
        """
        主动断开连接。断开后，必须发射 signal_disconnected 信号。
        """
        raise NotImplementedError

    def send_data(self, data: str) -> None:
        """
        将数据从终端模拟器发送到远端或本地PTY。
        :param data: 待发送的原始字节数据 (例如：用户按下的按键)。
        """
        raise NotImplementedError

    def send_window_size(self, rows: int, cols: int) -> None:
        """
        通知远端PTY窗口大小的改变。
        默认实现为空，因为并非所有通道（如Serial）都需要此功能。
        子类可以重写此方法以实现具体的协议操作（如SSH的resize请求）。
        """
        pass