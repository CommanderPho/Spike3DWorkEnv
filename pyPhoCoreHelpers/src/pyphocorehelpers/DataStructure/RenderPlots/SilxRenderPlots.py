from typing import Dict
from pyphocorehelpers.DataStructure.general_parameter_containers import RenderPlots, RenderPlotsData, VisualizationParameters
from pyphocorehelpers.gui.PhoUIContainer import PhoUIContainer
from pyphocorehelpers.DataStructure.dynamic_parameters import DynamicParameters

from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes


class SilxRenderPlots(RenderPlots):
	"""Container for holding and accessing Silx-based figures for SilxRenderPlots.

	from pyphocorehelpers.DataStructure.RenderPlots.SilxRenderPlots import SilxRenderPlots

	"""
	_display_library:str = 'silx'
	
	def __init__(self, name='SilxRenderPlots', app=None, parent_root_widget=None, display_outputs=DynamicParameters(), context=None, **kwargs):
		super(SilxRenderPlots, self).__init__(name, app=app, parent_root_widget=parent_root_widget, display_outputs=display_outputs, context=context, **kwargs)
		




