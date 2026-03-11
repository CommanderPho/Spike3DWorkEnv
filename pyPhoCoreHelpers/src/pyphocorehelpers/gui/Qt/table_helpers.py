from copy import deepcopy
from typing import Optional
import numpy as np
import sys
import os

# from qtpy import QtCore, QtWidgets, QtGui
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction
from PyQt5.QtWidgets import QWidget, QHeaderView
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont, QIcon
from PyQt5.QtCore import Qt, QPoint, QRect, QObject, QEvent, pyqtSignal, pyqtSlot, QSize, QDir


class TableContextMenuProviderDelegate:
    """ implementors provide context menus for clicked table cells
    
    from pyphocorehelpers.gui.Qt.table_helpers import CustomContextTableWidget, TableContextMenuProviderDelegate
    
    
    """
    def get_context_menu(self, target_table, row_index: Optional[int]=None, column_index: Optional[int]=None, is_row_header: bool=False, is_column_header: bool=False) -> QMenu:
        raise NotImplementedError(f'Implementors must override and provide this function!')
    



class CustomContextTableWidget(QTableWidget):
    """ provides specific context menus based on whether the user right-clicked in the row/col headers, a cell, or elsewhere 
    """
    def __init__(self, rows: Optional[int]=None, columns: Optional[int]=None, context_menu_delegate: Optional[TableContextMenuProviderDelegate]=None, parent: Optional[QWidget] = None):
        if (rows is not None) or (columns is not None):
            super().__init__(rows, columns, parent=parent)
        else:
            super().__init__(parent=parent)
            
        self._debug_print = False
        self._context_menu_delegate = context_menu_delegate

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_cell_menu)

        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.show_column_header_menu)
        
        self.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(self.show_row_header_menu)
        
        

    def show_cell_menu(self, pos):
        # Get the cell that was clicked
        index = self.indexAt(pos)
        if not index.isValid():
            return  # Ignore clicks outside valid cells

        row, col = index.row(), index.column()
        # print(f'show_cell_menu(pos: {pos}):\n\trow: {row}, col: {col}')
        
        menu: Optional[QMenu] = None
        if self._context_menu_delegate is not None:
            # print(f'\t has context_menu_delegate!')
            menu = self._context_menu_delegate.get_context_menu(target_table=self, row_index=row, column_index=col, is_row_header=False, is_column_header=False)
        else:
            print(f'CustomTableWidget: has no context menu delegate!')
            pass

        if menu is None: 
            ## still has no menu, make default:
            menu = QMenu(self)
            action_edit = QAction(f"Edit Cell ({row}, {col})", self)
            action_delete = QAction(f"Delete Cell ({row}, {col})", self)
            action_info = QAction(f"Cell Info ({row}, {col})", self)

            action_edit.triggered.connect(lambda: self.editItem(self.item(row, col)))
            action_delete.triggered.connect(lambda: self.setItem(row, col, None))
            action_info.triggered.connect(lambda: print(f"Cell ({row}, {col}): {self.item(row, col).text() if self.item(row, col) else 'Empty'}"))

            menu.addAction(action_edit)
            menu.addAction(action_delete)
            menu.addAction(action_info)

        ## cell `menu.exec_(...)` to display the menu:
        menu.exec_(self.viewport().mapToGlobal(pos))
        


    def show_row_header_menu(self, pos):
        # Convert local position to global position
        header = self.verticalHeader()
        global_pos = header.mapToGlobal(pos)

        # Determine which column was clicked
        row = header.logicalIndexAt(pos.y())

        if row >= 0:  # Ensure it's a valid column
            if self._debug_print:
                print(f'show_row_header_menu(pos: {pos}):\n\trow: {row}')
            menu: Optional[QMenu] = None
            if self._context_menu_delegate is not None:
                if self._debug_print:
                    print(f'\t has context_menu_delegate!')
                menu = self._context_menu_delegate.get_context_menu(target_table=self, row_index=row, column_index=None, is_row_header=True, is_column_header=False)
            else:
                print(f'CustomTableWidget: has no context menu delegate!')
                pass
            if menu is None: 
                ## still has no menu, make default:
                menu = QMenu(self)

                action_sort = QAction(f"Sort Row {row}", self)
                action_hide = QAction(f"Hide Row {row}", self)
                action_resize = QAction(f"Resize Row {row}", self)

                action_sort.triggered.connect(lambda: print(f"Sorting row {row}"))
                action_hide.triggered.connect(lambda: self.setRowHidden(row, True))
                action_resize.triggered.connect(lambda: header.resizeSection(row, 100))

                menu.addAction(action_sort)
                menu.addAction(action_hide)
                menu.addAction(action_resize)

            ## cell `menu.exec_(...)` to display the menu:
            menu.exec_(global_pos)
            

    def show_column_header_menu(self, pos):
        # Convert local position to global position
        header = self.horizontalHeader()
        global_pos = header.mapToGlobal(pos)

        # Determine which column was clicked
        col = header.logicalIndexAt(pos.x())

        if col >= 0:  # Ensure it's a valid column
            if self._debug_print:
                print(f'show_column_header_menu(pos: {pos}):\n\tcol: {col}')
            menu: Optional[QMenu] = None
            if self._context_menu_delegate is not None:
                if self._debug_print:
                    print(f'\t has context_menu_delegate!')
                menu = self._context_menu_delegate.get_context_menu(target_table=self, row_index=None, column_index=col, is_row_header=False, is_column_header=True)
            else:
                print(f'CustomTableWidget: has no context menu delegate!')
                pass 
               
            if menu is None: 
                ## still has no menu, make default:
                menu = QMenu(self)
                action_sort = QAction(f"Sort Column {col}", self)
                action_hide = QAction(f"Hide Column {col}", self)
                action_resize = QAction(f"Resize Column {col}", self)

                action_sort.triggered.connect(lambda: print(f"Sorting column {col}"))
                action_hide.triggered.connect(lambda: self.setColumnHidden(col, True))
                action_resize.triggered.connect(lambda: header.resizeSection(col, 100))

                menu.addAction(action_sort)
                menu.addAction(action_hide)
                menu.addAction(action_resize)

            menu.exec_(global_pos)
            



# ==================================================================================================================== #
# Table Sizing Helpers                                                                                                 #
# ==================================================================================================================== #

class TableSizingHelpers:
    """ Helps compute the required height for a QTableView or QTableWidget so that scroll-bars aren't needed


    from pyphocorehelpers.gui.Qt.table_helpers import TableSizingHelpers
    
    
    """
    @classmethod
    def determine_required_table_height(cls, table_view) -> int:
        """ Returns the required height for the table to show all of its rows without a vertical scroll bar
        
        from pyphocorehelpers.gui.Qt.table_helpers import TableSizingHelpers
        
        total_height: int = TableSizingHelpers.determine_required_table_height(table_view)
        print(f'total_height: {total_height}')
        table_view.setMinimumHeight(total_height)  # Set the required height
        table_view.setMaximumHeight(total_height)  # Prevent scrolling

        
        """
        total_height = table_view.horizontalHeader().height()  # Height of the header
        for row in range(table_view.model().rowCount()):
            total_height += table_view.rowHeight(row)  # Sum all row heights

        total_height += table_view.frameWidth() * 2  # Include frame borders
        return total_height

    @classmethod
    def determine_required_table_width(cls, table_view) -> int:
        """ Returns the required width for the table to show all of its columns without a horizontal scroll bar
        from pyphocorehelpers.gui.Qt.table_helpers import TableSizingHelpers
        
        total_width: int = TableSizingHelpers.determine_required_table_width(table_view)
        print(f'total_width: {total_width}')
        table_view.setMinimumWidth(total_width)  # Set the required width
        table_view.setMaximumWidth(total_width)  # Prevent scrolling

        
        """
        total_width = table_view.verticalHeader().width()  # Width of the row header (if visible)

        for col in range(table_view.model().columnCount()):
            total_width += table_view.columnWidth(col)  # Sum all column widths

        total_width += table_view.frameWidth() * 2  # Include frame borders
        return total_width
    

