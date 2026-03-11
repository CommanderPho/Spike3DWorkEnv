#TODO 2023-06-20 12:16: - [ ] Convert to `SubsettableDictRepresentable`
# from neuropy.utils.mixins.dict_representable import SubsettableDictRepresentable
from typing import List, Dict, Optional
from pyphocorehelpers.print_helpers import iPythonKeyCompletingMixin
from pyphocorehelpers.DataStructure.dynamic_parameters import DynamicParameters

class VisualizationParameters(iPythonKeyCompletingMixin, DynamicParameters):
    def __init__(self, name, **kwargs) -> None:
        super(VisualizationParameters, self).__init__(name=name, **kwargs)
    

class DebugHelper(iPythonKeyCompletingMixin, DynamicParameters):
    def __init__(self, name, **kwargs) -> None:
        super(DebugHelper, self).__init__(name=name, **kwargs)


#TODO 2023-06-13 10:59: - [ ] Convert to an attrs-based class instead of inheriting from DynamicParameters
# @attrs.define(slots=False)
class RenderPlots(iPythonKeyCompletingMixin, DynamicParameters):
    """
    from pyphocorehelpers.DataStructure.general_parameter_containers import RenderPlots

    Also see `pyphoplacecellanalysis.GUI.PyQtPlot.Widgets.ContainerBased.PhoContainerTool.PhoBaseContainerTool` for higher-level usage
    
    """
    _display_library:str = 'unknown'
    def __init__(self, name, context=None, **kwargs) -> None:
        super(RenderPlots, self).__init__(name=name, context=context, **kwargs)

    @classmethod
    def get_non_data_keys(cls) -> List[str]:
        """ a list of the non-user-contributed keys. """
        return ['name', 'context'] # , '_display_library'

    @property
    def data_keys(self):
        """The data_keys property."""
        return [k for k in self.keys() if k not in self.get_non_data_keys()]


    def data_items(self):
        return {k:v for k, v in self.items() if k in self.data_keys}.items()



    # Display Library Test Functions _____________________________________________________________________________________ #
    @classmethod
    def is_matplotlib(cls):
        """Whether the display library is matplotlib."""
        return cls._display_library == 'matplotlib'
    @classmethod
    def is_pyqtgraph(cls):
        """Whether the display library is pyqtgraph."""
        return cls._display_library == 'pyqtgraph'
    @classmethod
    def is_silx(cls):
        """Whether the display library is silx."""
        return cls._display_library == 'silx'
    

    # def __add__(self, other):
    #     # Combine figures and axes from self and other MatplotlibRenderPlots instances
    #     # combined_figures = self.figures + other.figures
    #     # combined_axes = self.axes + other.axes

    #     for k, v in other.data_items().items():
    #         if k not in self.data_keys:
    #             # unique to other, add it as a property to self
    #             self[k] = v 
    #         else:
    #             # present in both
    #             self[k] = self[k] + v  ## append or w/e

    #     return self ## return the updated self
    

    # def __add__(self, other):
    #     if not isinstance(other, CustomDict):
    #         raise TypeError("Unsupported operand type. The operand must be of type CustomDict.")
    #     combined_data = {key: self.data.get(key, 0) + other.data.get(key, 0) for key in set(self.data) | set(other.data)}
    #     return CustomDict(combined_data)


class RenderPlotsData(iPythonKeyCompletingMixin, DynamicParameters):
    """
    from pyphocorehelpers.DataStructure.general_parameter_containers import RenderPlotsData
    
    
    """
    def __init__(self, name, **kwargs) -> None:
        super(RenderPlotsData, self).__init__(name=name, **kwargs)


    @classmethod
    def get_non_data_keys(cls) -> List[str]:
        """ a list of the non-user-contributed keys. """
        return ['name', 'context'] # , '_display_library'

    @property
    def data_keys(self):
        """The data_keys property."""
        return [k for k in self.keys() if k not in self.get_non_data_keys()]


    def data_items(self):
        return {k:v for k, v in self.items() if k in self.data_keys}.items()

