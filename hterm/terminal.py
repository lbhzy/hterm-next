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

        self._screen = pyte.Screen(80, 30)
        # 创建一个流解析器，并将其绑定到屏幕
        self.stream = pyte.Stream(self._screen)

        # 1. 基础配置
        self.setStyleSheet("background-color: #1e1e1e;")
       
        # 2. 字体配置 (必须是等宽字体)
        self.font = QFont("Cascadia Mono", 16)
        self.font.setStyleHint(QFont.Monospace)
        self.font_metrics = QFontMetrics(self.font)

        # 获取单个字符宽度返回整数精度不够 计算多字符平均 
        self.char_width = self.font_metrics.horizontalAdvance('W' * 10) / 10
        self.line_height = self.font_metrics.height()

        # 4. 光标状态
        self.cursor_x = 0  # 字符列索引
        self.cursor_y = 0
        self.cursor_visible = True

        # 光标闪烁计时器
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_cursor)
        self.blink_timer.start(500)

    def feed(self, text: str):
        """向终端喂要显示的数据"""
        self.stream.feed(text)

    def send(self, text: str):
        """终端捕获用户输入后吐出的数据"""
        self.data_ready.emit(text)

    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        # 只重绘光标所在的区域，优化性能
        self.viewport().update()

    def paintEvent(self, event):
        t0 = time.time()
        painter = QPainter(self.viewport())
        painter.setFont(self.font)

        # 获取当前滚动条偏移量
        scroll_y = self.verticalScrollBar().value()
        # 获取视口尺寸
        viewport_height = self.viewport().height()

        # 计算可视范围内的起始行和结束行
        start_line = scroll_y // self.line_height
        self.buffer = self._screen.display
        end_line = min(len(self.buffer), start_line + (viewport_height // self.line_height) + 2)

        # --- 绘制文本 ---
        painter.setPen(QColor("#00FF00")) # 绿色文本

        for i in range(start_line, end_line):
            text = self.buffer[i]
            # 计算绘制坐标 (y需要加上ascent，因为drawText的基线在下方)
            y_pos = (i * self.line_height) - (scroll_y)

            # 这里是灵活性所在：你可以解析 text 中的颜色代码，
            # 并多次调用 drawText 用不同颜色绘制不同片段。
            painter.drawText(0, y_pos + self.font_metrics.ascent(), text)

        # --- 绘制光标 ---
        # 只有当光标在可视区域内时才绘制
        self.cursor_x = self._screen.cursor.x
        self.cursor_y = self._screen.cursor.y
        if self.cursor_visible:
            cursor_screen_y = (self.cursor_y * self.line_height) - scroll_y
            if 0 <= cursor_screen_y < viewport_height:
                # 计算光标像素位置
                cursor_screen_x = 0 + (self.cursor_x * self.char_width)
               
                # 绘制块状光标 (半透明白色)
                painter.fillRect(
                    cursor_screen_x,
                    cursor_screen_y,
                    self.char_width,
                    self.line_height,
                    QColor(255, 255, 255, 150)
                )
        # print(f'{time.time()-t0:.4f}')
        self.update_scroll_bar()

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

        # 触发重绘
        self.viewport().update()
        # 确保光标可见
        self.ensure_cursor_visible()

    def update_scroll_bar(self):
        """根据内容高度更新滚动条范围"""
        pass
        # content_height = len(self.buffer) * self.line_height
        # viewport_height = self.viewport().height()
        # self.verticalScrollBar().setRange(0, max(0, content_height - viewport_height))

    def ensure_cursor_visible(self):
        """自动滚动以跟随光标"""
        scroll_bar = self.verticalScrollBar()
        current_scroll = scroll_bar.value()
        viewport_height = self.viewport().height()
        cursor_top = self.cursor_y * self.line_height
        cursor_bottom = cursor_top + self.line_height

        if cursor_bottom > current_scroll + viewport_height:
            scroll_bar.setValue(cursor_bottom - viewport_height)
        elif cursor_top < current_scroll:
            scroll_bar.setValue(cursor_top)

    def resizeEvent(self, event):
        """窗口大小改变时重新计算滚动条"""
        self.update_scroll_bar()
        rows = int(self.viewport().height() / self.line_height)
        cols = int(self.viewport().width() / self.char_width)
        self._screen.resize(rows, cols)
        self.resized.emit(rows, cols)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    term = Terminal()
    term.data_ready.connect(term.feed)
    term.resized.connect(lambda row, cols: print(f'window size: ({row}, {cols})'))
    term.resize(600, 400)
    term.show()
    sys.exit(app.exec())
