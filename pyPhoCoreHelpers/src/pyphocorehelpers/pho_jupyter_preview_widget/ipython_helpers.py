from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython import get_ipython
from IPython.display import display
import ipykernel
import numpy as np
import pandas as pd

# from pho_jupyter_preview_widget.display_helpers import render_scrollable_colored_table_from_dataframe
from pyphocorehelpers.print_helpers import render_scrollable_colored_table_from_dataframe, render_scrollable_colored_table

def _parse_ndarray_preview_params(line: str) -> Dict:
    """ 
    %%ndarray_preview height=500, width=200, include_plaintext_repr=False
    
    %%ndarray_preview height=None, width=100, include_plaintext_repr=True, include_shape=False, horizontal_layout=False
    
    """
    # Split the magic line by commas to get individual key-value pairs (like `%%ndarray_preview height=500, width=200, include_plaintext_repr=False`)
    params = line.split(',')
    config = {}
    
    for param in params:
        key, value = param.split('=')
        key = key.strip()
        value = value.strip()
        # Convert string representation to appropriate type
        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.lower() =='none':
            value = None
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        config[key] = value
        
    return config


@magics_class
class PreviewWidgetMagics(Magics):
    """ 
    ## Usage:

        from pyphocorehelpers.pho_jupyter_preview_widget.ipython_helpers import PreviewWidgetMagics
        # Register the magic
        ip = get_ipython()
        ip.register_magics(PreviewWidgetMagics)

    """
    @line_magic
    def config_ndarray_preview(self, line):
        """ Updates the display preview config (persistantly). Is a line magic because it updates the ipython display_formatter directly and will persist for the remainder (and the following) cells
            Allows the user to change the thumbnail image size like:
    
        # call the line magic
        %config_ndarray_preview width=500 
        
        
        %config_ndarray_preview height=300, width=None, include_plaintext_repr=False, include_shape=False
        
        
        """
        from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_repr_with_graphical_preview
        config = _parse_ndarray_preview_params(line=line)

        ip = get_ipython()
        array_repr_with_graphical_preview(ip=ip, **config)
        

    @cell_magic
    def ndarray_preview(self, line, cell):
        """ 
        %%ndarray_preview height=500, width=200, include_plaintext_repr=False
        
        %%ndarray_preview height=None, width=100, include_plaintext_repr=True, include_shape=False, horizontal_layout=False

        %%ndarray_preview height=None, width=100, include_plaintext_repr=True, include_shape=False, horizontal_layout=False
        
        compatable with `InteractiveShell.ast_node_interactivity = "all"` and handles multiple outputs gracefully.
        
        """
        from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_repr_with_graphical_preview
            
        debug_print = False

        # Split the magic line by commas to get individual key-value pairs (like `%%ndarray_preview height=500, width=200, include_plaintext_repr=False`)
        params = line.split(',')
        config = _parse_ndarray_preview_params(line=line) 
        
        if debug_print:
            print(f'config: {config}\n')
            
        ip = get_ipython()
        
        ## Backup the current NDArray formatter
        _bak_formatter = ip.display_formatter.formatters['text/html'].type_printers.pop(np.ndarray, None)
            
        # Register the custom display function for NumPy arrays for the duration of the cell:
        array_repr_with_graphical_preview(ip=ip, **config)

        # Split the cell into individual lines
        cell_lines = cell.splitlines()
        cell_outputs = []
        
        # Execute each line and capture output (for compatibility with `InteractiveShell.ast_node_interactivity = "all"` to handle multiple outputs gracefully)
        for line in cell_lines:
            exec(line, self.shell.user_ns, self.shell.user_ns)
            
            # If the last line was an expression, capture its value to display
            if line.strip() and not line.strip().startswith('#'):
                try:
                    output = eval(line, self.shell.user_ns, self.shell.user_ns)
                    if output is not None:
                        display(output)
                        cell_outputs.append(output)
                        
                except BaseException:
                    pass  # Ignore errors for non-expressions or if exec-ed code raises an exception
        
        # Remove the custom formatter
        ip.display_formatter.formatters['text/html'].type_printers.pop(np.ndarray, None)

        ## Restore the previous formatter
        if _bak_formatter is not None:
            ip.display_formatter.formatters['text/html'].for_type(np.ndarray, _bak_formatter)
        





