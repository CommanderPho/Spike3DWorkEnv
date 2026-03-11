from copy import deepcopy
import os
import pandas as pd
from typing import Callable, Optional, List, Dict, Union, Any
import ipywidgets as widgets
from ipywidgets import HBox, VBox
from IPython.display import display, HTML, Javascript
from pathlib import Path


def render_colors(color_input):
    """ Renders a simple list of colors for visual previewing
    Usage:
    
        from pyphocorehelpers.gui.Jupyter.simple_widgets import render_colors

        render_colors(color_list)

    Advanced Usage:
    
        # Define the list of colors you want to display
        # color_list = ['red', 'blue', 'green', '#FFA500', '#800080']
        color_list = _plot_backup_colors.neuron_colors_hex

        # Create a button to trigger the color rendering
        button = widgets.Button(description="Show Colors")

        # Define what happens when the button is clicked
        def on_button_click(b):
            render_colors(color_list)

        button.on_click(on_button_click)

        # Display the button
        button
        
    """
    from qtpy.QtGui import QColor, QBrush, QPen

    # color_html = ''.join([f'<div style="width:50px; height:50px; background-color:{color}; margin:5px; display:inline-block;"></div>' for color in color_list])

    # Check if input is a dictionary
    if isinstance(color_input, dict):
        color_items = color_input.items()
    else:
        # Ensure color_input is a list, even if a single color is provided
        if not isinstance(color_input, (list, tuple)):
            color_input = [color_input]
        # Create a list of (label, color) where label is None for lists
        color_items = [(None, color) for color in color_input]

    # Convert colors to hex format if they are QColor objects and prepare HTML
    color_html = ''
    for label, color in color_items:
        if isinstance(color, QColor):
            hex_color = color.name()
        elif isinstance(color, str):
            hex_color = color if color.startswith('#') else f'#{color.lstrip("#")}'
        else:
            raise ValueError("Color must be a QColor, a hex string, or a valid CSS color name.")
        
        if label:
            color_html += f'<div style="display:inline-block; text-align:center; margin:5px;"><div style="width:50px; height:50px; background-color:{hex_color}; margin:5px;"></div><div>{label}</div></div>'
        else:
            color_html += f'<div style="width:50px; height:50px; background-color:{hex_color}; margin:5px; display:inline-block;"></div>'



    display(HTML(color_html))




# ==================================================================================================================== #
# Filesystem Paths                                                                                                     #
# ==================================================================================================================== #

def fullwidth_path_widget(a_path, file_name_label: str="session path:", box_layout_kwargs=None):
    """ displays a simple file path and a reveal button that shows it. 
     
     from pyphocorehelpers.gui.Jupyter.simple_widgets import fullwidth_path_widget
     
    """
    from pyphocorehelpers.Filesystem.path_helpers import open_file_with_system_default
    from pyphocorehelpers.Filesystem.open_in_system_file_manager import reveal_in_system_file_manager
    from pyphocorehelpers.programming_helpers import copy_to_clipboard

    box_layout_kwargs = box_layout_kwargs or {} # empty
    
    has_valid_file = False
    resolved_path: Optional[Path] = None

    if a_path is None:
        a_path = "<None>"
    else:
        if not isinstance(a_path, str):
            a_path = str(a_path)       
        resolved_path = Path(a_path).resolve()             
        has_valid_file = resolved_path.exists()
        is_dir = resolved_path.is_dir()
    
    
    left_label = widgets.Label(file_name_label, layout=widgets.Layout(width='auto'))
    # right_label = widgets.Label(a_path, layout=widgets.Layout(width='auto', flex='1 1 auto', margin='2px'))
    # Change the style of 'right_label' to make it bolder and larger using HTML tags in the value
    right_label = widgets.HTML(
        value=f"<b style='font-size: smaller;'>{a_path}</b>",
        layout=widgets.Layout(width='auto', flex='1 1 auto', margin='2px')
    )


    button_layout = widgets.Layout(flex='0 1 auto', width='auto', min_width='80px', margin='1px') # The button_layout ensures that buttons don't grow and are only as wide as necessary.
    # right_label_layout = widgets.Layout(flex='1 1 auto', min_width='0px', width='auto') # We use the flex property in the right_label_layout to let the label grow and fill the space, but it can also shrink if needed (flex='1 1 auto'). We set a min_width so it doesn't get too small and width='auto' to let it size based on content
    
    actions_button_list = []
    copy_to_clipboard_button = widgets.Button(description='Copy', layout=button_layout, disabled=(not Path(a_path).resolve().exists()), button_style='info', tooltip='Copy to Clipboard', icon='clipboard') # , icon='folder-tree'
    copy_to_clipboard_button.on_click(lambda _: copy_to_clipboard(str(a_path)))
    actions_button_list.append(copy_to_clipboard_button)

    reveal_button = widgets.Button(description='Reveal', layout=button_layout, disabled=(not Path(a_path).resolve().exists()), button_style='info', tooltip='Reveal in System Explorer', icon='folder-open-o')
    reveal_button.on_click(lambda _: reveal_in_system_file_manager(a_path))
    actions_button_list.append(reveal_button)
    
    if has_valid_file:
        is_dir = resolved_path.is_dir()
        if not is_dir:
            # is_file:
            open_button = widgets.Button(description='Open', layout=button_layout, disabled=((not Path(a_path).resolve().exists()) or ((Path(a_path).resolve().is_dir()))), button_style='info', tooltip='Open with default app', icon='external-link-square')
            open_button.on_click(lambda _: open_file_with_system_default(a_path))
            actions_button_list.append(open_button)
        else:
            # is directory
            open_button = widgets.Button(description='Open', layout=button_layout, disabled=((not Path(a_path).resolve().exists()) or ((not Path(a_path).resolve().is_dir()))), button_style='info', tooltip='Open Contents in System Explorer', icon='external-link-square')
            open_button.on_click(lambda _: open_file_with_system_default(a_path))
            actions_button_list.append(open_button)                                            
    

    box_layout_kwargs = (box_layout_kwargs | dict(display='flex', flex_flow='row nowrap',
                                                #    align_items='stretch', width='70%',
                                                    align_items='center', # Vertically align items in the middle
                                                    justify_content='flex-start', # Align items to the start of the container
                                                    width='90%'                                                 
                                                   ))
    box_layout = widgets.Layout(**box_layout_kwargs)
    hbox = widgets.Box(children=[left_label, right_label, *actions_button_list], layout=box_layout)
    return hbox




def simple_path_display_widget(a_path: Union[Path, str]):
    """ Returns a simple clickable Path that works on Windows and for paths containing spaces.
    
    Call like:
        from pyphocorehelpers.gui.Jupyter.simple_widgets import simple_path_display_widget, _build_file_link_from_path
        simple_path_display_widget(r"C:/Users/pho/repos/Spike3DWorkEnv/Spike3D/EXTERNAL/Screenshots/ProgrammaticDisplayFunctionTesting/2024-01-17/kdiba/gor01/one/2006-6-08_14-26-15/plot_all_epoch_bins_marginal_predictions_Laps all_epoch_binned Marginals.png")
        
    NOTE: could use from pyphocorehelpers.Filesystem.path_helpers import file_uri_from_path
    
    """
    def _subfn_build_file_link_from_path(a_path: Union[Path, str]) -> str:
        # if not isinstance(a_path, str):
        #     a_path = str(a_path)
        if not isinstance(a_path, Path):
            a_path = Path(a_path).resolve() # we need a Path
        a_path_url_str: str = a_path.as_uri() # returns a string like "file:///C:/Users/pho/repos/Spike3DWorkEnv/Spike3D/EXTERNAL/Screenshots/ProgrammaticDisplayFunctionTesting/2024-01-17/kdiba/gor01/one/2006-6-08_14-26-15/plot_all_epoch_bins_marginal_predictions_Laps%20all_epoch_binned%20Marginals.png"
        return f'<a href="{a_path_url_str}" target="_blank">{a_path_url_str}</a>'
        # return f'<a href="file://{a_path_url_str}" target="_blank">{a_path_url_str}</a>'

    # BEGIN FUNCTION BODY ________________________________________________________________________________________________ #
    file_link: str = _subfn_build_file_link_from_path(a_path)
    return HTML(file_link)



def build_global_data_root_parent_path_selection_widget(all_paths: List[Path], on_user_update_path_selection: Callable):
    """ 
    from pyphocorehelpers.gui.Jupyter.simple_widgets import build_global_data_root_parent_path_selection_widget
    
    all_paths = [Path(r'/home/halechr/turbo/Data'), Path(r'W:\Data'), Path(r'/home/halechr/FastData'), Path(r'/media/MAX/Data'), Path(r'/Volumes/MoverNew/data')]
    global_data_root_parent_path = extant_paths[0]
    def on_user_update_path_selection(new_path: Path):
        global global_data_root_parent_path
        new_global_data_root_parent_path = new_path.resolve()
        global_data_root_parent_path = new_global_data_root_parent_path
        print(f'global_data_root_parent_path changed to {global_data_root_parent_path}')
        assert global_data_root_parent_path.exists(), f"global_data_root_parent_path: {global_data_root_parent_path} does not exist! Is the right computer's config commented out above?"
                
    global_data_root_parent_path_widget = build_global_data_root_parent_path_selection_widget(all_paths, on_user_update_path_selection)
    global_data_root_parent_path_widget
    
    """
    extant_paths = [a_path for a_path in all_paths if a_path.exists()]
    assert len(extant_paths) > 0, f"NO EXTANT PATHS FOUND AT ALL!"
    global_data_root_parent_path = extant_paths[0]        


    # widgets.ToggleButtons
    global_data_root_parent_path_widget = widgets.ToggleButtons(
                                            options=extant_paths,
                                            description='Data Root:',
                                            disabled=False,
                                            button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                            tooltip='global_data_root_parent_path',
                                            layout=widgets.Layout(width='auto'),
                                            style={"button_width": 'max-content'}, # "190px"
                                        #     icon='check'
                                        )

    def on_global_data_root_parent_path_selection_change(change):
        global global_data_root_parent_path
        new_global_data_root_parent_path = Path(str(change['new'])).resolve()
        global_data_root_parent_path = new_global_data_root_parent_path
        print(f'global_data_root_parent_path changed to {global_data_root_parent_path}')
        assert global_data_root_parent_path.exists(), f"global_data_root_parent_path: {global_data_root_parent_path} does not exist! Is the right computer's config commented out above?"
        on_user_update_path_selection(new_global_data_root_parent_path)
        

    global_data_root_parent_path_widget.observe(on_global_data_root_parent_path_selection_change, names='value')
    ## Call the user function with the first extant path:
    on_user_update_path_selection(extant_paths[0])

    return global_data_root_parent_path_widget




def build_dropdown_selection_widget(all_items: List[Path], on_user_update_item_selection: Callable):
    """ Builds a dropdown list that allows the user to select from a list of items, such as contexts.
        from pyphocorehelpers.gui.Jupyter.simple_widgets import build_dropdown_selection_widget

        active_slected_context = included_session_contexts[0]

        def selected_context_changed_callback(context_str, context_data):
            global active_slected_context
            print(f"You selected {context_str}:{context_data}")
            active_slected_context = context_data # update the selected context

        context_selection_dropdown = build_dropdown_selection_widget(included_session_contexts, on_user_update_item_selection=selected_context_changed_callback)
        context_selection_dropdown
    
    """
    item_list = all_items.copy()
    assert len(item_list) > 0, f"item_list is empty!"
    # global_data_selected_item = item_list[0]        

    def selected_context_changed_callback(change):
        # global global_data_selected_item
        selected_item = change['new']
        print(f"You selected {selected_item}")
        # Run your function or cell code here
        on_user_update_item_selection(str(selected_item), selected_item)


    # item_list = ['Item 1', 'Item 2', 'Item 3']
    # item_list = included_session_contexts.copy()
    # item_list = all_items.copy()
    context_selection_dropdown = widgets.Dropdown(options=item_list, description='Select Context:', layout=widgets.Layout(width='auto'))
    context_selection_dropdown.style = {'description_width': 'initial'} # Increase dropdown width with CSS
    context_selection_dropdown.observe(selected_context_changed_callback, 'value')

    ## Call the user function with the first extant path:
    on_user_update_item_selection(str(item_list[0]), item_list[0])
    
    return context_selection_dropdown


def code_block_widget(contents: str, label: str="Code:"):
    """
    Create a code block widget with a copy-to-clipboard button.
    
    Parameters:
    contents (str): The initial text/content to display in the code block.
    label (str): The label for the code block textarea.

    Usage:

        from pyphocorehelpers.gui.Jupyter.simple_widgets import code_block_widget

        # Create and display the code block widget
        slurm_code_block = code_block_widget(initial_code, label="Python Code:")
    
    """
    # Create the code block text area widget
    code_textarea = widgets.Textarea(
        value=contents,
        placeholder='Type code here',
        description=label,
        disabled=False,
        layout=widgets.Layout(width='100%', height='200px')  # Adjust the size as needed
    )
    
    # Create the copy-to-clipboard button
    copy_button = widgets.Button(
        description='Copy to Clipboard',
        button_style='success',  # Possible styles: 'success', 'info', 'warning', 'danger' or ''
        tooltip='Copy code to clipboard',
        layout={'width': '150px'}  # Adjust the width of the button as needed
    )
    
    # Create the execute in terminal button
    execute_button = widgets.Button(
        description='Execute in Terminal',
        button_style='primary',  # Possible styles: 'success', 'info', 'warning', 'danger' or ''
        tooltip='Execute code in terminal',
        layout={'width': '150px'}  # Adjust the width of the button as needed
    )
    
    # Function to perform the copy to clipboard action
    def on_copy_button_clicked(b):
        payload = f"navigator.clipboard.writeText(`{code_textarea.value}`)"
        js_command = f"eval({payload})"
        display(widgets.HTML(value=f'<img src onerror="{js_command}">'))
    
        # Function to execute code in terminal
    def on_execute_button_clicked(b):
        # Use IPython's system command
        display(Javascript(f'IPython.notebook.kernel.execute("!{code_textarea.value}")'))
        
    # Attach the function to the click event of the button
    copy_button.on_click(on_copy_button_clicked)
    execute_button.on_click(on_execute_button_clicked)
    
    # Use a horizontal box (HBox) to place the button next to the text area
    hbox = widgets.HBox([code_textarea, copy_button, execute_button])
    display(hbox)
    return hbox



def filesystem_path_folder_contents_widget(a_path: Union[Path, str], on_file_open=None):
    """ Returns a simple clickable Path that works on Windows and for paths containing spaces.
    
    Call like:
        from pyphocorehelpers.gui.Jupyter.simple_widgets import filesystem_path_folder_contents_widget

        curr_collected_outputs_folder = Path(output_path_dicts['neuron_replay_stats_table']['.csv']).resolve().parent        
        filesystem_path_folder_contents_widget(curr_collected_outputs_folder)
    
    """
    import solara # `pip install "solara[assets]`

    if not isinstance(a_path, Path):
        a_path = Path(a_path).resolve() # we need a Path
    assert a_path.exists(), f'a_path: "{a_path} does not exist!"'


    if on_file_open is None:
        on_file_open = print

    return widgets.VBox(
            children=[
                solara.FileBrowser.widget(directory=a_path, on_file_open=on_file_open)
            ]
        )



# @function_attributes(short_name=None, tags=['panel', 'widget', 'filesystem'], input_requires=[], output_provides=[], uses=['panel'], used_by=[], creation_date='2025-01-14 08:41', related_items=[])
def create_filtered_file_selector(directory, general_pattern, allowed_patterns):
    """
    Create a filtered FileSelector widget.

    Parameters:
        directory (str): The directory to search files.
        general_pattern (str): The general glob pattern to match files.
        allowed_patterns (list): List of specific glob patterns to filter the files.

    Returns:
        pn.widgets.FileSelector: A FileSelector widget with filtering applied.
    """
    import panel as pn
    
    pn.extension()
        
    # Create the FileSelector widget
    file_selector = pn.widgets.FileSelector(directory=directory, file_pattern=general_pattern, only_files=False)

    # Define the filtering function
    def filter_files(event):
        filtered_files = [
            file for file in file_selector.value if 
            any(pn.util.glob.fnmatch.fnmatch(file, pattern) for pattern in allowed_patterns)
        ]
        print("Filtered Files:", filtered_files)  # Replace with your desired processing logic

    # Attach the filtering function to changes in the FileSelector value
    file_selector.param.watch(filter_files, 'value')

    return file_selector


# @function_attributes(short_name=None, tags=['panel', 'filesystem', 'file', 'selection', 'interactive', 'USEFUL', 'Tabulator'], input_requires=[], output_provides=[], uses=['panel', 'pn.widgets.Tabulator'], used_by=[], creation_date='2025-01-14 08:42', related_items=[])
def create_file_browser(directory, patterns, page_size:int=25, widget_height:int=600, selectable='toggle', on_selected_files_changed_fn: Optional[Callable]=None, debug_print=False):
    """
    Create a file browser widget showing file metadata (name, size, dates).

    Parameters:
        directory (str): The directory to search files.
        patterns (list): List of glob patterns to match files.

    Returns:
        pn.widgets.Tabulator: A Tabulator widget displaying file metadata.
        
    
    Usage:

        from pyphocorehelpers.gui.Jupyter.simple_widgets import create_file_browser

        # # Function to create a file browser widget with metadata

        # Example usage
        directory = basedir # basedir.as_posix() # "/mnt/data"  # Replace with an appropriate path
        patterns = ['*loadedSessPickle.pkl', 'output/*.pkl']

        def on_selected_files_changed(selected_df: pd.DataFrame):
            ''' captures: file_table, on_selected_files_changed '''
            print(f"on_selected_files_changed(selected_df: {selected_df})")
            full_paths = selected_df['File Path'].to_list()
            print(f'\tfull_paths: {full_paths}')
            

        # Create the file browser widget
        file_browser_widget = create_file_browser(directory, patterns, page_size=10, widget_height=400, on_selected_files_changed_fn=on_selected_files_changed)

        # Display the widget
        file_browser_widget.servable()

    """
    import panel as pn
    
    pn.extension()
    # Initialize Panel extension
    pn.extension('tabulator')
                    
    # Function to get file information
    def get_file_info(directory, patterns):
        """ subfunction to locate files and their metadata """
        files_data = []
        for pattern in patterns:
            for file_path in Path(directory).glob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files_data.append({
                        "File Name": file_path.name,
                        "Size (KB)": round(stat.st_size / 1024, 2),
                        "Creation Date": pd.to_datetime(stat.st_ctime, unit='s'),
                        "Modification Date": pd.to_datetime(stat.st_mtime, unit='s'),
                        "Rel Path": str(file_path.relative_to(directory)),  # Relative path
                        "File Path": str(file_path),  # abs path
                    })
        # return pd.DataFrame(files_data).sort_values(by=['Modification Date', "Creation Date", "Size (KB)", "File Name"], axis='index', ascending=False).reset_index(drop=True)
        # Create DataFrame
        df = pd.DataFrame(files_data)
        
        # Only sort if DataFrame is not empty
        if not df.empty:
            return df.sort_values(by=['Modification Date', "Creation Date", "Size (KB)", "File Name"], 
                                axis='index', ascending=False).reset_index(drop=True)
        else:
            return df  # Return empty DataFrame without sorting
                


    # Fetch file data
    file_info_df = get_file_info(directory, patterns)

    # Create a Tabulator widget
    file_table = pn.widgets.Tabulator(
        file_info_df,
        selectable=selectable,
        pagination="local",
        page_size=page_size,
        height=widget_height,
        sorters=[{"field": "Modification Date", "dir": "desc"}],  # Sort by most recent modification
        # editable=False,  # Make cells read-only
        show_index=False,
        disabled=True, # Make cells read-only
    )

    # Callback to handle selection
    def on_selection(event):
        """ captures: file_table, on_selected_files_changed
        """
        # if event.new:
        #     # selected_file = file_info_df.iloc[event.new[0]]  # Get selected row
        #     # print(f"Selected File: {selected_file['File Path']}")
        #     # selected_files = file_info_df.iloc[event.new]  # Get selected row
            
        #     # # Map visible row index to original DataFrame index
        #     # sorted_indexes = file_table.indexes
        #     # selected_row_index = event.new[0]  # Get the visible row index
        #     # original_index = sorted_indexes[selected_row_index]  # Map to original DataFrame index
        #     # selected_file = file_info_df.iloc[original_index]  # Get the correct row
        #     # print(f"Selected File: {selected_file['File Path']}")
            
        #     # Map visible row indices to original DataFrame indices
        #     print(f'file_table.selection: {file_table.selection}')
        #     sorted_indexes = file_table.indexes
        #     selected_rows = [sorted_indexes[i] for i in event.new]  # Map visible indices to original indices
        #     selected_files = file_info_df.iloc[selected_rows]  # Get the correct rows
        #     print("Selected Files:")
        #     print(selected_files["File Path"].to_list())  # Print the selected file paths
            
        # selection
        # file_table.selection
        selected_df = deepcopy(file_table.selected_dataframe)
        # print(f"Selected Files: {selected_df['File Path']}")
        if on_selected_files_changed_fn is not None:
            on_selected_files_changed_fn(selected_df)
            

    file_table.param.watch(on_selection, 'selection')
    return file_table
    


def create_tab_widget(display_dict: Dict[str, Any], **tab_kwargs) -> widgets.Tab:
    """
    Creates an ipywidgets Tab widget that allows tabbing between multiple display items.

    Args:
        display_dict (Dict[str, Any]): A dictionary where keys are titles (str) and values are display items (Any).

    Returns:
        widgets.Tab: An ipywidgets Tab widget.
        
    Usage:
        from pyphocorehelpers.gui.Jupyter.simple_widgets import create_tab_widget
        df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        df2 = pd.DataFrame({'X': [7, 8, 9], 'Y': [10, 11, 12]})

        tab_widget = create_tab_widget({"DataFrame 1": df1, "DataFrame 2": df2})
        display(tab_widget)

    """
    # Inject custom CSS to adjust tab label widths
    display(HTML('''
    <style>
        /* Adjust the tab labels to accommodate longer titles */
        .widget-tab .p-TabBar-tab {
            max-width: none !important;
            min-width: auto !important;
        }
        .widget-tab .p-TabBar-tab .p-TabBar-tabLabel {
            white-space: normal !important;
        }
    </style>
    '''))
        
    # layout =   # Automatically adjust the width to fit titles
    # layout = tab_kwargs.pop('layout', widgets.Layout(width='max-content'))
    layout = tab_kwargs.pop('layout', widgets.Layout(width='auto'))
    tab = widgets.Tab(layout=layout, **tab_kwargs)
    children = []
    titles = list(display_dict.keys())
    items = list(display_dict.values())
    
    for item in items:
        children.append(widgets.Output())
    
    tab.children = children
    
    for i, title in enumerate(titles):
        tab.set_title(i, title)
    
    for i, item in enumerate(items):
        with children[i]:
            display(item)
    
    return tab






# ==================================================================================================================== #
# Selection Widgets                                                                                                    #
# ==================================================================================================================== #


import ipywidgets as widgets
import traitlets
from IPython.display import display
# from Spike3D..venv.Lib.site-packages.ipywidgets.widgets.widget_selection import _MultipleSelection

class CheckBoxListWidget(widgets.VBox):
    """ 
    from pyphocorehelpers.gui.Jupyter.simple_widgets import CheckBoxListWidget
    
    options_list = ['high_wcorr', 'user_selected', 'high_pearsonr_corr', 'high_shuffle_percentile_score', 'high_shuffle_wcorr_z_score', 'good_jump', 'long_duration']
    chk_box_list_widget = CheckBoxListWidget(options_list=options_list)
    chk_box_list_widget
    """
    # Define a trait for the value attribute
    value = traitlets.Any()
    
    _widgets = None
    

    @property
    def options_dict(self) -> Dict[str, bool]:
        """The options_list property."""
        return {k:v.value for k, v in self._widgets.items()}
    @options_dict.setter
    def options_dict(self, value: Dict[str, bool]):
        for k, v in value.items():
            assert k in self._widgets, f"k: {k} is not in self._widgets: {list(self._widgets.keys())}"
            a_widget = self._widgets.get(k, None)
            a_widget.value = v

    
    def __init__(self, options_list: Union[List[str], Dict[str, bool]], **kwargs):
        # Set the layout for the VBox to have a black border
        layout = kwargs.pop('layout', widgets.Layout(
            border='1px solid black',
            padding='0px',
            margin='0px'
        ))

        super().__init__(layout=layout, **kwargs)
        self._widgets = {}
        # Define a layout for the checkboxes with zero margins and padding
        checkbox_layout = widgets.Layout(
            margin='0px',
            padding='0px',
            height='auto',
            line_height='0.5em'  # Adjust this value as needed
            # line_height='normal'
        )

        if not isinstance(options_list, dict):
            options_list = {k:False for k in options_list} ## turn into a dict with default False (unchecked/disabled) values
            
        # Initialize child widgets
        # for k in options_list:
        for k, is_checked in options_list.items():
            self._widgets[k] = widgets.Checkbox(description=k, layout=checkbox_layout, value=is_checked)
            
        # Set the initial value
        # self.value = tuple([v.value for k, v in self._widgets.items()])
        self.value = tuple([k for k, v in self._widgets.items() if v.value]) # return the key for each checkbox that is checked.
        
        # Set the children of the HBox
        self.children = list(self._widgets.values())
        
        # Observe changes in child widgets
        for child_widget in self.children:
            child_widget.observe(self._on_widget_change, names='value')
    
    def _on_widget_change(self, change):
        # Update the value trait
        # self.value = tuple([v.value for k, v in self._widgets.items()])
        ## value is the selected value labels
        self.value = tuple([k for k, v in self._widgets.items() if v.value]) # return the key for each checkbox that is checked.
         
        
    @traitlets.observe('value')
    def _value_changed(self, change):
        # Callback when value changes
        # print(f'Value changed to: {self.value}')
        pass


    # def update_options_list(options_list: List):
    #     """ updates the existing options list """
    #     # Remove previous children ___________________________________________________________________________________________ #
    #     # Observe changes in child widgets
    #     for child_widget in self.children:
    #         child_widget.observe(self._on_widget_change, names='value')
    #         child_widget.remove()
            
    #     # Initialize child widgets
    #     for k in options_list:
    #         self._widgets[k] = widgets.Checkbox(description=k, layout=checkbox_layout)
            
    #     # Set the initial value
    #     # self.value = tuple([v.value for k, v in self._widgets.items()])
    #     self.value = tuple([k for k, v in self._widgets.items() if v.value]) # return the key for each checkbox that is checked.
        
    #     # Set the children of the HBox
    #     self.children = list(self._widgets.values())
        
    #     # Observe changes in child widgets
    #     for child_widget in self.children:
    #         child_widget.observe(self._on_widget_change, names='value')
            


# @function_attributes(short_name=None, tags=['widget', 'jupyter', 'ipywidgets'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-11-22 09:14', related_items=[])
class MultiCheckboxWidget(widgets.VBox):
    """Widget with a search field and lots of checkboxes.
    
        import ipywidgets as widgets
        from IPython.display import display
        from pyphocorehelpers.gui.Jupyter.simple_widgets import MultiCheckboxWidget
        
        def f(**kwargs):
            print(kwargs)

        options_dict = {
            x: widgets.Checkbox(
                description=x, 
                value=False,
                style={"description_width":"0px"}
            ) for x in ['hello','world']
        }

        ui = MultiCheckboxWidget(options_dict)
        out = widgets.interactive_output(f, options_dict)
        display(widgets.HBox([ui, out]))        
        
    """
    
    def __init__(self, options_dict):
        super().__init__()
        self.options_dict = options_dict
        
        # Create the search widget and output widget
        self.search_widget = widgets.Text()
        self.output_widget = widgets.Output()
        
        # Extract the checkboxes from the options_dict
        self.options = list(options_dict.values())
        
        # Define the layout for the options
        options_layout = widgets.Layout(
            overflow='auto',
            border='1px solid black',
            width='300px',
            height='300px',
            flex_flow='column',
            display='flex'
        )
        
        # Create a VBox to hold the checkboxes with the specified layout
        self.options_widget = widgets.VBox(self.options, layout=options_layout)
        
        # Initialize the VBox with the search widget and the options widget
        self.children = [self.search_widget, self.options_widget]
        
        # Set up observers for each checkbox
        for checkbox in self.options:
            checkbox.observe(self.on_checkbox_change, names='value')
        
        # Set up an observer for the search widget
        self.search_widget.observe(self.on_text_change, names='value')
        
        # Display the output widget
        display(self.output_widget)
        
    
    def on_checkbox_change(self, change):
        with self.output_widget:
            # Clear previous output
            self.output_widget.clear_output()
            
            # Re-sort the checkboxes based on their checked status
            self.options_widget.children = sorted(
                self.options_widget.children,
                key=lambda x: x.value,
                reverse=True
            )
    
    def on_text_change(self, change):
        with self.output_widget:
            # Clear previous output
            self.output_widget.clear_output()
            search_input = change['new'].lower().strip()
            
            # Filter the checkboxes based on the search input
            if search_input == '':
                # Reset to all options if search input is empty
                new_options = sorted(
                    self.options,
                    key=lambda x: x.value,
                    reverse=True
                )
            else:
                # Filter options that contain the search input
                filtered_keys = [
                    key for key in self.options_dict.keys()
                    if search_input in key.lower()
                ]
                new_options = sorted(
                    [self.options_dict[key] for key in filtered_keys],
                    key=lambda x: x.value,
                    reverse=True
                )
            self.options_widget.children = new_options
