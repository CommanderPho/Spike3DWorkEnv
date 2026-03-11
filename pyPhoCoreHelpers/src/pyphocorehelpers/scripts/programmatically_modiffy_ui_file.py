import sys
from PyQt5 import QtCore, QtXml

""" from https://stackoverflow.com/questions/52029649/qtdesigner-pyqt-pyside-disable-translatable-by-default 
Supposedly takes a .ui file produced by uic and QtDesigner and turns off the "Translatable" property, cleaning up the code.
UNTESTED

Other Discussion:
https://stackoverflow.com/questions/51483773/how-can-i-remove-the-translatable-checkbox-in-qt-designer-for-a-qstring-proper
https://doc.qt.io/qt-5/designer-creating-custom-widgets.html#notes-on-the-domxml-function
https://doc.qt.io/qt-5/qtdesigner-customwidgetplugin-example.html
https://doc.qt.io/qt-5/quiloader.html - The QUiLoader class enables standalone applications to dynamically create user interfaces at run-time using the information stored in UI files or specified in plugin paths.

"""

class QtDesigner_UiFile_Modifications:
    """docstring for QtDesigner_UiFile_Modifications."""
    # def __init__(self, arg):
    #     super(QtDesigner_UiFile_Modifications, self).__init__()
    
    @classmethod
    def make_non_translatable(cls, doc):
        """ removes the Translatable properties from all strings """
        strings = doc.elementsByTagName("string")
        for i in range(strings.count()):
            strings.item(i).toElement().setAttribute("notr", "true")
        return doc

# action

    @classmethod
    def modify_ui_file(cls, filename="/path/of/your_file.ui"):
        """ the main call function. Opens the file, loads it into XML, modifies it if needed, and then writes it back out. """
        file = QtCore.QFile(filename)
        if not file.open(QtCore.QFile.ReadOnly):
            print(f'failed ot open file "{filename}"')
            sys.exit(-1)

        doc = QtXml.QDomDocument()
        if not doc.setContent(file):
            print(f'failed to open file "{filename}" as XML content')
            sys.exit(-1)
        file.close()
        ## Have the file in doc

        # Get the properties and make the changes:
        doc = cls.make_non_translatable(doc)

        # Re-open the file to write out the changes in doc:
        if not file.open(QtCore.QFile.Truncate|QtCore.QFile.WriteOnly):
            print(f'failed to write out the changes to the file: "{filename}"')
            sys.exit(-1)

        xml = doc.toByteArray()
        file.write(xml)
        file.close()



if __name__ == '__main__':
    filename = r"C:\Users\pho\repos\pyPhoPlaceCellAnalysis\src\pyphoplacecellanalysis\GUI\Qt\Menus\GlobalApplicationMenusMainWindow\GlobalApplicationMenusMainWindow.ui"
    QtDesigner_UiFile_Modifications.modify_ui_file(filename=filename)