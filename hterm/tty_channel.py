import os
import pty
import queue
import fcntl
import struct
import termios
import threading


class TtyChannel:
    def __init__(self, type, progname):
        self.progname = progname
        self.buffer = queue.Queue(maxsize=1024 * 10)

    def open(self):
        pid, self.fd = pty.fork()
        if pid == 0:
            # 子进程执行目标程序
            os.execvp(self.progname, [self.progname])

        self.thread = threading.Thread(target=self.read_task, daemon=True)
        self.thread.start()

    def join(self):
        self.thread.join()

    def read(self, size):
        data = os.read(self.fd, size)
        text = data.decode("utf-8", "replace")
        return text
    
    def read_non_blocking(self, size):
        try:
            text = self.buffer.get_nowait()        
            return text
        except queue.Empty:
            return
    
    def write(self, text):
        data = text.encode()
        os.write(self.fd, data)
        
    def read_task(self):
        while True:
            text = self.read(1024)
            self.buffer.put(text)

    def resize(self, rows, cols):
        winsize = struct.pack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)


if __name__ == '__main__':
    tty = TtyChannel('shell', 'bash')
    tty.open()
    tty.join()
    