    
from pyphocorehelpers.general_helpers import OrderedMeta
from pyphocorehelpers.print_helpers import SimplePrintable, PrettyPrintable, iPythonKeyCompletingMixin

from pyphocorehelpers.DataStructure.dynamic_parameters import DynamicParameters

class ConnectionsContainer(iPythonKeyCompletingMixin, DynamicParameters):
    """ holds references to connections and allows batch disconnection for specific signals """
    def __init__(self, **kwargs) -> None:
        super(ConnectionsContainer, self).__init__(**kwargs)
    
    def append(self, connection):
     raise NotImplementedError
 