from typing import Optional
from qtpy import QtCore, QtWidgets

def find_tree_item_by_text(tree_widget: QtWidgets.QTreeWidget, text: str) -> Optional[QtWidgets.QTreeWidgetItem]:
    """
    from pyphocorehelpers.gui.Qt.tree_helpers import find_tree_item_by_text
    
    # Assuming self.treeWidget is your QTreeWidget instance
    item_text_to_find = "_display_spike_rasters_window"
    found_item = find_tree_item_by_text(treeWidget, item_text_to_find)

    if found_item is not None:
        # Do something with the found item
        print("Item found:", found_item.text(0))
    else:
        print("Item not found:", item_text_to_find)

    """
    # Iterate through top level items
    for i in range(tree_widget.topLevelItemCount()):
        top_item = tree_widget.topLevelItem(i)
        result = find_tree_item_recursive(top_item, text)
        if result is not None:
            return result
    return None

def find_tree_item_recursive(parent_item: QtWidgets.QTreeWidgetItem, text: str) -> Optional[QtWidgets.QTreeWidgetItem]:
    # Check children of the current item recursively
    if parent_item.text(0) == text:
        return parent_item
    
    # Check children items
    for i in range(parent_item.childCount()):
        child = parent_item.child(i)
        result = find_tree_item_recursive(child, text)
        if result is not None:
            return result
    
    # If not found, return None
    return None