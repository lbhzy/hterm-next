from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import sys
import time
import pyte


class Terminal(QAbstractScrollArea):
    data_ready = Signal(str)
    resized = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # ratio取极小值确保prev_page和next_page每次只移动一行
        self._screen = pyte.HistoryScreen(80, 30, 99999, 0.000001)
        self.stream = pyte.Stream(self._screen)

        # 1. 基础配置
        self.setStyleSheet("background-color: #1e1e1e;")
       
        # 2. 字体配置 (必须是等宽字体)
        # font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font = self.font()
        print(font.family())
        font.setFamily('Cascadia Mono')
        font.setPointSize(16)
        self.setFont(font)

        # 获取单个字符宽度返回的整数精度不够 计算多字符平均 
        self.char_width = self.fontMetrics().horizontalAdvance('W' * 1000) / 1000
        self.line_height = self.fontMetrics().height()

        # 4. 光标状态
        self.cursor_x = 0  # 字符列索引
        self.cursor_y = 0
        self.cursor_visible = True

        # 光标闪烁计时器
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_cursor)
        # self.blink_timer.start(500)

        self.verticalScrollBar().valueChanged.connect(self.on_vscroll)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.update_scrollbar()


    def feed(self, text: str):
        """向终端喂要显示的数据"""
        self.stream.feed(text)
        self.update_scrollbar()
        self.viewport().update()

    def send(self, text: str):
        """终端捕获用户输入后吐出的数据"""
        self.data_ready.emit(text)

    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        # 只重绘光标所在的区域，优化性能
        self.viewport().update()

    def update_scrollbar(self):
        line_height = self.fontMetrics().height()
        total_lines = len(self._screen.history.top) + self._screen.lines + len(self._screen.history.bottom)
        self.verticalScrollBar().setRange(
            0, max(0, total_lines * line_height - self.viewport().height())
        )
        self.verticalScrollBar().setPageStep(self.viewport().height())
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def on_vscroll(self, value: int):
        # 将screen调整到滑块位置
        pos = int(self.verticalScrollBar().value() / self.fontMetrics().height())
        screen_pos = len(self._screen.history.top)
        diff = abs(pos - screen_pos)
        for _ in range(diff):
            if screen_pos > pos:
                self._screen.prev_page()
            else:
                self._screen.next_page()

    def paintEvent(self, event):
        t0 = time.time()
        painter = QPainter(self.viewport())

        # --- 绘制文本 ---
        painter.setPen(QColor("#00FF00")) # 绿色文本

        line_height = self.fontMetrics().height()
        # # 将screen调整到滑块位置
        # pos = int(self.verticalScrollBar().value() / line_height)
        # screen_pos = len(self._screen.history.top)
        # diff = abs(pos - screen_pos)
        # for _ in range(diff):
        #     if screen_pos > pos:
        #         self._screen.prev_page()
        #     else:
        #         self._screen.next_page()

        # 绘制screen区域
        y_offset = self.verticalScrollBar().value() % line_height
        lines = self._screen.display
        for i, line in enumerate(lines):
            y = i * line_height
            painter.drawText(
                0, y + self.fontMetrics().ascent() - y_offset, line
            )

        # 多绘制一行 避免下一行突然出现
        # i = i + 1
        # if len(self._screen.history.bottom):
        #     self._screen.next_page()
        #     text = self._screen.display[-1]
        #     y = i * line_height
        #     painter.drawText(
        #         0, y + self.fontMetrics().ascent() - y_offset, text
        #     )

        # --- 绘制光标 ---
        if self.cursor_visible and not self._screen.cursor.hidden:
            # 计算光标像素位置
            cursor_screen_x = self._screen.cursor.x * self.char_width
            cursor_screen_y = self._screen.cursor.y * self.line_height - y_offset
            
            # 绘制块状光标 (半透明白色)
            painter.fillRect(
                cursor_screen_x,
                cursor_screen_y,
                self.char_width,
                self.line_height,
                QColor(255, 255, 255, 150)
            )
        # print(f'{time.time()-t0:.4f}')

    def keyPressEvent(self, event: QKeyEvent):
        """ 处理键盘输入 """
        text = event.text()

        if event.key() == Qt.Key_Up:        # 上键
            text = '\x1b[A'
        elif event.key() == Qt.Key_Down:    # 下键
            text = '\x1b[B'
        elif event.key() == Qt.Key_Right:   # 右键
            text = '\x1b[C'
        elif event.key() == Qt.Key_Left:    # 左键
            text = '\x1b[D'

        if text:
            print('send:', text.encode())
            self.send(text)
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        """窗口大小改变时重新计算滚动条"""
        rows = int(self.viewport().height() / self.line_height)
        cols = int(self.viewport().width() / self.char_width)
        self._screen.resize(rows, cols)
        self.resized.emit(rows, cols)
        self.update_scrollbar()

        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    term = Terminal()
    term.data_ready.connect(term.feed)
    term.resized.connect(lambda row, cols: print(f'window size: ({row}, {cols})'))
    term.resize(600, 400)
    term.show()
    sys.exit(app.exec())
