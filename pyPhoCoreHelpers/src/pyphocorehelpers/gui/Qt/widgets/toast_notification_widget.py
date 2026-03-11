import sys
from typing import Optional
from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QPushButton, QStyle
from qtpy.QtCore import QTimer, Qt

class ToastWidget(QWidget):
    """
    Displays a message for a short time only in its parent window

    
    from pyphocorehelpers.gui.Qt.widgets.toast_notification_widget import ToastWidget, ToastShowingWidgetMixin

    
    """
    def __init__(self, message, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(True)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.adjustSize()
        self.setFixedSize(self.size())
        
        self._should_position_to_parent_window = False
        self.durationMs = 2000
        QTimer.singleShot(self.durationMs, self.close)

    @property
    def toast_widget(self) -> bool:
        """The toast_widget property."""
        return self.toast

    @property
    def should_position_to_parent_window(self) -> bool:
        """The should_position_to_parent_window property."""
        return self._should_position_to_parent_window
    @should_position_to_parent_window.setter
    def should_position_to_parent_window(self, value: bool):
        self._should_position_to_parent_window = value


    def show_message(self, message, durationMs: Optional[int]=None):
        if durationMs is not None:
            self.durationMs = durationMs
            
        self.label.setText(message)
        self.adjustSize()
        self.setFixedSize(self.size())

        # Position the toast in the bottom-right corner of the parent
        if self.parent():
            
            if self.should_position_to_parent_window:
                parent_item = self.parent().window()
            else:
                parent_item = self.parent()

            # parent_size = self.parent().window().size()
            self.move(
                parent_item.frameGeometry().bottomRight().x() - self.width(),
                parent_item.frameGeometry().bottomRight().y() - self.height()
            )

        else:
            print(f'WARNING: ToastWidget has no parent!')

    

        QTimer.singleShot(self.durationMs, self.close)
        self.show()



class ToastShowingWidgetMixin:
    """ implementors contain a toast widget and must call `self._init_ToastShowingWidgetMixin() during startup
    
    """
    @property
    def toast_widget(self) -> ToastWidget:
        """The toast_widget property."""
        return self.toast
    
    def _init_ToastShowingWidgetMixin(self):
        self.toast = ToastWidget('Hello, PyQt5!', parent=self)


    def show_toast_message(self, message: str, durationMs:int=2000):
        """ shows a temporary toast message
        """
        self.toast_widget.show_message(message, durationMs=int(durationMs))



class ExampleApp(ToastShowingWidgetMixin, QWidget):
    """ Example app containing a toast widget """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 200, 100)
        self.setWindowTitle('Toast Example')
        # Create a button that when clicked, will display the toast
        self.button = QPushButton('Show Toast', self)
        self.button.clicked.connect(self.show_toast)  # Connect the button signal to the slot

        # Layout to place the button in the application
        layout = QVBoxLayout()  
        layout.addWidget(self.button)
        self.setLayout(layout)

        self._init_ToastShowingWidgetMixin()
        self.show()
        
    def show_toast(self):
        message = 'This is a toast message!'
        self.toast_widget.show_message(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExampleApp()
    sys.exit(app.exec_())

