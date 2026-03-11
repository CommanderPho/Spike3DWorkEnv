#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QFrame, QGridLayout, QSlider, QStyle, QStyleOptionSlider, QPlainTextEdit, QPushButton

# from PyQt5 import QtGui
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen
from PyQt5.QtCore import pyqtSignal, QRect


class HighlightedJumpSlider(QSlider):
    """
    Slider that allows user to jump to any point on it, regardless of steps.
    It also supports partial highlighting.
    """
    def __init__(self, parent=None):
        super(HighlightedJumpSlider, self).__init__(parent)
        self.highlightStart = None
        self.highlightEnd = None

    def mousePressEvent(self, ev):
        """ Jump to click position """
        self.setValue(QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), ev.x(), self.width())
        )

    def mouseMoveEvent(self, ev):
        """ Jump to pointer position while moving """
        self.setValue(QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), ev.x(), self.width())
        )

    def setHighlight(self, start, end):
        if start is not None and end is not None and start < end:
            self.highlightStart, self.highlightEnd = start, end

    def paintEvent(self, event):
        if self.highlightStart is not None and self.highlightEnd is not None:
            p = QPainter(self)
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            gr = self.style().subControlRect(QStyle.CC_Slider, opt,
                                             QStyle.SC_SliderGroove, self)
            rectX, rectY, rectW, rectH = gr.getRect()
            startX = int(
                (rectW/(self.maximum() - self.minimum()))
                * self.highlightStart + rectX
            )
            startY = (rectH - rectY) / 2
            width = int(
                (rectW/(self.maximum() - self.minimum()))
                * self.highlightEnd + rectX
            ) - startX
            height = (rectH - startY) / 2
            c = QColor(0, 152, 116)
            p.setBrush(c)
            c.setAlphaF(0.3)
            p.setPen(QPen(c, 1.0))
            rectToPaint = QRect(startX, startY, width, height)
            p.drawRects(rectToPaint)
        super(HighlightedJumpSlider, self).paintEvent(event)
