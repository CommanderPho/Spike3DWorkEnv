#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QObject, pyqtSignal
from PyQt5.QtWidgets import QPushButton


class ToggleButtonModel(QObject):
    """
    This is the model that controls a ToggleButton. By default, its state is
    True.
    
    
    Usage:
    	from app.model import TimestampModel, ToggleButtonModel, TimestampDelta
    	self.play_pause_model = ToggleButtonModel(None, self)
        self.play_pause_model.setStateMap(
            {
                True: {
                    "text": "",
                    "icon": qta.icon("fa.play", scale_factor=0.7)
                },
                False: {
                    "text": "",
                    "icon": qta.icon("fa.pause", scale_factor=0.7)
                }
            }
        )
        self.ui.button_play_pause.setModel(self.play_pause_model)
        self.ui.button_play_pause.clicked.connect(self.play_pause)
        
        
        
    """
    dataChanged = pyqtSignal()
    stateChanged = pyqtSignal(bool)

    def __init__(self, state_map=None, parent=None):
        super(ToggleButtonModel, self).__init__(parent)
        self.state = True
        if state_map:
            self.state_map = state_map
        else:
            self.state_map = {
                True: {
                    "text": None,
                    "icon": None,
                },
                False: {
                    "text": None,
                    "icon": None
                }
            }

    def setStateMap(self, state_map):
        self.state_map = state_map
        self.dataChanged.emit()

    def getText(self, state):
        return self.state_map[state]["text"]

    def getIcon(self, state):
        return self.state_map[state]["icon"]

    def getState(self):
        return self.state

    def setState(self, state):
        self.state = state
        self.stateChanged.emit(self.state)


class ToggleButton(QPushButton):
    """
    This is a QPushButton that supports toggling. It can have two states: True
    or False, each has its own set of text and icon. The button is controlled
    by a ToggleButtonModel. Without a model, the button behaves exactly like
    a QPushButton
    """
    stateChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(ToggleButton, self).__init__(parent)
        self.model = None
        self.clicked.connect(self.toggle)

    def toggle(self):
        if not self.model:
            return
        self.model.setState(not self.model.getState())

    def _stateChangeHandler(self):
        if not self.model:
            return
        self.setText(self.model.getText(self.model.getState()))
        self.setIcon(self.model.getIcon(self.model.getState()))
        self.stateChanged.emit(self.model.getState())

    def setModel(self, model):
        """
        Use a model for this button. The model will notify this button when a
        new state is required
        :param model: The model to use
        :return: None
        """
        self.model = model
        self._stateChangeHandler()
        self.model.dataChanged.connect(self._stateChangeHandler)
        self.model.stateChanged.connect(self._stateChangeHandler)

