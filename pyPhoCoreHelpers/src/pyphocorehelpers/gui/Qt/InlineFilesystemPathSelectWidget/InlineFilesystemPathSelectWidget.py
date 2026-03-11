# from pyphocorehelpers.gui.Qt.InlineFilesystemPathSelectWidget.InlineFilesystemPathSelectBase import InlineFilesystemPathSelectBase

from pathlib import Path
from pyphocorehelpers.gui.Qt.InlineFilesystemPathSelectWidget.Uic_AUTOGEN_InlineFilesystemPathSelectBase import Ui_Form
from pyphocorehelpers.gui.Qt.ExceptionPrintingSlot import pyqtExceptionPrintingSlot

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QWidget, QStyle

import pyphoplacecellanalysis.External.pyqtgraph as pg

class InlineFilesystemPathSelectWidget(QWidget):
    """ A widget that displays a label, the currently selected filesystem path, and a button to choose a new path.
    
    Properties:
        is_save_mode: bool = False # if true, the dialog created by the widget is that produced when saving. Allows specifying default file extensions and file names

        # Commmon:
        label: str = 'Path' # The text displayed to the left of the path
        path_type: str = 'folder' # {'file', 'folder'}
        
        # save mode only:
        
        
        
        # Non-save mode only:
        allows_multiple: bool = False # If True, allows multiple selections to be made. Only relevant for 
        
    Usage:
        from pyphocorehelpers.gui.Qt.InlineFilesystemPathSelectWidget.InlineFilesystemPathSelectWidget import InlineFilesystemPathSelectWidget
        InlineFilesystemPathSelectWidget('Root')
    """
    _label: str = 'Path Test'
    is_save_mode: bool = False # if true, the dialog created by the widget is that produced when saving. Allows specifying default file extensions and file names
    path_type: str = 'folder' # {'file', 'folder'}
    allows_multiple: bool = False # If True, allows multiple selections to be made. Only relevant for 
    sigFileSelectionChanged = QtCore.Signal(str)
    
    @property
    def path(self):
        """The path property."""
        # Get path from the file path string:
        curr_path_string = self.ui.txtFilePath.text()
        curr_path = Path(curr_path_string)
        return curr_path
    @path.setter
    def path(self, value):
        self.ui.txtFilePath.setText(str(value))
        
        
    @property
    def label(self):
        """The label property."""
        return self._label
    @label.setter
    def label(self, value):
        self._label = value
        self.ui.lblMain.setText(self._label)
        self.ui.lblMain.adjustSize()
        

    # @property
    # def is_save_mode(self):
    #     """The is_save_mode property."""
    #     return self._is_save_mode
    # @is_save_mode.setter
    # def is_save_mode(self, value):
    #     self._is_save_mode = value
        
    def __init__(self, parent=None, label=None, is_save_mode=False, path_type='folder', allows_multiple=False):
        super().__init__(parent=parent) # Call the inherited classes __init__ method
        self.ui = Ui_Form()
        self.ui.setupUi(self) # builds the design from the .ui onto this widget.
        
        # self._is_save_mode = is_save_mode
        self._label = label
        self.is_save_mode = is_save_mode
        self.path_type = path_type
        self.allows_multiple = allows_multiple
        
        self.initUI()
        self.show() # Show the GUI
        
    def initUI(self):
        self.ui.lblMain.setText(self._label)
        self.ui.lblMain.adjustSize()
        
        pixmapi = getattr(QStyle, 'SP_DirIcon')
        icon = self.style().standardIcon(pixmapi)
        self.ui.btnSelectFile.setIcon(icon)
        self.ui.btnAlternate.setVisible(False)
        
        self.ui.txtFilePath.textChanged.connect(self.on_textChanged) # Re-emit when the text changes
        
        # Dialogs:
        self.ui.fileDialog = None
        self.ui.btnSelectFile.clicked.connect(self.selectPathDialog)
        
           
    def __str__(self):
         return 
     
             
    def reconfigure(self, label=None, is_save_mode=None, path_type=None, allows_multiple=None):
        """ Sets the properties IFF they aren't none, meaning no properties are changed if no inputs are provided. """
        if label is not None:
            self.label = label
        if is_save_mode is not None:
            self.is_save_mode = is_save_mode
        if path_type is not None:
            self.path_type = path_type
        if allows_multiple is not None:
            self.allows_multiple = allows_multiple
        
    @pyqtExceptionPrintingSlot()
    def selectPathDialog(self, startDir=None):
        if startDir is None:
            try:
                current_path = self.path
                if current_path and current_path.exists():
                    startDir = str(current_path)
                else:
                    startDir = '.'
            except:
                startDir = '.'

        # Ensure startDir is always a string
        if not isinstance(startDir, str):
            startDir = '.'

        # self.ui.fileDialog = pg.FileDialog(None, "Select File", startDir, "Custom Eval Node (*.pEval)")
    
        # folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        
        # if self._is_save_mode:
        #     self.ui.fileDialog.setDefaultSuffix("pEval")
        #     self.ui.fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave) 
                    
        # self.ui.fileDialog.show()
        # self.ui.fileDialog.fileSelected.connect(self.onDialogComplete)
        
        ## MODAL MODE:
        
        if self.path_type == 'folder':
             # Select folder mode:
            selected_path = pg.FileDialog.getExistingDirectory(None, "Select Folder", startDir)
        elif self.path_type == 'file':
            selected_path = pg.FileDialog.getOpenFileName(None, "Select File", startDir)
        else:
            raise NotImplementedError
        
       
        self.onDialogComplete(selected_path)
        
    
     
    # def loadFile(self, fileName=None, startDir=None):
    #     """Load a Custom Eval Node (``*.pEval``) file.
    #     """
    #     if fileName is None:
    #         if startDir is None:
    #             startDir = str(self.path)
    #         if startDir is None:
    #             startDir = '.'
    #         self.ui.fileDialog = pg.FileDialog(None, "Load Custom Eval Node..", startDir, "Custom Eval Node (*.pEval)")
    #         self.ui.fileDialog.show()
    #         self.ui.fileDialog.fileSelected.connect(self.onDialogComplete)
    #         return
    #         ## NOTE: was previously using a real widget for the file dialog's parent, but this caused weird mouse event bugs..
        

    # def saveFile(self, fileName=None, startDir=None, suggestedFileName='custom_node.pEval'):
    #     """Save this Custom Eval Node to a .pEval file
    #     """
    #     if fileName is None:
    #         if startDir is None:
    #             startDir = str(self.path)
    #         if startDir is None:
    #             startDir = '.'
    #         self.ui.fileDialog = pg.FileDialog(None, "Save Custom Eval Node..", startDir, "Custom Eval Node (*.pEval)")
    #         self.ui.fileDialog.setDefaultSuffix("pEval")
    #         self.ui.fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave) 
    #         self.ui.fileDialog.show()
    #         self.ui.fileDialog.fileSelected.connect(self.onDialogComplete)
    #         return
        



    @pyqtExceptionPrintingSlot(str)
    def onDialogComplete(self, fileName):
        """ called by the spawned dialog when the user makes a selection """
        print(f'onDialogComplete(filename: {fileName})')
        
        if isinstance(fileName, tuple):
            fileName = fileName[0]  # Qt4/5 API difference
        if fileName == '':
            # Canceled:
            return
        
        # Set the path internally:
        self.path = fileName
        
        # Emit changed signal:
        self.sigFileSelectionChanged.emit(str(fileName))


    @pyqtExceptionPrintingSlot(str)
    def on_textChanged(self, text):
        """ called when the path string changes (even during edits) """   
        ## validate the path
        is_path_valid = self._visually_validate_path(self.path)
        # re-emit the file changed signal
        self.sigFileSelectionChanged.emit(str(self.path))


    def _visually_validate_path(self, path_str):
        """ visually updates the validation by checking the validity of the user-entered path """
        if not self.is_save_mode:
            is_path_valid = self._validate_path(path_str)
            # is_path_valid = self.ui.txtFilePath.hasAcceptableInput() # future
            self.ui.txtFilePath.setStyleSheet(
                "border: 3px solid {color}".format(
                    color="green" if is_path_valid else "red"
                )
            )
        else:
            """ in save_mode we don't want to indicate that potentially valid paths don't exist (because that's often the whole point). Always return valid """
            is_path_valid = True
        return is_path_valid
        
    @classmethod
    def _validate_path(cls, path_str):
        path = Path(path_str)
        return path.exists() # return whether the path exists


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = InlineFilesystemPathSelectWidget()
    Form.show()
    sys.exit(app.exec_())
    