"""

You can use `pd.describe_option()` to see the various customization options you can set for pandas

"""
from typing import Optional
import numpy as np
import pandas as pd
import ipykernel # ip: "ipykernel.zmqshell.ZMQInteractiveShell)" = IPython.get_ipython()
from IPython.display import display, HTML, Javascript
from ipywidgets import widgets, VBox



def set_pho_preferences(is_concise=False):
    """ Sets Pho Hale's general preferences for Jupyter Notebooks
    
    Includes increasing the number of rows/columns displayed for Pandas dataframes, and setting the numpy print options to be full-width for the jupyter notebook.
    """
    set_pho_numpy_display_preferences(is_concise=is_concise)
    set_pho_pandas_display_preferences(is_concise=is_concise)
    
def set_pho_preferences_verbose():
    is_concise=False
    set_pho_numpy_display_preferences(is_concise=is_concise)
    set_pho_pandas_display_preferences(is_concise=is_concise)

    
def set_pho_preferences_concise():
    is_concise=True
    set_pho_numpy_display_preferences(is_concise=is_concise)
    set_pho_pandas_display_preferences(is_concise=is_concise)
    

    
def set_pho_pandas_display_preferences(is_concise=True):
    import pandas as pd
    ## Pandas display options
    # pd.set_option('display.max_columns', None)  # or 1000
    # pd.set_option('display.max_rows', None)  # or 1000
    # pd.set_option('display.max_colwidth', -1)  # or 199
    pd.set_option('display.width', 1000)
    # pd.set_option('display.max_columns', None)  # or 1000
    # pd.set_option('display.max_rows', None)  # or 1000
    # pd.set_option('display.max_colwidth', -1)  # or 199
    # pd.set_option('display.width', 1000)
    pd.set_option('display.show_dimensions', True) # always shows dimensions even if the full dataframe can be printed.
    pd.set_option('display.max_columns', 256) # maximum number of columns to display
    if not is_concise:
        pd.set_option('display.min_rows', 30)
        pd.set_option('display.max_rows', 50)
    else:
        pd.set_option('display.min_rows', None)
        pd.set_option('display.max_rows', 12)

def set_pho_numpy_display_preferences(is_concise=True):
    import numpy as np
    ## Numpy display options:
    # Set up numpy print options to only wrap at window width:
    if is_concise:
        edgeitems = None
    else:
        edgeitems = 30
        
    np.set_printoptions(edgeitems=edgeitems, linewidth=100000, formatter=dict(float=lambda x: "%g" % x))
    # np.set_printoptions(edgeitems=3, linewidth=4096, formatter=dict(float=lambda x: "%.3g" % x))
    np.core.arrayprint._line_width = 144
    


# ---------------------------------------------------------------------------- #
#                       Jupyter Datatype Printing Helpers                      #
# ---------------------------------------------------------------------------- #

def array_repr_with_graphical_shape(ip: "ipykernel.zmqshell.ZMQInteractiveShell") -> "ipykernel.zmqshell.ZMQInteractiveShell":
    """Generate an HTML representation for a NumPy array, similar to Dask.
        
    from preferences_helpers import array_graphical_shape
    from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_preview_with_graphical_shape_repr_html
    
    # Register the custom display function for NumPy arrays
    import IPython
    
    ip: "ipykernel.zmqshell.ZMQInteractiveShell)" = IPython.get_ipython()


    """
    from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_preview_with_graphical_shape_repr_html
    # Register the custom display function for NumPy arrays
    ip.display_formatter.formatters['text/html'].for_type(np.ndarray, lambda arr: array_preview_with_graphical_shape_repr_html(arr))
    return ip


def array_repr_with_graphical_preview(ip: "ipykernel.zmqshell.ZMQInteractiveShell", include_shape: bool=True, horizontal_layout:bool=True, include_plaintext_repr:bool=True, height:int=50, width:Optional[int]=None) -> "ipykernel.zmqshell.ZMQInteractiveShell":
    """Generate an HTML representation for a NumPy array with a Dask shape preview and a thumbnail heatmap
    
    """
    from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_preview_with_heatmap_repr_html
    

    # Register the custom display function for NumPy arrays
    ip.display_formatter.formatters['text/html'].for_type(np.ndarray, lambda arr: array_preview_with_heatmap_repr_html(arr, include_shape=include_shape, horizontal_layout=horizontal_layout, include_plaintext_repr=include_plaintext_repr, height=height, width=width))
    
    # ## Plain-text type representation can be suppressed like:
    if include_plaintext_repr:
        # Override text formatter to prevent plaintext representation
        ## SIDE-EFFECT: messes up printing NDARRAYs embedded in lists, dicts, other objects, etc. It seems that when rendering these they use the 'text/plain' representations
        ip.display_formatter.formatters['text/plain'].for_type(
            np.ndarray, 
            lambda arr, p, cycle: None
        )
    
    return ip


#TODO 2024-08-07 13:02: - [ ] Finish custom plaintext formatting
# # Register the custom display function for NumPy arrays
# import IPython
# ip = IPython.get_ipython()

# def format_list_of_ndarrays(obj, p, cycle):
#     if all(isinstance(x, np.ndarray) for x in obj):
#         return "[" + ", ".join(np.array2string(a) for a in obj) + "]"
#     else:
#         # Fallback to the original formatter
#         return p.text(repr(obj))
#         # # Use the existing formatter if present, or default to repr
#         # existing_formatter = ip.display_formatter.formatters['text/plain'].lookup_by_type(list)
#         # return existing_formatter(obj, p, cycle) if existing_formatter else repr(obj)
    

# # ip.display_formatter.formatters['text/plain'].for_type(
# #     List[NDArray], 
# #     lambda arr, p, cycle: np.array2string(arr)
# # )

# # Register the custom formatter
# ip.display_formatter.formatters['text/plain'].for_type(list, format_list_of_ndarrays)
# ip.display_formatter.formatters['text/plain'].type_printers[np.ndarray]


# ip.display_formatter.formatters['text/plain'].type_printers.pop(list, None)


def dataframe_show_more_button(ip: "ipykernel.zmqshell.ZMQInteractiveShell") -> "ipykernel.zmqshell.ZMQInteractiveShell":
    """Adds a functioning 'show more' button below each displayed dataframe to show more rows.

    Usage:
        ip = get_ipython()
        ip = dataframe_show_more_button(ip=ip)
    """
    # def _subfn_dataframe_show_more(df, initial_rows=10):
    #     """Generate an HTML representation for a Pandas DataFrame with a 'show more' button."""
    #     total_rows = df.shape[0]
    #     if total_rows <= initial_rows:
    #         return df.to_html()

    #     # Create the initial view
    #     initial_view = df.head(initial_rows).to_html()

    #     # Escape backticks in the DataFrame HTML to ensure proper JavaScript string
    #     full_view = df.to_html().replace("`", r"\`").replace("\n", "\\n")

    #     # Generate the script for the 'show more' button
    #     script = f"""
    #     <script type="text/javascript">
    #         function showMore() {{
    #             var div = document.getElementById('dataframe-more');
    #             div.innerHTML = `{full_view}`;
    #         }}
    #     </script>
    #     """

    #     # Create the 'show more' button
    #     button = f"""
    #     <button onclick="showMore()">Show more</button>
    #     <div id="dataframe-more"></div>
    #     """

    #     # Combine everything into the final HTML
    #     html = f"""
    #     {script}
    #     {initial_view}
    #     {button}
    #     """
    #     return HTML(html)
    
    def _subfn_dataframe_show_more(df, initial_rows=10, default_more_rows=50):
        """Generate an HTML representation for a Pandas DataFrame with a 'show more' button."""
        total_rows = df.shape[0]
        if total_rows <= initial_rows:
            return df.to_html()

        # Create the initial view
        initial_view = df.head(initial_rows).to_html()

        # Escape backticks and newlines in the DataFrame HTML to ensure proper JavaScript string
        df_html = df.to_html().replace("`", "\\`").replace("\n", "\\n")

        # Generate the script for the 'show more' button with input for number of rows
        script = f"""
        <script type="text/javascript">
            function showMore() {{
                var numRows = document.getElementById('num-rows').value;
                if (numRows === "") {{
                    numRows = {default_more_rows};
                }} else {{
                    numRows = parseInt(numRows);
                }}
                var div = document.getElementById('dataframe-more');
                var df_html = `{df_html}`;
                var parser = new DOMParser();
                var doc = parser.parseFromString(df_html, 'text/html');
                var rows = doc.querySelectorAll('tbody tr');
                for (var i = 0; i < rows.length; i++) {{
                    if (i >= numRows) {{
                        rows[i].style.display = 'none';
                    }} else {{
                        rows[i].style.display = '';
                    }}
                }}
                div.innerHTML = doc.body.innerHTML;
            }}
        </script>
        """

        # Create the 'show more' button and input field with default value
        button_and_input = f"""
        <input type="number" id="num-rows" placeholder="Enter number of rows to display" value="{default_more_rows}">
        <button onclick="showMore()">Show more</button>
        <div id="dataframe-more"></div>
        """

        # Combine everything into the final HTML
        html = f"""
        {script}
        {initial_view}
        {button_and_input}
        """
        return HTML(html)


    ip.display_formatter.formatters['text/html'].for_type(pd.DataFrame, lambda df: display(_subfn_dataframe_show_more(df)))
    return ip



# Usage example



# def dataframe_show_more_button(ip: "ipykernel.zmqshell.ZMQInteractiveShell") -> "ipykernel.zmqshell.ZMQInteractiveShell":
#     """Adds a functioning "show more" button below each displayed dataframe to show more rows
            
#     Usage:
#         from pyphocorehelpers.preferences_helpers import array_repr_with_graphical_shape, dataframe_show_more_button

#         ip = get_ipython()

#         ip = array_repr_with_graphical_shape(ip=ip)
#         ip = dataframe_show_more_button(ip=ip)


#     """
#     # Register the custom display function for NumPy arrays
#     # ip.display_formatter.formatters['text/html'].for_type(pd.DataFrame, lambda df: ????(df))

#     def show_more(df, show_rows=5, _id=None):
#         # Generate a default id based on the object id if not specified
#         _id = f"df-{id(df)}" if _id is None else _id
#         return f"""
#         <div id="{_id}" class="dataframe-container">
#             {df.head(show_rows).to_html()}
#             <button onclick="showMoreRows('{_id}', {show_rows})">Show More</button>
#         </div>
#         <script>
#         function showMoreRows(id, showRows) {{
#             var dfContainer = document.getElementById(id);
#             var currentRows = dfContainer.getElementsByTagName('table')[0].rows.length - 1; // Subtract 1 for the header
#             var totalRows = {len(df)};
#             var newRows = Math.min(totalRows, currentRows + showRows);
#             var xhr = new XMLHttpRequest();
#             xhr.open('GET', `/_show_more?id=${id}&rows=${newRows}`, false); // Synchronous request for simplicity
#             xhr.send();
#             if (xhr.status === 200) {{
#                 dfContainer.innerHTML = xhr.responseText + dfContainer.innerHTML;
#             }}
#         }}
#         </script>
#         """

#     # Register the custom display function for pandas DataFrames
#     ip.display_formatter.formatters['text/html'].for_type(
#         pd.DataFrame, lambda df, show_rows=5, unique_id=None:
#         show_more(df, show_rows, unique_id)
#     )

#     return ip

    
