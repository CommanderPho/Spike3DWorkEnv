"""
PyQt Signal Snooper

A non-invasive utility for monitoring PyQt5/PySide signal emissions from an object
and its child widget tree. Uses connection-based monitoring to guarantee it doesn't
affect application behavior.

Usage with callback:
    from pyphocorehelpers.gui.Qt.SignalSnooper import SignalSnooper
    
    def my_callback(signal_name, emitting_object, args, kwargs, timestamp):
        print(f"Signal '{signal_name}' emitted from {type(emitting_object).__name__}")
    
    snooper = SignalSnooper(my_widget, callback=my_callback, include_children=True)
    snooper.start()
    snooper.stop()

Usage with widget window (recommended for Jupyter notebooks):
    from pyphocorehelpers.gui.Qt.SignalSnooper import create_snooper_with_widget
    
    snooper, widget = create_snooper_with_widget(my_widget)
    widget.show()  # Show the monitoring window
    snooper.start()  # Start monitoring
    
    # Widget features:
    # - Scrollable display with line limit
    # - Pause/Resume button
    # - Filter by signal name
    # - Clear button
    # - Statistics display
    # - Rate-limited updates to prevent flooding
    
    snooper.stop()  # Stop monitoring
"""

import time
import inspect
import weakref
from typing import Optional, Callable, List, Dict, Any, Set
from collections import defaultdict, deque
from threading import Lock

try:
    from qtpy import QtCore, QtWidgets
    from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                                 QPushButton, QLabel, QCheckBox, QLineEdit, QSpinBox)
    from qtpy.QtCore import Qt, QTimer
    from qtpy.QtGui import QFont
    # Try to get Signal types for detection
    try:
        from qtpy.QtCore import Signal as QtSignal, pyqtSignal
        _SIGNAL_TYPES = (QtSignal, pyqtSignal)
    except ImportError:
        try:
            from PyQt5.QtCore import pyqtSignal
            _SIGNAL_TYPES = (pyqtSignal,)
        except ImportError:
            try:
                from PySide2.QtCore import Signal as QtSignal
                _SIGNAL_TYPES = (QtSignal,)
            except ImportError:
                # Fallback: try to detect at runtime
                _SIGNAL_TYPES = None
except ImportError:
    try:
        from PyQt5.QtCore import QObject, pyqtSignal, Qt, QTimer
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                                     QPushButton, QLabel, QCheckBox, QLineEdit, QSpinBox)
        from PyQt5.QtGui import QFont
        from PyQt5 import QtWidgets, QtCore
        _SIGNAL_TYPES = (pyqtSignal,)
    except ImportError:
        raise ImportError("Could not import PyQt5, PySide2, or qtpy")


class _SignalLogger(QtCore.QObject):
    """Internal QObject that provides logging slots for signal monitoring."""
    
    def __init__(self, signal_name: str, emitting_object: Any, callback: Optional[Callable], 
                 emission_stats: Dict[str, int], signal_name_filter: Optional[List[str]]):
        super().__init__()
        self.signal_name = signal_name
        self.emitting_object_ref = weakref.ref(emitting_object) if emitting_object else None
        self.callback = callback
        self.emission_stats = emission_stats
        self.signal_name_filter = signal_name_filter
        self.start_time = time.time()
    
    def log_emission(self, *args, **kwargs):
        """Slot that gets called when a signal is emitted."""
        try:
            # Check if this signal should be monitored
            if self.signal_name_filter is not None:
                if self.signal_name not in self.signal_name_filter:
                    return
            
            # Get the emitting object (use weakref to avoid keeping it alive)
            emitting_object = self.emitting_object_ref() if self.emitting_object_ref else None
            
            # Update statistics
            self.emission_stats[self.signal_name] += 1
            
            # Calculate timestamp
            timestamp = time.time() - self.start_time
            
            # Call user callback if provided
            if self.callback:
                try:
                    self.callback(
                        signal_name=self.signal_name,
                        emitting_object=emitting_object,
                        args=args,
                        kwargs=kwargs,
                        timestamp=timestamp
                    )
                except Exception as e:
                    # Isolate callback errors - don't let them affect the application
                    print(f"SignalSnooper: Error in callback for signal '{self.signal_name}': {e}")
        except Exception as e:
            # Isolate all logging errors - never let them affect the application
            print(f"SignalSnooper: Error logging signal emission: {e}")


class SignalSnooper:
    """
    Non-invasive signal monitoring utility for PyQt5/PySide applications.
    
    Monitors signal emissions from a target object and optionally its child widget tree.
    Uses connection-based monitoring (connecting to signals) rather than intercepting
    emit calls, guaranteeing it doesn't affect application behavior.
    
    Safety Guarantees:
    - Never modifies signal objects or their emit methods
    - All logging code is exception-isolated
    - Uses Qt's normal signal/slot mechanism (no timing changes)
    - Provides explicit cleanup to remove all connections
    - Uses weak references to avoid circular dependencies
    """
    
    def __init__(self, 
                 target_object: QtCore.QObject,
                 callback: Optional[Callable[[str, Any, tuple, dict, float], None]] = None,
                 include_children: bool = True,
                 signal_name_filter: Optional[List[str]] = None):
        """
        Initialize the signal snooper.
        
        Args:
            target_object: QObject to monitor for signal emissions
            callback: Optional function called for each signal emission with signature:
                     callback(signal_name: str, emitting_object: Any, args: tuple, 
                             kwargs: dict, timestamp: float) -> None
            include_children: If True, recursively monitor child QObjects in the widget tree
            signal_name_filter: Optional list of signal names to monitor (None = all signals)
        
        The callback receives:
            - signal_name: Name of the signal that was emitted
            - emitting_object: The QObject that emitted the signal (may be None if object was destroyed)
            - args: Tuple of positional arguments passed to the signal
            - kwargs: Dict of keyword arguments passed to the signal (usually empty for Qt signals)
            - timestamp: Time since snooper started (in seconds)
        """
        if not isinstance(target_object, QtCore.QObject):
            raise TypeError(f"target_object must be a QObject, got {type(target_object)}")
        
        self.target_object = target_object
        self.callback = callback
        self.include_children = include_children
        self.signal_name_filter = signal_name_filter
        
        # Track all connections for cleanup
        self._connections: List[tuple] = []  # List of (signal, logger) tuples
        self._loggers: List[_SignalLogger] = []  # Keep references to loggers
        self._monitored_objects: Set[QtCore.QObject] = set()
        self._is_monitoring = False
        
        # Statistics
        self._emission_stats: Dict[str, int] = defaultdict(int)
        self._start_time = None
    
    def start(self):
        """Begin monitoring signals from the target object and optionally its children."""
        if self._is_monitoring:
            return
        
        self._start_time = time.time()
        self._monitor_object(self.target_object)
        
        if self.include_children:
            self._monitor_children(self.target_object)
        
        self._is_monitoring = True
    
    def stop(self):
        """Stop monitoring and disconnect all logging connections."""
        if not self._is_monitoring:
            return
        
        # Disconnect all connections
        for signal, logger in self._connections:
            try:
                signal.disconnect(logger.log_emission)
            except (TypeError, RuntimeError):
                # Signal might already be disconnected or object destroyed
                pass
        
        # Clear all tracking
        self._connections.clear()
        self._loggers.clear()
        self._monitored_objects.clear()
        self._is_monitoring = False
    
    def _monitor_object(self, obj: QtCore.QObject):
        """Monitor all signals on a single object."""
        if obj in self._monitored_objects:
            return  # Already monitoring this object
        
        if not isinstance(obj, QtCore.QObject):
            return
        
        # Find all signals on this object
        signals = self._find_signals(obj)
        
        # Connect to each signal
        for signal_name, signal in signals.items():
            try:
                # Create a logger for this signal
                logger = _SignalLogger(
                    signal_name=signal_name,
                    emitting_object=obj,
                    callback=self.callback,
                    emission_stats=self._emission_stats,
                    signal_name_filter=self.signal_name_filter
                )
                
                # Connect the signal to the logger's slot
                signal.connect(logger.log_emission)
                
                # Track the connection for cleanup
                self._connections.append((signal, logger))
                self._loggers.append(logger)
                
            except (TypeError, RuntimeError) as e:
                # Some signals might not be connectable (e.g., built-in Qt signals)
                # This is fine - just skip them
                pass
        
        self._monitored_objects.add(obj)
    
    def _monitor_children(self, parent: QtCore.QObject):
        """Recursively monitor all child QObjects."""
        if not isinstance(parent, QtCore.QObject):
            return
        
        try:
            # Find all child QObjects
            children = parent.findChildren(QtCore.QObject)
            
            for child in children:
                # Skip if already monitoring
                if child in self._monitored_objects:
                    continue
                
                # Monitor this child
                self._monitor_object(child)
                
                # Recursively monitor its children
                if self.include_children:
                    self._monitor_children(child)
        
        except Exception as e:
            # Handle any errors gracefully (e.g., object destroyed during iteration)
            pass
    
    def _find_signals(self, obj: QtCore.QObject) -> Dict[str, Any]:
        """
        Find all signals on an object using introspection.
        
        Returns a dict mapping signal names to signal objects.
        """
        signals = {}
        
        # Get the object's class and all its base classes
        classes = [obj.__class__] + list(inspect.getmro(obj.__class__))
        
        # Check each class for signal attributes
        seen_names = set()
        for cls in classes:
            # Use getmembers to get all attributes, including those from base classes
            for name, attr in inspect.getmembers(cls):
                # Skip private attributes and duplicates
                if name.startswith('_') or name in seen_names:
                    continue
                
                try:
                    # Check if the class attribute is a Signal descriptor
                    # Signal descriptors have specific type names
                    is_signal_descriptor = self._is_signal_descriptor(attr)
                    
                    if is_signal_descriptor:
                        # Get the instance-bound signal
                        instance_signal = getattr(obj, name, None)
                        if instance_signal is not None:
                            # Verify the bound signal has connect method (it should)
                            if hasattr(instance_signal, 'connect') and hasattr(instance_signal, 'emit'):
                                signals[name] = instance_signal
                                seen_names.add(name)
                
                except (AttributeError, TypeError, RuntimeError):
                    # Attribute might not exist on instance, or might not be accessible
                    # Some attributes might raise errors when accessed
                    continue
        
        return signals
    
    def _is_signal_descriptor(self, obj: Any) -> bool:
        """Check if an object is a Signal or pyqtSignal descriptor (class attribute)."""
        if obj is None:
            return False
        
        obj_type = type(obj)
        type_name = obj_type.__name__
        
        # Check for Signal descriptor type names
        # PyQt5: 'pyqtSignal' or 'Signal'
        # PySide: 'Signal'
        if 'Signal' in type_name or 'pyqtSignal' in type_name:
            # Signal descriptors are class attributes, not instances
            # They don't have connect/emit directly, but the type name indicates they're signals
            return True
        
        # Try using known signal types if available (for isinstance check)
        if _SIGNAL_TYPES is not None:
            try:
                return isinstance(obj, _SIGNAL_TYPES)
            except TypeError:
                # isinstance might fail for some signal types
                pass
        
        return False
    
    def get_emission_count(self, signal_name: Optional[str] = None) -> int:
        """
        Get count of signal emissions.
        
        Args:
            signal_name: If provided, return count for this specific signal.
                       If None, return total count for all signals.
        
        Returns:
            Number of emissions
        """
        if signal_name is None:
            return sum(self._emission_stats.values())
        else:
            return self._emission_stats.get(signal_name, 0)
    
    def get_all_emission_counts(self) -> Dict[str, int]:
        """Get a dictionary of all signal names and their emission counts."""
        return dict(self._emission_stats)
    
    def clear_stats(self):
        """Clear all emission statistics."""
        self._emission_stats.clear()
        # Reset start time
        if self._is_monitoring:
            self._start_time = time.time()
    
    def get_monitored_objects_count(self) -> int:
        """Get the number of objects being monitored."""
        return len(self._monitored_objects)
    
    def __enter__(self):
        """Context manager entry - automatically starts monitoring."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically stops monitoring."""
        self.stop()
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.stop()
        except:
            pass


class SignalSnooperWidget(QWidget):
    """
    A Qt widget window for displaying signal emissions safely.
    
    Features:
    - Scrollable text display with maximum line limit
    - Rate-limited updates to prevent flooding
    - Pause/resume functionality
    - Filter by signal name
    - Clear button
    - Statistics display
    - Thread-safe queue for async updates
    """
    
    def __init__(self, parent=None, max_lines: int = 1000, update_interval_ms: int = 100):
        """
        Initialize the signal snooper widget.
        
        Args:
            parent: Parent widget (optional)
            max_lines: Maximum number of lines to keep in display (older lines are removed)
            update_interval_ms: How often to update the display (in milliseconds)
        """
        super().__init__(parent)
        self.max_lines = max_lines
        self.update_interval_ms = update_interval_ms
        
        # Thread-safe queue for pending emissions
        self._emission_queue = deque()
        self._queue_lock = Lock()
        
        # State
        self._is_paused = False
        self._line_count = 0
        self._total_emissions = 0
        
        # Deduplication state
        self._last_line = None
        self._duplicate_count = 0
        
        # Initialize UI
        self._init_ui()
        
        # Start update timer
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._process_queue)
        self._update_timer.start(self.update_interval_ms)
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Signal Snooper Monitor")
        self.setGeometry(100, 100, 800, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Pause button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setCheckable(True)
        self.pause_button.toggled.connect(self._on_pause_toggled)
        control_layout.addWidget(self.pause_button)
        
        # Clear button
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._on_clear)
        control_layout.addWidget(clear_button)
        
        # Filter input
        control_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Signal name filter (empty = all)")
        self.filter_input.textChanged.connect(self._on_filter_changed)
        control_layout.addWidget(self.filter_input)
        
        # Max lines input
        control_layout.addWidget(QLabel("Max lines:"))
        self.max_lines_spin = QSpinBox()
        self.max_lines_spin.setMinimum(100)
        self.max_lines_spin.setMaximum(10000)
        self.max_lines_spin.setValue(self.max_lines)
        self.max_lines_spin.valueChanged.connect(self._on_max_lines_changed)
        control_layout.addWidget(self.max_lines_spin)
        
        # Statistics label
        self.stats_label = QLabel("Emissions: 0")
        control_layout.addWidget(self.stats_label)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # Text display
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        # Set font using QFont object to ensure it actually applies
        font = QFont("Courier", 8)
        # Try different ways to set monospace style hint depending on Qt version
        try:
            font.setStyleHint(QFont.StyleHint.Monospace)
        except AttributeError:
            try:
                font.setStyleHint(QFont.Monospace)
            except AttributeError:
                pass  # Just use Courier family without style hint
        self.text_display.setFont(font)
        main_layout.addWidget(self.text_display)
        
        self.setLayout(main_layout)
    
    def add_emission(self, signal_name: str, emitting_object: Any, args: tuple, 
                     kwargs: dict, timestamp: float):
        """
        Add a signal emission to the display queue (thread-safe).
        
        This method can be called from any thread safely.
        """
        # Format the emission info
        obj_type = type(emitting_object).__name__ if emitting_object else "None"
        args_str = ', '.join(str(arg)[:50] for arg in args[:3])
        if len(args) > 3:
            args_str += f', ... (+{len(args) - 3} more)'
        
        line = f"[{timestamp:.4f}s] {obj_type}.{signal_name}({args_str})"
        
        # Add to queue (thread-safe)
        with self._queue_lock:
            self._emission_queue.append(line)
            # Limit queue size to prevent memory issues
            if len(self._emission_queue) > self.max_lines * 2:
                self._emission_queue.popleft()
    
    def _process_queue(self):
        """Process pending emissions from the queue (called by timer)."""
        if self._is_paused:
            return
        
        # Get items from queue (thread-safe)
        items_to_add = []
        with self._queue_lock:
            # Take up to 50 items at a time to prevent UI freezing
            for _ in range(min(50, len(self._emission_queue))):
                if self._emission_queue:
                    items_to_add.append(self._emission_queue.popleft())
        
        if not items_to_add:
            # Flush any pending duplicate when queue is empty
            # This ensures we show duplicates even if emissions stop temporarily
            if self._last_line is not None:
                self._flush_duplicate()
            return
        
        # Get current filter
        filter_text = self.filter_input.text().strip().lower()
        
        # Process items with deduplication
        for line in items_to_add:
            # Apply filter first
            if filter_text and filter_text not in line.lower():
                # Still count filtered emissions in total, but don't display
                self._total_emissions += 1
                continue  # Skip filtered lines (don't count as duplicates)
            
            # Count this emission
            self._total_emissions += 1
            
            # Check if this line is a duplicate of the last displayed one
            if line == self._last_line:
                self._duplicate_count += 1
            else:
                # Flush the previous line (with duplicate count if any)
                self._flush_duplicate()
                # Start tracking this new line
                self._last_line = line
                self._duplicate_count = 0
        
        # Remove old lines if over limit (do this once after adding all items)
        if self._line_count > self.max_lines:
            # Get the document and remove lines from the beginning
            doc = self.text_display.document()
            cursor = self.text_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            
            # Count how many lines to remove
            lines_to_remove = self._line_count - self.max_lines
            
            # Move down to the line we want to keep
            for _ in range(lines_to_remove):
                if not cursor.movePosition(cursor.MoveOperation.Down):
                    break
            
            # Select from start to current position and remove
            cursor.movePosition(cursor.MoveOperation.Start, cursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            self._line_count = self.max_lines
        
        # Update statistics
        self.stats_label.setText(f"Emissions: {self._total_emissions} | Lines: {self._line_count}")
    
    def _flush_duplicate(self):
        """Flush the last line with duplicate count if applicable."""
        if self._last_line is None:
            return
        
        # Format the line with duplicate count if needed
        if self._duplicate_count > 0:
            display_line = f"{self._last_line} (+{self._duplicate_count})"
        else:
            display_line = self._last_line
        
        # Add to display
        self.text_display.append(display_line)
        self._line_count += 1
        
        # Reset tracking
        self._last_line = None
        self._duplicate_count = 0
    
    def _on_pause_toggled(self, checked: bool):
        """Handle pause button toggle."""
        self._is_paused = checked
        self.pause_button.setText("Resume" if checked else "Pause")
    
    def _on_clear(self):
        """Clear the display."""
        # Flush any pending duplicate before clearing
        self._flush_duplicate()
        self.text_display.clear()
        self._line_count = 0
        self._last_line = None
        self._duplicate_count = 0
        with self._queue_lock:
            self._emission_queue.clear()
        self.stats_label.setText("Emissions: 0 | Lines: 0")
    
    def _on_filter_changed(self, text: str):
        """Handle filter text change."""
        # Filter is applied in _process_queue, no action needed here
        pass
    
    def _on_max_lines_changed(self, value: int):
        """Handle max lines change."""
        self.max_lines = value
        # Trim if necessary
        if self._line_count > self.max_lines:
            doc = self.text_display.document()
            cursor = self.text_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            
            lines_to_remove = self._line_count - self.max_lines
            for _ in range(lines_to_remove):
                if not cursor.movePosition(cursor.MoveOperation.Down):
                    break
            
            cursor.movePosition(cursor.MoveOperation.Start, cursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            self._line_count = self.max_lines
            self.stats_label.setText(f"Emissions: {self._total_emissions} | Lines: {self._line_count}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self._update_timer.stop()
        event.accept()


def create_snooper_with_widget(target_object: QtCore.QObject, 
                               include_children: bool = True,
                               signal_name_filter: Optional[List[str]] = None,
                               widget_max_lines: int = 1000,
                               widget_update_interval_ms: int = 100,
                               parent_widget: Optional[QWidget] = None) -> tuple:
    """
    Convenience function to create a SignalSnooper with an attached widget window.
    
    Args:
        target_object: QObject to monitor
        include_children: If True, monitor child widgets recursively
        signal_name_filter: Optional list of signal names to monitor
        widget_max_lines: Maximum lines in the widget display
        widget_update_interval_ms: Update interval for the widget (milliseconds)
        parent_widget: Parent widget for the monitor window (optional)
    
    Returns:
        Tuple of (SignalSnooper instance, SignalSnooperWidget instance)
    
    Example:
        snooper, widget = create_snooper_with_widget(my_widget)
        widget.show()  # Show the monitoring window
        snooper.start()  # Start monitoring
    """
    # Create widget
    widget = SignalSnooperWidget(parent=parent_widget, 
                                  max_lines=widget_max_lines,
                                  update_interval_ms=widget_update_interval_ms)
    
    # Create callback that adds to widget
    def widget_callback(signal_name, emitting_object, args, kwargs, timestamp):
        widget.add_emission(signal_name, emitting_object, args, kwargs, timestamp)
    
    # Create snooper with widget callback
    snooper = SignalSnooper(
        target_object=target_object,
        callback=widget_callback,
        include_children=include_children,
        signal_name_filter=signal_name_filter
    )
    
    return snooper, widget

