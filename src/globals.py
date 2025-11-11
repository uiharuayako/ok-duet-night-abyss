from PySide6.QtCore import QObject, Signal
from pynput import mouse, keyboard
from qfluentwidgets import DoubleSpinBox
from PySide6.QtWidgets import QApplication
from ok import Logger, og

logger = Logger.get_logger(__name__)

# --- 猴子补丁 ---
# 修改 DoubleSpinBox，使其默认拥有一个更大的最大值

# 1. 保存原始的 __init__ 方法
_original_init = DoubleSpinBox.__init__

def _new_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)  # 2. 调用原始的初始化方法
    self.setMaximum(99999.0)              # 3. 设置我们想要的新最大值

DoubleSpinBox.__init__ = _new_init  # 4. 用我们的新方法替换原始方法
# --- 猴子补丁 ---


class Globals(QObject):
    clicked = Signal(int, int, object, bool)
    pressed = Signal(object)

    def __init__(self, exit_event):
        super().__init__()
        self.pynput_mouse = None
        self.pynput_keyboard = None
        exit_event.bind_stop(self)
        self.init_pynput()

    def stop(self):
        logger.info("pynput stop")
        self.reset_pynput()

    def init_pynput(self):
        logger.info("pynput start")
        if self.pynput_mouse is None:
            self.pynput_mouse = mouse.Listener(on_click=self.on_click)
            self.pynput_mouse.start()
        if self.pynput_keyboard is None:
            self.pynput_keyboard = keyboard.Listener(on_press=self.on_press)
            self.pynput_keyboard.start()

    def reset_pynput(self):
        if self.pynput_mouse:
            self.pynput_mouse.stop()
            self.pynput_mouse = None
        if self.pynput_keyboard:
            self.pynput_keyboard.stop()
            self.pynput_keyboard = None

    def on_click(self, x, y, button, pressed):
        self.clicked.emit(x, y, button, pressed)
    
    def on_press(self, key):
        self.pressed.emit(key)
        


if __name__ == "__main__":
    glbs = Globals(exit_event=None)
