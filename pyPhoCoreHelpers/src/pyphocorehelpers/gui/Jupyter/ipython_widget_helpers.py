import asyncio
from time import time
from threading import Timer # used in `throttle(...)`
from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes
from enum import Enum
import ipywidgets as widgets
from IPython.display import display

def throttle(wait):
    """ Decorator that prevents a function from being called more than once every wait period. 
    https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#throttling
    
    from pyphocorehelpers.gui.Jupyter.ipython_widget_helpers import throttle
    
    
    """

    def decorator(fn):
        time_of_last_call = 0
        scheduled, timer = False, None
        new_args, new_kwargs = None, None
        def throttled(*args, **kwargs):
            nonlocal new_args, new_kwargs, time_of_last_call, scheduled, timer
            def call_it():
                nonlocal new_args, new_kwargs, time_of_last_call, scheduled, timer
                time_of_last_call = time()
                fn(*new_args, **new_kwargs)
                scheduled = False
            time_since_last_call = time() - time_of_last_call
            new_args, new_kwargs = args, kwargs
            if not scheduled:
                scheduled = True
                new_wait = max(0, wait - time_since_last_call)
                timer = Timer(new_wait, call_it)
                # timer = pg.QtCore.QTimer()
                timer.start()
        return throttled
    return decorator


""" 
from pyphocorehelpers.gui.Jupyter.ipython_widget_helpers import throttle

slider = widgets.IntSlider()
text = widgets.IntText()

@throttle(0.2)
def value_changed(change):
    text.value = change.new
slider.observe(value_changed, 'value')

widgets.VBox([slider, text])


"""

@metadata_attributes(short_name=None, tags=['enum', 'widgets', 'ipywidget', 'helper'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-01-06 22:26', related_items=[])
class EnumSelectorWidgets:
    """ help to allow the user to select between enum-type variables
    
    from pyphocorehelpers.gui.Jupyter.ipython_widget_helpers import EnumSelectorWidgets

    # Define an example Enum
    class Color(Enum):
        RED = "Red"
        GREEN = "Green"
        BLUE = "Blue"
        
    target_enum_class = Color	
    # target_enum_class = PipelineSavingScheme

    # ==================================================================================================================== #
    # Example 1: Options Dropdown Control                                                                                  #
    # ==================================================================================================================== #
        
    # Create and display the selector
    selector = EnumSelectorWidgets.create_enum_selector(target_enum_class)

    # Access selected value
    def on_value_change(change):
        print(f"Selected: {change['new']}") # for `create_enum_selector`

    selector.observe(on_value_change, names='value')


    # ==================================================================================================================== #
    # Example 2: Options Toggle Control                                                                                    #
    # ==================================================================================================================== #
    
    # Create and display the selector
    selector = EnumSelectorWidgets.create_enum_toggle_buttons(target_enum_class)

    # Access selected value
    def on_value_change(change):
        print(f"Selected: {target_enum_class[change['new']]}") ## for `create_enum_toggle_buttons`

    selector.observe(on_value_change, names='value')


    """
    @classmethod
    def create_enum_selector(cls, enum_cls, defer_display:bool=False):
        """
        Create an ipywidget dropdown for selecting an option from an Enum.

        Args:
            enum_cls (Enum): The Enum subclass to generate the selector for.

        Returns:
            widgets.Dropdown: An ipywidget dropdown for selecting an Enum option.
        """
        if not issubclass(enum_cls, Enum):
            raise TypeError("Provided class must be a subclass of Enum.")
        
        # Map Enum members to their displayable names
        options = [(member.name, member) for member in enum_cls]
        
        # Create a dropdown widget
        dropdown = widgets.Dropdown(
            options=options,
            description=f"{enum_cls.__name__}:",
            style={'description_width': 'initial'}
        )
        
        # Display the dropdown in the notebook
        if not defer_display:
            display(dropdown)
        
        return dropdown

    @classmethod
    def create_enum_toggle_buttons(cls, enum_cls, defer_display:bool=False):
        """
        Create an ipywidget toggle button list for selecting an option from an Enum.

        Args:
            enum_cls (Enum): The Enum subclass to generate the toggle buttons for.

        Returns:
            widgets.ToggleButtons: An ipywidget toggle button widget for selecting an Enum option.
        """
        if not issubclass(enum_cls, Enum):
            raise TypeError("Provided class must be a subclass of Enum.")
        
        # Map Enum members to their displayable names
        options = [member.name for member in enum_cls]
        
        # Create a toggle button widget
        toggle_buttons = widgets.ToggleButtons(
            options=options,
            description=f"{enum_cls.__name__}:",
            style={'description_width': 'initial'},
            button_style='',  # Use '' for default style or 'success', 'info', etc.
            tooltips=[f"Select {member.name}" for member in enum_cls]
        )
        
        # # Function to map selected label back to the Enum value
        # def on_value_change(change):
        #     selected_enum = enum_cls[change['new']]
        #     print(f"Selected Enum: {selected_enum}")

        # # Attach observer for value changes
        # toggle_buttons.observe(on_value_change, names='value')
        
        # Display the toggle buttons in the notebook
        if not defer_display:
            display(toggle_buttons)
        
        return toggle_buttons


