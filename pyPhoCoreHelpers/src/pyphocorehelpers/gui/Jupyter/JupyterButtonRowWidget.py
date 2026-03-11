from attrs import define, field, Factory, astuple, asdict
from typing import Optional, List, Dict
import ipywidgets as widgets
from IPython.display import display



def build_fn_bound_buttons(button_defns, **default_kwargs):
	""" much simplier version of `JupyterButtonRowWidget` """
	# default_kwargs = dict(display='flex', flex_flow='column', align_items='stretch', layout=btn_layout)
	# button_list = []
	button_dict = {}
	for (a_label, a_fn, *args) in button_defns:
		if len(args) > 0:
			button_kwargs = args[0]
			# print(f'using provided button_kwargs: {button_kwargs}')
		else:
			button_kwargs = default_kwargs
			
		a_btn = widgets.Button(description=a_label, **button_kwargs) # , style= {'width': 'initial'}
		a_btn.on_click(a_fn)
		# button_list.append(a_btn)
		button_dict[a_label] = a_btn
	# return button_list
	return button_dict
		
		
@define(slots=False)
class JupyterButtonContainerWidget:
	""" Displays a clickable row of buttons in the Jupyter Notebook that perform any function 
	
	Usage:
		from pyphocorehelpers.gui.Jupyter.JupyterButtonRowWidget import JupyterButtonRowWidget
		from pyphocorehelpers.Filesystem.open_in_system_file_manager import reveal_in_system_file_manager

		# Define the set of buttons:
		button_defns = [("Output Folder", lambda _: reveal_in_system_file_manager(curr_active_pipeline.get_output_path())),
				("global pickle", lambda _: reveal_in_system_file_manager(curr_active_pipeline.global_computation_results_pickle_path)),
				("pipeline pickle", lambda _: reveal_in_system_file_manager(curr_active_pipeline.pickle_path)),
				(".h5 export", lambda _: reveal_in_system_file_manager(curr_active_pipeline.h5_export_path)),
				("ViTables .h5 export", lambda _: reveal_in_system_file_manager(curr_active_pipeline.h5_export_path))
			]

		# Create and display the button
		button_executor = JupyterButtonRowWidget(button_defns=button_defns)

	
	"""
	button_dict: Dict = field(default=Factory(dict))
	root_widget: Optional[widgets.HBox] = field(default=None)

	@property
	def button_list(self) -> List:
		return list(self.button_dict.values())


	@classmethod
	def init_from_button_defns(cls, button_defns, defer_display:bool=True) -> "JupyterButtonContainerWidget":
		## Build the widget:
		_obj = cls()
		_obj.build_widget(button_defns)
		# Display if needed
		if not defer_display:
			_obj.display_buttons()
		return _obj
	

	def build_widget(self, button_defns):
		## builds the buttons from the definitions:
		self.button_dict = build_fn_bound_buttons(button_defns)
		raise NotImplementedError
		# self.root_widget = widgets.HBox(self.button_list)
		

	def display_buttons(self):
		assert self.root_widget is not None
		display(self.root_widget)



@define(slots=False)
class JupyterButtonRowWidget(JupyterButtonContainerWidget):
	""" Displays a clickable row of buttons in the Jupyter Notebook that perform any function 
	
	Usage:
		from pyphocorehelpers.gui.Jupyter.JupyterButtonRowWidget import JupyterButtonRowWidget
		from pyphocorehelpers.Filesystem.open_in_system_file_manager import reveal_in_system_file_manager

		# Define the set of buttons:
		button_defns = [("Output Folder", lambda _: reveal_in_system_file_manager(curr_active_pipeline.get_output_path())),
				("global pickle", lambda _: reveal_in_system_file_manager(curr_active_pipeline.global_computation_results_pickle_path)),
				("pipeline pickle", lambda _: reveal_in_system_file_manager(curr_active_pipeline.pickle_path)),
				(".h5 export", lambda _: reveal_in_system_file_manager(curr_active_pipeline.h5_export_path)),
				("ViTables .h5 export", lambda _: reveal_in_system_file_manager(curr_active_pipeline.h5_export_path))
			]

		# Create and display the button
		button_executor = JupyterButtonRowWidget(button_defns=button_defns)

	
	"""
	# button_dict: Dict = field(default=Factory(dict))
	root_widget: Optional[widgets.HBox] = field(default=None)

	def build_widget(self, button_defns):
		## builds the buttons from the definitions:
		self.button_dict = build_fn_bound_buttons(button_defns)
		self.root_widget = widgets.HBox(self.button_list)
		





@define(slots=False)
class JupyterButtonColumnWidget(JupyterButtonContainerWidget):
	""" Displays a clickable column of buttons in the Jupyter Notebook that perform any function 
	
	Usage:
		from pyphocorehelpers.gui.Jupyter.JupyterButtonRowWidget import JupyterButtonRowWidget
		from pyphocorehelpers.Filesystem.open_in_system_file_manager import reveal_in_system_file_manager

		# Define the set of buttons:
		button_defns = [("Output Folder", lambda _: reveal_in_system_file_manager(curr_active_pipeline.get_output_path())),
				("global pickle", lambda _: reveal_in_system_file_manager(curr_active_pipeline.global_computation_results_pickle_path)),
				("pipeline pickle", lambda _: reveal_in_system_file_manager(curr_active_pipeline.pickle_path)),
				(".h5 export", lambda _: reveal_in_system_file_manager(curr_active_pipeline.h5_export_path)),
				("ViTables .h5 export", lambda _: reveal_in_system_file_manager(curr_active_pipeline.h5_export_path))
			]

		# Create and display the button
		button_executor = JupyterButtonRowWidget(button_defns=button_defns)

	
	"""
	# button_dict: Dict = field(default=Factory(dict))
	root_widget: Optional[widgets.VBox] = field(default=None)

	def build_widget(self, button_defns):
		## builds the buttons from the definitions:
		self.button_dict = build_fn_bound_buttons(button_defns)
		self.root_widget = widgets.VBox(self.button_list)
		




