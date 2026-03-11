from typing import Dict
from pyphocorehelpers.DataStructure.general_parameter_containers import RenderPlots, RenderPlotsData, VisualizationParameters
from pyphocorehelpers.gui.PhoUIContainer import PhoUIContainer
from pyphocorehelpers.DataStructure.dynamic_parameters import DynamicParameters

from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes


class PyqtgraphRenderPlots(RenderPlots):
	"""Container for holding and accessing Pyqtgraph-based figures for PyqtgraphRenderPlots.

	from pyphocorehelpers.DataStructure.RenderPlots.PyqtgraphRenderPlots import PyqtgraphRenderPlots

	"""
	_display_library:str = 'pyqtgraph'
	
	def __init__(self, name='PyqtgraphRenderPlots', app=None, parent_root_widget=None, display_outputs=DynamicParameters(), context=None, **kwargs):
		super(PyqtgraphRenderPlots, self).__init__(name, app=app, parent_root_widget=parent_root_widget, display_outputs=display_outputs, context=context, **kwargs)
		




