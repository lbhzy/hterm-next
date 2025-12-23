import time
import threading
from PySide6.QtCore import Signal, QObject


class PtyChannel(QObject):
    """ 伪终端通道基类 """
    # 当从远端或本地PTY接收到数据时发射
    received = Signal(str)
    
    # 当连接成功建立时发射
    connected = Signal(str)
    
    # 当连接断开或发生错误时发射
    disconnected = Signal(str)

    def __init__(self):
        super().__init__()
        self._running = False
        self.is_connected = False
        
    def connect_impl(self) -> None:
        """ 建立通道连接，需要子类实现 """
        raise NotImplementedError

    def disconnect_impl(self) -> None:
        """ 断开通道连接，需要子类实现 """
        raise NotImplementedError

    def send_impl(self, data: str) -> None:
        """ 向通道发送数据，需要子类实现 """
        raise NotImplementedError
    
    def recv_non_blocking_impl(self, size: int) -> str | None:
        """
        非阻塞模式从通道读取数据。
        Returns:
            str: 成功读取到的数据。如果没有可用数据应返回空字符串 ""。
        Return:
            None: 明确指示底层通道已关闭/断开，触发回收流程。
        """
        raise NotImplementedError

    def send_window_size_impl(self, rows: int, cols: int) -> None:
        """ 通知远端 PTY 窗口大小的改变，有些通道没有此功能可以不实现 """
        pass

    def send_window_size(self, rows: int, cols: int) -> None:
        if self.is_connected:
            self.send_window_size_impl(rows, cols)

    def open(self):
        try:
            self.connect_impl()
            # 启动数据接收线程
            self._running = True
            self._thread = threading.Thread(target=self.receive_loop, daemon=True)
            self._thread.start()
            # 更新状态
            self.is_connected = True
            self.connected.emit(f'连接成功')
        except Exception as e:
            self.disconnect_impl()
            self.is_connected = False
            self.disconnected.emit(f'连接失败：{e}')

    def close(self):
        if self.is_connected:
            # 等待线程结束
            self._running = False
            self._thread.join()
            # 断开通道连接
            self.disconnect_impl()
            # 更新状态
            self.is_connected = False
            self.disconnected.emit('已手动断开')

    def send_data(self, data: str):
        if self.is_connected:
            self.send_impl(data)
        else:
            self.open()

    def receive_loop(self):
        while self._running:
            time.sleep(0.01)
            data = self.recv_non_blocking_impl(10000)
            if data:
                self.received.emit(data)
            elif data == None:
                self.disconnect_impl()
                self._running = False
                self.is_connected = False
                self.disconnected.emit('已断开')