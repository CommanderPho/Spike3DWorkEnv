from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QLabel, QWidget, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
import sys
from typing import List, Tuple

from neuropy.utils.result_context import IdentifyingContext

# Empty session tuple for initialization
empty_session_tuple = {
    'format_name': '',
    'animal': '',
    'exper_name': '',
    'session_name': '',
    'session_descriptor_string': '',
    'id': '<Selection Not Found>',
    'hostname': '',
    'creation_time': '',
    'running_time': '',
    'ping_time': '',
    'monitoring_time': '',
    'size': '',
    'tags': '',
    'entrypoint': ''
}

class LogViewerWidget(QWidget):
    """ 
    from pyphocorehelpers.gui.Qt.testLogFileViewer import LogViewerWidget
    
    """
    def __init__(self, context_indexed_run_logs, most_recent_runs_session_descriptor_string_to_context_map, most_recent_runs_context_indexed_run_extra_data):
        super().__init__()

        self.context_indexed_run_logs = context_indexed_run_logs
        self.most_recent_runs_context_indexed_run_extra_data = most_recent_runs_context_indexed_run_extra_data

        # Tree Widget __________________________________________________________________________________________________ #
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setMinimumWidth(300)
        self.tree_widget.setMaximumWidth(300)
        self.tree_widget.itemSelectionChanged.connect(self.on_tree_selection_changed)
        
        # Load tree data
        self.load_tree_data(list(most_recent_runs_session_descriptor_string_to_context_map.values()))

        # Text area for log display ____________________________________________________________________________________ #
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setMinimumHeight(650)

        # Header layout for displaying session data ____________________________________________________________________ #
        self.header_labels = {}
        self.header_layout = QVBoxLayout()
        display_session_extra_data_keys = ['id', 'hostname', 'creation_time', 'running_time', 'ping_time', 'monitoring_time', 'size', 'tags', 'entrypoint']
        self.build_session_tuple_header(a_session_tuple=empty_session_tuple, included_display_session_extra_data_keys=display_session_extra_data_keys)

        # Main layout __________________________________________________________________________________________________ #
        content_layout = QVBoxLayout()
        content_layout.addLayout(self.header_layout)
        content_layout.addWidget(self.text_area)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.tree_widget)
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)
    
    def load_tree_data(self, included_session_contexts: List):
        """Load the session context into the tree widget."""
        for context in included_session_contexts:
            an_item = QTreeWidgetItem(self.tree_widget, [str(context)])
            an_item.setData(1, 0, context) # column=0, role=0, value=context
            

    def build_session_tuple_header(self, a_session_tuple: dict, included_display_session_extra_data_keys: List[str]):
        """Builds header labels based on session data."""
        for key in included_display_session_extra_data_keys:
            label = QLabel(f"<b>{key}</b>: 'Not Available'", self)
            label.setTextFormat(Qt.RichText)
            self.header_labels[key] = label
            self.header_layout.addWidget(label)

    def update_header_labels(self, new_values):
        """Update header labels with new session data."""
        for key, value in new_values.items():
            if key in self.header_labels:
                self.header_labels[key].setText(f"<b>{key}</b>: {value}")

    def on_tree_selection_changed(self):
        """Handle tree selection change to update session info and log content."""
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            selected_context_name: str = selected_items[0].text(0)
            selected_context: IdentifyingContext = selected_items[0].data(1, 0)
            
            curr_context_extra_data_tuple = self.most_recent_runs_context_indexed_run_extra_data.get(selected_context, {})
            self.update_header_labels(curr_context_extra_data_tuple)

            curr_context_run_log = self.context_indexed_run_logs.get(selected_context, '<Context Not Found>')
            self.text_area.setText(curr_context_run_log)
            self.text_area.moveCursor(QTextCursor.Start)



# Example usage of the LogViewerWidget
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Mock data for demonstration
    context_indexed_run_logs = {
        'session1': 'Log content for session 1...',
        'session2': 'Log content for session 2...',
    }
    
    most_recent_runs_session_descriptor_string_to_context_map = {
        'session1_descriptor': 'session1',
        'session2_descriptor': 'session2',
    }

    most_recent_runs_context_indexed_run_extra_data = {
        'session1': {'id': '1', 'hostname': 'localhost', 'creation_time': '2023-10-01', 'running_time': '30m'},
        'session2': {'id': '2', 'hostname': 'remote', 'creation_time': '2023-10-02', 'running_time': '45m'},
    }

    viewer = LogViewerWidget(context_indexed_run_logs, most_recent_runs_session_descriptor_string_to_context_map, most_recent_runs_context_indexed_run_extra_data)
    viewer.setWindowTitle('Session Log Viewer')
    viewer.show()

    sys.exit(app.exec_())
