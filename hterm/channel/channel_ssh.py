import time
import threading

import paramiko

from hterm.channel.channel_pty import PtyChannel


class SshChannel(PtyChannel):
    """SSH通道"""
    def __init__(self, server: str, port: int, username: str, password: str):
        super().__init__()
        self._running = True
        self.server = server
        self.port = port
        self.username = username
        self.password = password

        self._thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.ssh = paramiko.SSHClient()
        # 允许连接不在 know_hosts 文件中的主机
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def connect(self):
        try:
            self.ssh.connect(self.server, self.port, self.username, self.password, timeout=1)
            self.channel = self.ssh.invoke_shell()
            self.transport = self.ssh.get_transport()
            self.transport.set_keepalive(10)
            self.connected.emit(f"\r\n{self.server}:{self.port} 连接成功\r\n")
            self._thread.start()
        except Exception as e:
            self.disconnected.emit(f"\r\n{self.server}:{self.port} 连接失败：{e}\r\n")
        
        
    def disconnect(self) -> None:
        self.is_connected = False
        self.disconnected.emit("User requested disconnect.")
        self._running = False
        self.ssh.close()
        self._thread.join()

    def send_data(self, data: str):
        data_bytes = data.encode()
        self.channel.send(data_bytes)
    
    def send_window_size(self, rows: int, cols: int):
        self.channel.resize_pty(width=cols, height=rows)
    
    def receive_loop(self):
        while self._running:
            if self.channel.recv_ready():
                data_bytes = self.channel.recv(1024)
                if data_bytes:
                    data_str = data_bytes.decode("utf-8", "replace")
                    self.received.emit(data_str)
            time.sleep(0.01)