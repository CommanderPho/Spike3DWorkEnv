from IPython.display import display
from IPython import get_ipython
from PyQt5.QtWidgets import QSizePolicy, QWidget, QApplication
from PyQt5.QtCore import QSize, QObject, QPoint, QRect
import traceback

""" 
pyqt_ipython_rendering_helpers.py

"""

helper_types_list = ['text/plain', 'text/html']


class PyQtFormatters:
    """Class for managing PyQt5 object formatters in IPython/Jupyter environments.
    
    Example usage:
        from pyphocorehelpers.pyqt_ipython_rendering_helpers import PyQtFormatters
        
        # Create an instance and register formatters
        formatters = PyQtFormatters()
        formatters.register()
        
        # Later, if needed, unregister formatters
        formatters.unregister()
    """
    
    def __init__(self):
        """Initialize the formatter class."""
        self.ip = get_ipython()
        self.registered_types = {'text/plain': [], 'text/html': []}
        
    def register(self):
        """Register formatters for PyQt5 objects to get better representation in IPython/Jupyter."""
        if self.ip is None:
            print("Not running in IPython environment")
            return
        
        text_formatter = self.ip.display_formatter.formatters['text/plain']
        html_formatter = self.ip.display_formatter.formatters['text/html']

        # for a_helper_type in [text_formatter, html_formatter]:
        for a_helper_type_str, a_helper_formatter in zip(helper_types_list, [text_formatter, html_formatter]):
            
            # Register the formatters (wrap them in safe_format for extra protection)
            a_helper_formatter.for_type(QSizePolicy, self._helper_safe_format(self.format_size_policy))
            self.registered_types[a_helper_type_str].append(QSizePolicy)
            
            # Uncomment to register additional formatters
            # a_helper_formatter.for_type(QSize, self._helper_safe_format(self.format_qsize))
            # self.registered_types[a_helper_type_str].append(QSize)
            a_helper_formatter.for_type(QPoint, self._helper_safe_format(self.format_qpoint))
            self.registered_types[a_helper_type_str].append(QPoint)
            a_helper_formatter.for_type(QRect, self._helper_safe_format(self.format_qrect))
            self.registered_types[a_helper_type_str].append(QRect)
            # a_helper_formatter.for_type(QWidget, self._helper_safe_format(self.format_qwidget))
            # self.registered_types[a_helper_type_str].append(QWidget)
            # a_helper_formatter.for_type(QObject, self._helper_safe_format(self.format_qobject))
            # self.registered_types[a_helper_type_str].append(QObject)       
             
        print("PyQt5 formatters registered successfully")
    
    def unregister(self):
        """Unregister the PyQt5 formatters and restore default formatting."""
        if self.ip is None:
            print("Not running in IPython environment")
            return
        
        # text_formatter = self.ip.display_formatter.formatters['text/plain']
        for a_helper_type_str, registered_formatter_types_list in self.registered_types.items():
            print(f'removing {len(registered_formatter_types_list)} registered formatters for a_helper_type_str: "{a_helper_type_str}"...')
            a_formatter = self.ip.display_formatter.formatters[a_helper_type_str]
            # Remove the formatters for each registered type
            for qt_type in registered_formatter_types_list:
                if qt_type in a_formatter.type_printers:
                    del a_formatter.type_printers[qt_type]
        
        print(f'done.')
        self.registered_types = {'text/plain': [], 'text/html': []} ## start fresh again
        print("PyQt5 formatters unregistered successfully")


    def _helper_safe_format(self, format_fn):
        """Wrapper to make any formatter function safe.
        
        Args:
            format_fn: The formatting function to wrap
            
        Returns:
            A safe version of the formatter function that handles cycles and exceptions
            
        Usage:
            a_size_policy_formatter_fn = qt_formatters._helper_safe_format(qt_formatters.format_size_policy)
            
        """
        def safe_formatter(obj, p=None, cycle=False):
            try:
                if cycle:
                    return p.text('...')
                else:
                    return format_fn(obj, p)
            except Exception as e:
                return f"<Error formatting {type(obj).__name__}: {str(e)}>"
        return safe_formatter
    
    def format_size_policy(self, obj, p):
        """Format a QSizePolicy with relevant information.
        
        Args:
            obj: QSizePolicy object
            p: IPython printer
            
        Returns:
            Formatted string representation
        """
        general_policies = {QSizePolicy.Fixed: "Fixed", QSizePolicy.Minimum: "Minimum",
                    QSizePolicy.Maximum: "Maximum", QSizePolicy.Preferred: "Preferred",
                    QSizePolicy.Expanding: "Expanding", QSizePolicy.MinimumExpanding: "MinimumExpanding",
                    QSizePolicy.Ignored: "Ignored"}
    
        try:
            h_policy_idx = obj.horizontalPolicy()
            v_policy_idx = obj.verticalPolicy()
            
            h_policy = general_policies.get(h_policy_idx, f"Unknown({h_policy_idx})")
            v_policy = general_policies.get(v_policy_idx, f"Unknown({v_policy_idx})")
                                    
            return f"QSizePolicy(horizontal={h_policy}, vertical={v_policy}, " \
                   f"h_stretch={obj.horizontalStretch()}, v_stretch={obj.verticalStretch()})"
        except:
            print(f'WARNING[format_size_policy]: QSizePolicy({traceback.format_exc().splitlines()[-1]})')
            return str(obj)
    
    def format_qsize(self, obj, p):
        """Format a QSize with width and height.
        
        Args:
            obj: QSize object
            p: IPython printer
            
        Returns:
            Formatted string representation
        """
        try:
            width = obj.width()
            height = obj.height()
            return f"QSize({width}×{height})"
        except:
            return f"QSize({traceback.format_exc().splitlines()[-1]})"
    
    def format_qpoint(self, obj, p):
        """Format a QPoint with x and y coordinates.
        
        Args:
            obj: QPoint object
            p: IPython printer
            
        Returns:
            Formatted string representation
        """
        try:
            return f"QPoint({obj.x()},{obj.y()})"
        except:
            return f"QPoint({traceback.format_exc().splitlines()[-1]})"
    
    def format_qrect(self, rect, p, prefix_string='rect: ', indent_string = '\t', include_edge_positions=False):
        """Format a QRect with position and size.
        From pyphoplacecellanalysis.General.Mixins.DisplayHelpers.debug_print_QRect 2025-04-04 06:24 
        Args:
            obj: QRect object
            p: IPython printer
            
        Returns:
            Formatted string representation
        """
        try:
            # return f"QRect({obj.x()},{obj.y()},{obj.width()}×{obj.height()})"
            if include_edge_positions: 
                return '\n'.join([f'{indent_string}{prefix_string}QRectF(x: {rect.x()}, y: {rect.y()}, width: {rect.width()}, height: {rect.height()})', f'{indent_string}{indent_string}left: {rect.left()}\t right: {rect.right()}', f'{indent_string}{indent_string}top: {rect.top()}\t bottom: {rect.bottom()}'])
            else:
                return f'{indent_string}{prefix_string}QRectF(x: {rect.x()}, y: {rect.y()}, width: {rect.width()}, height: {rect.height()})' # Concise       

        except:
            return f"QRect({traceback.format_exc().splitlines()[-1]})"
    
    def format_qwidget(self, obj, p):
        """Format a QWidget with limited information to avoid side effects.
        
        Args:
            obj: QWidget object
            p: IPython printer
            
        Returns:
            Formatted string representation
        """
        try:
            if obj.__class__ == QWidget:
                class_name = obj.__class__.__name__
                size_info = f"{obj.width()}×{obj.height()}" if obj.isVisible() else "hidden"
                object_name = obj.objectName()
                name_info = f", name='{object_name}'" if object_name else ""
                return f"{class_name}(size={size_info}{name_info})"
            else:
                return p.text(repr(obj))
        except:
            return f"{type(obj).__name__}({traceback.format_exc().splitlines()[-1]})"
    
    def format_qobject(self, obj, p):
        """Format a generic QObject as fallback.
        
        Args:
            obj: QObject object
            p: IPython printer
            
        Returns:
            Formatted string representation
        """
        try:
            if obj.__class__ == QObject:
                class_name = obj.__class__.__name__
                object_name = obj.objectName()
                name_info = f", name='{object_name}'" if object_name else ""
                return f"{class_name}(id={hex(id(obj))[-6:]}{name_info})"
            else:
                return p.text(repr(obj))
        except:
            return f"{type(obj).__name__}({traceback.format_exc().splitlines()[-1]})"


# For backward compatibility with existing code
def register_qt_formatters():
    """Register robust formatters for PyQt5 objects (legacy function).
    
    This function is maintained for backward compatibility.
    For new code, use PyQtFormatters class directly.
    """
    formatters = PyQtFormatters()
    formatters.register()
    return formatters

def unregister_qt_formatters():
    """Unregister the PyQt5 formatters (legacy function).
    
    This function is maintained for backward compatibility.
    For new code, use PyQtFormatters class directly.
    """
    formatters = PyQtFormatters()
    formatters.unregister()
