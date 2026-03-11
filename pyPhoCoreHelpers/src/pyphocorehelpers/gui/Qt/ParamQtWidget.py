from qtpy import QtCore, QtWidgets
import param

# @metadata_attributes(short_name=None, tags=['param', 'config', 'pyqt', 'widget', 'mapping', 'working', 'useful'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-12-09 17:55', related_items=['ParamToPyQtBinding'])
class ParamQtWidget(QtWidgets.QWidget):
    """A QWidget that automatically creates Qt-based controls for a param.Parameterized object
    while managing sync
    
    Historical: I created this fresh, but there's already a `ParamToPyQtBinding` that I'm not sure how well it works


    Usage:
    
        from pyphocorehelpers.gui.Qt.ParamQtWidget import ParamQtWidget, ParamQtWidgetMappingMixin
        from pyphoplacecellanalysis.General.Model.Configs.ParamConfigs import BasePlotDataParams, ExtendedPlotDataParams

        a_widget: ParamQtWidget = ParamQtWidget(a_layer.gui_params)
        a_widget.show()

    """
    
    def __init__(self, param_obj, parent=None):
        super().__init__(parent)
        self.param_obj = param_obj
        self._watcher = None # Keep a reference to the watcher
        self.setup_ui()
        self.setup_bindings()
    
    def setup_ui(self):
        # QFormLayout is more efficient for Label-Widget pairs
        layout = QtWidgets.QFormLayout(self)
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        for param_name in self.param_obj.param.objects():
            if param_name == 'name': continue # Skip internal name param
            
            p_obj = self.param_obj.param[param_name]
            p_value = getattr(self.param_obj, param_name)
            
            # Create appropriate widget
            widget = None
            
            if isinstance(p_obj, param.Boolean):
                widget = QtWidgets.QCheckBox()
                widget.setChecked(p_value)
                widget.toggled.connect(lambda v, p=param_name: setattr(self.param_obj, p, v))
            
            elif isinstance(p_obj, param.Integer):
                widget = QtWidgets.QSpinBox()
                # Handle bounds if they exist
                if p_obj.bounds:
                    # Qt uses 0/99 by default, need to open it up if no bounds
                    min_val = p_obj.bounds[0] if p_obj.bounds[0] is not None else -2147483648
                    max_val = p_obj.bounds[1] if p_obj.bounds[1] is not None else 2147483647
                    widget.setRange(min_val, max_val)
                else:
                    widget.setRange(-2147483648, 2147483647)
                widget.setValue(p_value)
                widget.valueChanged.connect(lambda v, p=param_name: setattr(self.param_obj, p, v))

            elif isinstance(p_obj, param.Number):
                widget = QtWidgets.QDoubleSpinBox()
                if p_obj.bounds:
                    min_val = p_obj.bounds[0] if p_obj.bounds[0] is not None else -float('inf')
                    max_val = p_obj.bounds[1] if p_obj.bounds[1] is not None else float('inf')
                    # QDoubleSpinBox doesn't support inf directly, use large numbers
                    widget.setRange(max(-1e9, min_val), min(1e9, max_val))
                else:
                    widget.setRange(-1e9, 1e9)
                
                widget.setDecimals(6)
                widget.setSingleStep(getattr(p_obj, 'step', 0.1) or 0.1)
                widget.setValue(p_value)
                widget.valueChanged.connect(lambda v, p=param_name: setattr(self.param_obj, p, v))
            
            elif isinstance(p_obj, param.Selector):
                widget = QtWidgets.QComboBox()
                objects = p_obj.objects if p_obj.objects else []
                # Handle dict or list selectors
                items = list(objects.keys()) if isinstance(objects, dict) else objects
                widget.addItems([str(i) for i in items])
                widget.setCurrentText(str(p_value))
                widget.currentTextChanged.connect(lambda v, p=param_name: setattr(self.param_obj, p, v))

            elif isinstance(p_obj, param.String):
                widget = QtWidgets.QLineEdit()
                widget.setText(str(p_value))
                widget.textChanged.connect(lambda v, p=param_name: setattr(self.param_obj, p, v))
            
            else:
                widget = QtWidgets.QLabel(str(p_value))

            # CRITICAL: Set object name so findChild can work in the watcher
            widget.setObjectName(param_name)
            
            # Add to Form Layout
            layout.addRow(param_name.replace("_", " ").title() + ":", widget)


    def setup_bindings(self):
        """Set up param watchers with safety checks"""
        
        def update_ui(event):
            # SAFETY CHECK 1: Catch the RuntimeError if C++ object is already gone
            try:
                # This access will throw RuntimeError if self is deleted
                widget = self.findChild(QtWidgets.QWidget, event.name)
            except RuntimeError:
                # The widget is dead, we shouldn't be here, but we can exit gracefully
                return

            if not widget:
                return

            blocker = QtCore.QSignalBlocker(widget)
            try:
                if isinstance(widget, QtWidgets.QCheckBox):
                    widget.setChecked(event.new)
                elif isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
                    widget.setValue(event.new)
                elif isinstance(widget, QtWidgets.QLineEdit):
                    widget.setText(str(event.new))
                elif isinstance(widget, QtWidgets.QComboBox):
                    widget.setCurrentText(str(event.new))
                elif isinstance(widget, QtWidgets.QLabel):
                    widget.setText(str(event.new))
            finally:
                del blocker

        # 1. Store the watcher object
        self._watcher = self.param_obj.param.watch(update_ui, list(self.param_obj.param.params().keys()))
        
        # 2. Connect to the destroyed signal to clean up
        self.destroyed.connect(self._on_destroyed)
        

    def _on_destroyed(self):
        """Unregister the watcher when the Qt Widget is destroyed"""
        if self._watcher:
            try:
                self.param_obj.param.unwatch(self._watcher)
            except Exception:
                # Param object might be gone too, or watcher already removed
                pass
            self._watcher = None
            


class ParamQtWidgetMappingMixin:
    """ implementors build their own control QtWidgets

    """
    
    def get_gui_widget(self) -> QtWidgets.QWidget:
        """Returns a QWidget with controls for a `BasePlotDataParams` subclass 
        """
        return ParamQtWidget(self)



# # Usage in your class:
# def get_gui_widget(self) -> QtWidgets.QWidget:
#     """Returns a QWidget with controls for gui_params"""
#     return ParamQtWidget(self.gui_params)


# a_widget = a_layer.create_panel_widget()
