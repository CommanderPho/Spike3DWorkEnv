from typing import Optional
from functools import wraps
from attrs import define, field, Factory, asdict, astuple
from qtpy import QtCore, QtWidgets


@define(slots=False)
class AttrsQtObject(QtCore.QObject):
    """ 
    Normally init
    
    def __init__(self, ..., parent=None):
        super(AttrsQtObject, self).__init__(parent)

    """
    
    def __attrs_pre_init__(self):
        # super().__init__(parent=None) # normally have to do: super(ToggleButtonModel, self).__init__(parent)
        QtCore.QObject.__init__(self) # some inheritors of QObject seem to do this instead
        # note that the use of super() is often avoided because Qt does not allow to inherit from multiple QObject subclasses.
