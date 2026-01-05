import sys
import time
from functools import wraps
from typing import TypedDict

import pyte
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QKeyEvent, QPainter, QPalette
from PySide6.QtWidgets import QAbstractScrollArea, QApplication


def monitor(func):
    # 初始化上一次调用的时间（闭包变量）
    last_call_time = None

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal last_call_time  # 声明使用外部嵌套作用域变量

        # 1. 计算函数调用间隔
        current_time = time.time()
        interval = (current_time - last_call_time) * 1000 if last_call_time else 0
        last_call_time = current_time

        # 2. 计算函数执行耗时
        start_exec = time.time()
        result = func(*args, **kwargs)  # 执行原函数
        end_exec = time.time()

        duration = (end_exec - start_exec) * 1000

        # 打印统计信息（单位：ms）
        print(f"interval: {interval:.2f} ms cost: {duration:.2f} ms")

        return result

    return wrapper


class ThemeDict(TypedDict):
    name: str
    cursor: str
    background: str
    foreground: str


DEFAULT_THEME = {
    "name": "Horizon Dark",
    "black": "#16161C",
    "red": "#E95678",
    "green": "#29D398",
    "brown": "#FAB795",
    "blue": "#26BBD9",
    "magenta": "#EE64AE",
    "cyan": "#59E3E3",
    "white": "#FADAD1",
    "brightblack": "#232530",
    "brightred": "#EC6A88",
    "brightgreen": "#3FDAA4",
    "brightbrown": "#FBC3A7",
    "brightblue": "#3FC6DE",
    "brightmagenta": "#F075B7",
    "brightcyan": "#6BE6E6",
    "brightwhite": "#FDF0ED",
    "cursor": "#FDF0ED",
    "background": "#1C1E26",
    "foreground": "#FDF0ED",
}


class Terminal(QAbstractScrollArea):
    # 携带用户输入或快捷命令的信号
    input_ready = Signal(str)
    # 终端窗口大小改变
    resized = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.theme: ThemeDict = DEFAULT_THEME
        self._screen = pyte.Screen(80, 30)
        self.stream = pyte.Stream(self._screen)

        self.set_theme(self.theme)
        # 2. 字体配置 (必须是等宽字体)
        font = self.font()
        font.setFamilies(["Cascadia Mono", "HarmonyOS Sans SC"])
        font.setPointSize(16)
        self.setFont(font)

        # 获取单个字符宽度返回的整数精度不够 计算多字符平均
        self.char_width = self.fontMetrics().horizontalAdvance("W" * 1000) / 1000
        # self.char_width = self.fontMetrics().horizontalAdvance("W")
        self.line_height = self.fontMetrics().height()

        self.cursor_visible = True
        self.blink_text_visible = True
        self.last_input_time = 0

        # 闪烁计时器 (实现光标和文本闪烁)
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_blink_state)
        self.blink_timer.start(500)

    def feed(self, data: str):
        """向终端喂要显示的数据"""
        print("recv:", data.encode())
        self.stream.feed(data)
        self.update_scrollbar()
        self.viewport().update()

    def input(self, data: str):
        """终端输入数据"""
        print("send:", data.encode())
        self.last_input_time = time.time()
        self.input_ready.emit(data)

    def set_theme(self, theme: ThemeDict):
        self.theme.update(theme)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.theme["background"]))
        palette.setColor(QPalette.Base, QColor(self.theme["background"]))
        palette.setColor(QPalette.Text, QColor(self.theme["foreground"]))
        self.setPalette(palette)

    def toggle_blink_state(self):
        if self.hasFocus():
            self.cursor_visible = not self.cursor_visible
        else:
            # 失焦后光标始终显示
            self.cursor_visible = True

        # 连续输入过程保证光标可见
        if time.time() - self.last_input_time < 0.5:
            self.cursor_visible = True

        self.blink_text_visible = not self.blink_text_visible

        self.viewport().update()

    def update_scrollbar(self):
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            is_bottom = True
        else:
            is_bottom = False

        self.verticalScrollBar().setRange(0, len(self._screen.top_buffer))

        # 滚动条不在底部时，不更新值
        if is_bottom:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setBackgroundMode(Qt.BGMode.OpaqueMode)
        font = painter.font()
        color = QColor()
        brush = QBrush(color)  # 传入 color 保证是 BrushStyle.SolidPattern 类型

        # --- 绘制文本 ---
        text_visible = True
        start_line = self.verticalScrollBar().value()
        last_char = None
        for i, line in enumerate(
            self._screen.all_buffer[start_line : start_line + self._screen.lines]
        ):
            y = i * self.line_height

            data = ""
            for x in range(self._screen.columns):
                char = line[x]

                # 判断当前字符样式是否与上一个字符完全一致
                is_same_style = False
                if last_char is not None:
                    # 只有所有影响视觉的属性都一致，才能合并字符串
                    is_same_style = (
                        char.fg == last_char.fg
                        and char.bg == last_char.bg
                        and char.bold == last_char.bold
                        and char.italics == last_char.italics
                        and char.underscore == last_char.underscore
                        and char.strikethrough == last_char.strikethrough
                        and char.reverse == last_char.reverse
                        and char.blink == last_char.blink
                    )
                last_char = char
                if is_same_style:
                    # 遇到相同格式字符
                    # 1. 将当前字符合并进 data
                    # 2. 直接遍历下一个字符
                    data += char.data

                    # 已经遍历到行尾，将 data 渲染出来
                    if x == self._screen.columns - 1:
                        if text_visible:
                            painter.drawText(
                                (x + 1 - len(data)) * self.char_width,
                                y + self.fontMetrics().ascent(),
                                data,
                            )
                    continue
                else:
                    # 遇到不同格式字符
                    # 1. 渲染出之前的 data
                    # 2. 当前字符赋值给 data，作为新格式数据打头阵
                    # 3. 重新给 painter 设置新格式
                    if data:
                        if text_visible:
                            painter.drawText(
                                (x - len(data)) * self.char_width,
                                y + self.fontMetrics().ascent(),
                                data,
                            )
                    data = char.data

                # 文本闪烁
                if char.blink and not self.blink_text_visible:
                    # 字符有闪烁属性且当前闪烁文本不可见时，跳过渲染
                    text_visible = False
                else:
                    text_visible = True
                # 反转前景色与背景色
                if char.reverse:
                    bg_color = self.theme["foreground"]
                    fg_color = self.theme["background"]
                else:
                    fg_color = self.theme["foreground"]
                    bg_color = self.theme["background"]
                # 前景色
                if char.fg == "default":
                    pass
                elif char.fg in self.theme.keys():
                    fg_color = self.theme[char.fg]
                else:
                    fg_color = "#" + char.fg
                color.setRgb(int(fg_color[1:], base=16))
                painter.setPen(color)
                # 背景色
                if char.bg == "default":
                    pass
                elif char.bg in self.theme.keys():
                    bg_color = self.theme[char.bg]
                else:
                    bg_color = "#" + char.bg
                color.setRgb(int(bg_color[1:], base=16))
                brush.setColor(color)
                painter.setBackground(brush)
                # 文本属性
                font.setBold(char.bold)  # 加粗
                font.setItalic(char.italics)  # 斜体
                font.setUnderline(char.underscore)  # 下滑线
                font.setStrikeOut(char.strikethrough)  # 删除线
                painter.setFont(font)

        # --- 绘制光标 ---
        all_lines = len(self._screen.all_buffer)
        # 判断光标在可视范围
        if (
            start_line + self._screen.lines
            > all_lines - self._screen.lines + self._screen.cursor.y
        ):
            if self.cursor_visible:
                # 计算光标像素位置
                cursor_screen_x = self._screen.cursor.x * self.char_width
                cursor_screen_y = (
                    all_lines - self._screen.lines - start_line + self._screen.cursor.y
                ) * self.line_height
                # 绘制块状光标
                cursor_color = QColor(self.theme["cursor"])
                cursor_color.setAlpha(128)  # 半透明
                # 判断焦点状态
                if self.hasFocus():
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(cursor_color)
                else:
                    painter.setBrush(Qt.NoBrush)  # 空心光标
                painter.drawRect(
                    cursor_screen_x,
                    cursor_screen_y,
                    self.char_width,
                    self.line_height,
                )

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘输入"""
        text = event.text()

        if event.key() == Qt.Key_Up:  # 上键
            text = "\x1b[A"
        elif event.key() == Qt.Key_Down:  # 下键
            text = "\x1b[B"
        elif event.key() == Qt.Key_Right:  # 右键
            text = "\x1b[C"
        elif event.key() == Qt.Key_Left:  # 左键
            text = "\x1b[D"

        if text:
            self.input(text)

    def resizeEvent(self, event):
        """窗口大小改变时重新计算滚动条"""
        rows = int(self.viewport().height() / self.line_height)
        cols = int(self.viewport().width() / self.char_width)
        self._screen.resize(rows, cols)
        self.resized.emit(rows, cols)
        self.update_scrollbar()

        super().resizeEvent(event)

    def focusNextPrevChild(self, next):
        """禁止 tab 焦点切换"""
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    term = Terminal()
    term.input_ready.connect(term.feed)
    term.resized.connect(lambda row, cols: print(f"window size: ({row}, {cols})"))
    term.resize(600, 400)
    term.show()
    theme = {  # Horizon Dark
        "name": "Horizon Dark",
        "black": "#16161C",
        "red": "#E95678",
        "green": "#29D398",
        "brown": "#FAB795",
        "blue": "#26BBD9",
        "magenta": "#EE64AE",
        "cyan": "#59E3E3",
        "white": "#FADAD1",
        "cursor": "#FDF0ED",
        "background": "#1C1E26",
        "foreground": "#FDF0ED",
    }
    term.set_theme(theme)
    sys.exit(app.exec())
