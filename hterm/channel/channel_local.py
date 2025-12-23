import os
import sys

from hterm.channel.channel_pty import PtyChannel

if sys.platform == 'win32':
    from winpty import PtyProcess
else:
    import pty
    import fcntl
    import select
    import struct
    import signal
    import termios


class LocalChannel(PtyChannel):
    """ Local 通道 """
    def __init__(self, progname):
        super().__init__()
        self.progname = progname
    
    def connect_impl(self):
        if sys.platform == 'win32':
            self.proc = PtyProcess.spawn(self.progname)
            self.proc.fileobj.setblocking(False)
        else:
            self.pid, self.fd = pty.fork()
            if self.pid == 0:
                # 子进程执行目标程序
                os.execvp(self.progname, [self.progname])
        
    def disconnect_impl(self):
        if sys.platform == 'win32':
            self.proc.close(force=True)
        else:
            os.kill(self.pid, signal.SIGHUP)
            os.waitpid(self.pid, os.WNOHANG)
            os.close(self.fd)

    def send_impl(self, data: str):
        if sys.platform == 'win32':
            self.proc.write(data)
        else:
            data_bytes = data.encode()
            os.write(self.fd, data_bytes)
        
    def send_window_size_impl(self, rows: int, cols: int):
        if sys.platform == 'win32':
            self.proc.setwinsize(rows, cols)
        else:
            winsize = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def recv_non_blocking_impl(self, size: int):
        if sys.platform == 'win32':
                try:
                    data = self.proc.read(size)
                    if data:
                        return data
                    else:
                        return None
                except BlockingIOError:
                    return ''
        else:
            r, _, _ = select.select([self.fd], [], [], 0)
            if r:
                data = os.read(self.fd, size).decode('utf-8', 'replace')
                if data:
                    return data
                else:
                    return None
            else:
                return ''
