from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import sys
import time
from typing import TypedDict

import pyte

class ThemeDict(TypedDict):
    name: str
    cursor: str
    background: str
    foreground: str

DEFAULT_THEME = {
    'name':       'Horizon Dark',
    'black':    '#16161C',
    'red':      '#E95678',
    'green':    '#29D398',
    'brown':    '#FAB795',
    'blue':     '#26BBD9',
    'magenta':  '#EE64AE',
    'cyan':     '#59E3E3',
    'white':    '#FADAD1',
    'brightblack':    '#232530',
    'brightred':      '#EC6A88',
    'brightgreen':    '#3FDAA4',
    'brightbrown':    '#FBC3A7',
    'brightblue':     '#3FC6DE',
    'brightmagenta':  '#F075B7',
    'brightcyan':     '#6BE6E6',
    'brightwhite':    '#FDF0ED',
    'cursor':   '#FDF0ED',
    'background': '#1C1E26',
    'foreground': '#FDF0ED',
}

class Terminal(QAbstractScrollArea):
    # 携带用户输入或快捷命令的信号
    input_ready = Signal(str)
    # 终端窗口大小改变
    resized = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.theme: ThemeDict = DEFAULT_THEME
        # ratio取极小值确保prev_page和next_page每次只移动一行
        self._screen = pyte.Screen(80, 30)
        self.stream = pyte.Stream(self._screen)
       
        self.set_theme(self.theme)
        # 2. 字体配置 (必须是等宽字体)
        # font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font = self.font()
        font.setFamily('Cascadia Mono')
        font.setPointSize(16)
        self.setFont(font)

        # 获取单个字符宽度返回的整数精度不够 计算多字符平均 
        # self.char_width = self.fontMetrics().horizontalAdvance('W' * 1000) / 1000
        self.char_width = self.fontMetrics().horizontalAdvance('W')
        self.line_height = self.fontMetrics().height()

        # 4. 光标状态
        self.cursor_x = 0  # 字符列索引
        self.cursor_y = 0
        self.cursor_visible = True

        # 光标闪烁计时器
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_cursor)
        self.blink_timer.start(500)

        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.update_scrollbar()


    def feed(self, data: str):
        """向终端喂要显示的数据"""
        print('recv:', data.encode())
        self.stream.feed(data)
        self.update_scrollbar()
        self.cursor_visible = True
        self.blink_timer.start(500)
        self.viewport().update()

    def input(self, data: str):
        """终端输入数据"""
        print('send:', data.encode())
        self.input_ready.emit(data)

    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        # 只重绘光标所在的区域，优化性能
        self.viewport().update()

    def update_scrollbar(self):
        self.verticalScrollBar().setRange(0, len(self._screen.top_buffer))
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def paintEvent(self, event):
        t0 = time.time()
        painter = QPainter(self.viewport())
        painter.setBackgroundMode(Qt.BGMode.OpaqueMode)
        font = painter.font()

        # --- 绘制文本 ---
        start_line = self.verticalScrollBar().value()
        for i, line in enumerate(self._screen.all_buffer[start_line:start_line + self._screen.lines]):
            y = i * self.line_height
            for x in range(self._screen.columns):
                char = line[x]
                if char.reverse:
                    bg_color = self.theme['foreground']
                    fg_color = self.theme['background']
                else:
                    fg_color = self.theme['foreground']
                    bg_color = self.theme['background']
                # 前景色
                if char.fg == 'default':
                    pass
                elif char.fg in self.theme.keys():
                    fg_color = self.theme[char.fg]
                else:
                    fg_color = '#' + char.fg
                painter.setPen(QColor(fg_color))
                # 背景色
                if char.bg == 'default':
                    pass
                elif char.bg in self.theme.keys():
                    bg_color = self.theme[char.bg]
                else:
                    bg_color = '#' + char.bg
                painter.setBackground(QBrush(QColor(bg_color)))
                # 文本属性
                font.setBold(char.bold)
                font.setItalic(char.italics)
                font.setUnderline(char.underscore)
                font.setStrikeOut(char.strikethrough)
                painter.setFont(font)

                painter.drawText(
                    x * self.char_width, 
                    y + self.fontMetrics().ascent(), 
                    char.data
                )

        # --- 绘制光标 ---
        all_lines = len(self._screen.all_buffer)
        # 判断光标在可视范围
        if start_line + self._screen.lines > all_lines - self._screen.lines + self._screen.cursor.y:
            if self.cursor_visible:
                # 计算光标像素位置
                cursor_screen_x = self._screen.cursor.x * self.char_width
                cursor_screen_y = self._screen.cursor.y * self.line_height
                # 绘制块状光标
                cursor_color = QColor(self.theme['cursor'])
                cursor_color.setAlpha(128)  # 半透明
                painter.fillRect(
                    cursor_screen_x,
                    cursor_screen_y,
                    self.char_width,
                    self.line_height,
                    cursor_color
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
            self.input(text)
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

    def set_theme(self, theme: ThemeDict):
        self.theme.update(theme)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.theme['background']))
        palette.setColor(QPalette.Base, QColor(self.theme['background']))
        palette.setColor(QPalette.Text, QColor(self.theme['foreground']))
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    term = Terminal()
    term.input_ready.connect(term.feed)
    term.resized.connect(lambda row, cols: print(f'window size: ({row}, {cols})'))
    term.resize(600, 400)
    term.show()
    theme = {    # Horizon Dark
        'name':       'Horizon Dark',
        'black':    '#16161C',
        'red':      '#E95678',
        'green':    '#29D398',
        'brown':    '#FAB795',
        'blue':     '#26BBD9',
        'magenta':  '#EE64AE',
        'cyan':     '#59E3E3',
        'white':    '#FADAD1',
        'cursor':   '#FDF0ED',
        'background': '#1C1E26',
        'foreground': '#FDF0ED',
    }
    term.set_theme(theme)
    sys.exit(app.exec())
