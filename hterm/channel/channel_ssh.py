import time
import threading

import paramiko

from hterm.channel.channel_pty import PtyChannel


class SshChannel(PtyChannel):
    """ SSH通道 """
    def __init__(self, server: str, port: int, username: str, password: str):
        super().__init__()
        
        self.server = server
        self.port = port
        self.username = username
        self.password = password

        self._running = True
        self.is_connected = False

        self.ssh = paramiko.SSHClient()
        # 允许连接不在 know_hosts 文件中的主机
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def connect(self):
        try:
            # 连接 ssh
            self.ssh.connect(self.server, self.port, self.username, self.password, timeout=1)
            self.channel = self.ssh.invoke_shell()
            self.channel.settimeout(0.01)   # 设置 recv 超时时间
            self.transport = self.ssh.get_transport()
            self.transport.set_keepalive(10)
            # 启动数据接收线程
            self._running = True
            self._thread = threading.Thread(target=self.receive_loop, daemon=True)
            self._thread.start()
            # 更新状态
            self.is_connected = True
            self.connected.emit(f'{self.server}:{self.port} 连接成功')
        except Exception as e:
            self.ssh.close()
            self.is_connected = False
            self.disconnected.emit(f'{self.server}:{self.port} 连接失败：{e}')

    def disconnect(self):
        if self.is_connected:
            # 等待线程结束
            self._running = False
            self._thread.join()
            # 关闭 ssh
            self.ssh.close()
            # 更新状态
            self.is_connected = False
            self.disconnected.emit('ssh 已手动断开')

    def send_data(self, data: str):
        if self.is_connected:
            data_bytes = data.encode()
            self.channel.send(data_bytes)
        else:
            self.connect()
    
    def send_window_size(self, rows: int, cols: int):
        if self.is_connected:
            self.channel.resize_pty(width=cols, height=rows)
    
    def receive_loop(self):
        while self._running:
            try:
                data_bytes = self.channel.recv(10000)
                if data_bytes:
                    data_str = data_bytes.decode('utf-8', 'replace')
                    self.received.emit(data_str)
                else:   # 返回空代表通道已关闭
                    self.ssh.close()
                    self._running = False
                    self.is_connected = False
                    self.disconnected.emit('ssh 已断开')
            except TimeoutError as e:
                continue