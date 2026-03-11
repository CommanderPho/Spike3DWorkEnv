from qtpy import QtCore, QtWidgets, uic
from PyQt5.QtCore import Qt

def get_spacer_at(layout, row, column):
    item = layout.itemAtPosition(row, column)
    if item and item.spacerItem():
        return item.spacerItem()
    return None


def get_all_spacer_items(widget):
    """
    Returns a flat list of all QSpacerItems in the widget.
    
    Args:
        widget: A QWidget instance to search for spacers
        
    Returns:
        list: All QSpacerItems found in the widget's layouts
    """
    spacers = []
    
    def process_layout(layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            # Check if this item is a spacer
            if item.spacerItem():
                spacers.append(item.spacerItem())
            # If it's a layout, process it recursively
            elif item.layout():
                process_layout(item.layout())
            # If it's a widget with a layout, process that layout
            elif item.widget() and item.widget().layout():
                process_layout(item.widget().layout())
    
    # Start with the widget's main layout
    if widget.layout():
        process_layout(widget.layout())
    
    return spacers


# @function_attributes(short_name=None, tags=['UNUSED', 'UNTESTED', 'alternative', 'post-hoc', 'qt-creator', 'pyqt5', 'spacers', 'workaround'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-03-11 03:45', related_items=['load_ui_with_named_spacers'])
# def attach_named_spacers(ui_object, layout):
#     """Alternative to `load_ui_with_named_spacers` that uses the normal uic.load(...) and then finds the spacers post-hoc in the layout and attaches them to the ui object by name.
    
#     """
#     for i in range(layout.count()):
#         layout_item = layout.itemAt(i)
#         if layout_item.spacerItem():
#             # Get the name from the object name property
#             spacer_name = layout_item.spacerItem().objectName()
#             if spacer_name:
#                 setattr(ui_object, spacer_name, layout_item.spacerItem())




# @function_attributes(short_name=None, tags=['uic', 'qt-creator', 'pyqt5', 'spacers', 'workaround'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-03-11 03:45', related_items=[])
def load_ui_with_named_spacers(ui_file, base_instance=None):
    """Loads a UI file and makes spacers accessible by name.
    
    from pyphocorehelpers.gui.Qt.QtUIC_Helpers import load_ui_with_named_spacers
    
    Replaces `uic.load(...)` initialization:
    
    ```
    class Spike3DRasterLeftSidebarControlBar(QWidget):
        def __init__(self, parent=None):
			super().__init__(parent=parent) # Call the inherited classes __init__ method
			self.ui = uic.loadUi(uiFile, self) # Load the .ui file
			self.initUI()
			self.show() # Show the GUI
    ```
    with
    ```
    class Spike3DRasterLeftSidebarControlBar(QWidget):
        def __init__(self, parent=None):
			super().__init__(parent=parent) # Call the inherited classes __init__ method
			self.ui = load_ui_with_named_spacers(uiFile, self) # Load the .ui file
			self.initUI()
			self.show() # Show the GUI
	```
    
    """
    if base_instance is None:
        ui = uic.loadUi(ui_file)
    else:
        ui = uic.loadUi(ui_file, base_instance)
    
    # Get all spacers in your widget
    horizontal_spacers = []
    vertical_spacers = []
    all_spacers = get_all_spacer_items(ui)
    for i, a_spacer in enumerate(all_spacers):
        # Identify horizontal spacers by checking size hints
        # Horizontal spacers have fixed height and variable width
        size_hint = a_spacer.sizeHint()
        size_policy = a_spacer.sizePolicy()
        h_policy = size_policy.horizontalStretch()
        v_policy = size_policy.verticalStretch()
        expanding_dir = a_spacer.expandingDirections()
        # if expanding_dir == Qt.Horizontal
        # Check if it's a horizontal spacer (fixed height, variable width)
        is_horizontal: bool = (h_policy > 0 or size_hint.width() > size_hint.height() or (size_hint.width() > 0 and size_hint.height() == 0))
        if is_horizontal:
            spacer_orientation_rel_index: int = len(horizontal_spacers)
            spacer_orientation_prefix: str = f"horizontalSpacer"
            horizontal_spacers.append(a_spacer)
        else:
            ## otherwise must be vertical
            spacer_orientation_rel_index: int = len(vertical_spacers)
            spacer_orientation_prefix: str = f"verticalSpacer"        
            vertical_spacers.append(a_spacer)

        spacer_name: str = f"{spacer_orientation_prefix}_{spacer_orientation_rel_index}" # horizontalSpacer_6
        setattr(ui, spacer_name, a_spacer.spacerItem())
            
    return ui

