from copy import deepcopy
from typing import Optional, List, Dict, Callable
from attrs import define, field, Factory


@define
class ParamToPyQtBinding:
    """ The `param` library allows automatically generating Panel GUIs from Parameterized classes. 
    This class aims to help provide similar automatic generation/bindings for PyQt5 widgets
    
    Usage:
    
    from pyphocorehelpers.gui.Qt.Param_to_PyQt_Binding import ParamToPyQtBinding
    
    """
    get_value: Callable = field()
    set_value: Callable = field()
    on_changed: Optional[Callable] = field(default=None)
     

    @classmethod
    def param_to_pyqt_binding_dict(cls) -> Dict[str, "ParamToPyQtBinding"]:
        return {
            "QToolButton":ParamToPyQtBinding(get_value=(lambda ctrl: ctrl.isChecked()), set_value=(lambda ctrl, value: ctrl.setChecked(value)), on_changed=(lambda ctrl: ctrl.toggled)), # check control
            # QtWidgets.QToolButton:ParamToPyQtBinding(get_value=(lambda ctrl: ctrl.text), set_value=(lambda ctrl, value: ctrl.setText(value))),
            "QPushButton":ParamToPyQtBinding(get_value=(lambda ctrl: ctrl.text()), set_value=(lambda ctrl, value: ctrl.setText(value))),
            "ColorButton":ParamToPyQtBinding(get_value=(lambda ctrl: ctrl.color()), set_value=(lambda ctrl, value: ctrl.setColor(value, finished=True)), on_changed=(lambda ctrl: ctrl.sigColorChanging)),
            "QDoubleSpinBox":ParamToPyQtBinding(get_value=(lambda ctrl: ctrl.value()), set_value=(lambda ctrl, value: ctrl.setProperty("value", value)), on_changed=(lambda ctrl: ctrl.valueChanged)), # setValue
        }