from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QMenu, QAction

from pathlib import Path
from pyphocorehelpers.Filesystem.open_in_system_file_manager import reveal_in_system_file_manager

class FilesystemPathLineEdit(QLineEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__initUi()

    def __initUi(self):
        self.setMouseTracking(True)
        self.setReadOnly(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepareMenu)

    def mouseMoveEvent(self, e):
        self.__showToolTip()
        return super().mouseMoveEvent(e)

    def __showToolTip(self):
        text = self.text()
        text_width = self.fontMetrics().boundingRect(text).width()

        if text_width > self.width():
            self.setToolTip(text)
        else:
            self.setToolTip('')

    def __prepareMenu(self, pos):
        menu = QMenu(self)
        openDirAction = QAction('Open Path')
        openDirAction.setEnabled(self.text().strip() != '')
        openDirAction.triggered.connect(self.__openPath)
        menu.addAction(openDirAction)
        menu.exec(self.mapToGlobal(pos))

    def __openPath(self):
        filepath = self.text()
        reveal_in_system_file_manager(filepath)
        # path = filename.replace('/', '\\')
        # subprocess.Popen(r'explorer /select,"' + path + '"')