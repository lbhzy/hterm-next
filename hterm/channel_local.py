import os
import sys
import threading

from channel_pty import PtyChannel

if sys.platform == 'win32':
    from winpty import PtyProcess
else:
    import pty
    import fcntl
    import struct
    import termios


class LocalChannel(PtyChannel):
    """Local 通道"""
    def __init__(self, progname):
        super().__init__()
        self.progname = progname
        self._running = True
    
    def connect(self) -> None:
        if sys.platform == 'win32':
            self.proc = PtyProcess.spawn(self.progname)
        else:
            self.pid, self.fd = pty.fork()
            if self.pid == 0:
                # 子进程执行目标程序
                os.execvp(self.progname, [self.progname])
        self.is_connected = True
        self.connected.emit(f'\r\nLocalChannel: {self.progname} connected.\r\n')
        
        self._thread = threading.Thread(target=self.receive_loop, daemon=True)
        self._thread.start()
        
    def disconnect(self) -> None:
        if not self.is_connected:
            return
        self.is_connected = False
        self.disconnected.emit("User requested disconnect.")
        self._running = False
        if sys.platform == 'win32':
            self.proc.close(force=True)
            self._thread.join()
        else:
            os.close(self.fd)
            self._thread.join()
            os.kill(self.pid, termios.SIGHUP)
            os.waitpid(self.pid, os.WNOHANG)

    def send_data(self, data: str) -> None:
        if sys.platform == 'win32':
            self.proc.write(data)
        else:
            data_bytes = data.encode()
            os.write(self.fd, data_bytes)
        
    def send_window_size(self, rows: int, cols: int):
        if sys.platform == 'win32':
            self.proc.setwinsize(rows, cols)
        else:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def receive_loop(self):
        while self._running:
            if sys.platform == 'win32':
                data_str = self.proc.read()
            else:
                data_bytes = os.read(self.fd, 1024)
                data_str = data_bytes.decode("utf-8", "replace")
            self.received.emit(data_str)
