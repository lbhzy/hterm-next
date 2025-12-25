import paramiko

from hterm.channel.channel_pty import PtyChannel


class SshChannel(PtyChannel):
    """SSH通道"""

    def __init__(self, server: str, port: int, username: str, password: str):
        super().__init__()

        self.server = server
        self.port = port
        self.username = username
        self.password = password

        self.ssh = paramiko.SSHClient()
        # 允许连接不在 know_hosts 文件中的主机
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect_impl(self):
        self.ssh.connect(
            self.server, self.port, self.username, self.password, timeout=1
        )
        self.channel = self.ssh.invoke_shell(term="xterm-256color")
        self.channel.settimeout(0.01)  # 设置 recv 超时时间
        self.transport = self.ssh.get_transport()
        self.transport.set_keepalive(10)

    def disconnect_impl(self):
        self.ssh.close()

    def send_impl(self, data: str):
        data_bytes = data.encode()
        self.channel.send(data_bytes)

    def send_window_size_impl(self, rows: int, cols: int):
        self.channel.resize_pty(width=cols, height=rows)

    def recv_non_blocking_impl(self, size):
        try:
            data_bytes = self.channel.recv(size)
            if data_bytes:
                data_str = data_bytes.decode("utf-8", "replace")
                return data_str
            else:
                return None
        except TimeoutError:
            return ""
