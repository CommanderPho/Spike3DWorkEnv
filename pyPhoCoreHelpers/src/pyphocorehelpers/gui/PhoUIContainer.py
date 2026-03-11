from pyphocorehelpers.print_helpers import SimplePrintable, PrettyPrintable, iPythonKeyCompletingMixin
from pyphocorehelpers.DataStructure.dynamic_parameters import DynamicParameters

class PhoUIContainer(iPythonKeyCompletingMixin, DynamicParameters):
    """A simple extensable container that allows setting properties dynamically to hold UI elements or other important data."""
    def __init__(self, name='PhoUIContainer', **kwargs) -> None:
        super(PhoUIContainer, self).__init__(name=name, **kwargs)
    
