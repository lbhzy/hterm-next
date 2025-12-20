from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

import qtawesome as qta

from hterm.ui.quick_dialog import QuickDialog


class QuickBar(QToolBar):
    """ 快捷命令栏 """
    command_ready = Signal(dict)
    
    def __init__(self):
        super().__init__('快捷命令栏')
        self.setup_ui()

    def setup_ui(self):
        self.setIconSize(QSize(25, 25))
        action = QAction(self)
        action.setIcon(qta.icon('ph.command-bold'))
        action.triggered.connect(self.open_dialog)
        self.addAction(action)
        
    def load_commands(self, config):
        """ 载入快捷命令配置，生成快捷命令按钮 """
        for action in self.actions():
            widget = self.widgetForAction(action)
            if isinstance(widget, QPushButton):
                self.removeAction(action)

        if not config:
            return
        
        for cmd in config['command']:
            button = QPushButton(cmd['name'])
            button.setIcon(qta.icon('mdi.script-text-outline'))
            button.setToolTip(str(cmd))
            button.type = cmd['type']
            button.content = cmd['content']
            button.clicked.connect(self.on_button_clicked)
            self.addWidget(button)

    @Slot()
    def on_button_clicked(self):
        button = self.sender()
        cmd = {
            'type': button.type,
            'content': button.content
        }
        self.command_ready.emit(cmd)

    @Slot()
    def open_dialog(self):
        dialog = QuickDialog(self) 
        dialog.exec()


if __name__ == '__main__':
    app = QApplication()
    bar = QuickBar()
    bar.command_ready.connect(lambda s: print(f'command: {s}'))
    config = {
        'command': [
            {
                'name': '命令1',
                'type': 'text',
                'content': 'echo hterm\n'
            },
            {
                'name': '命令2',
                'type': 'script',
                'content': 'echo hterm\n'
            },
            {
                'name': '命令3',
                'type': 'text',
                'content': 'echo hterm\n'
            },
        ]
    }
    bar.load_commands(config)
    bar.load_commands(config)
    bar.show()
    app.exec()