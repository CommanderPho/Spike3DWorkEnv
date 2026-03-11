from pathlib import Path
import ipywidgets as widgets
from IPython.display import display
from PIL import Image as PILImage
from io import BytesIO
from typing import Dict
from datetime import datetime
from PIL import Image, ImageDraw, UnidentifiedImageError
import ipywidgets as widgets
from datetime import datetime

from ipywidgets import VBox, HBox, Dropdown, Button, Output
from PIL import Image as PILImage
from io import BytesIO

from pyphocorehelpers.programming_helpers import copy_to_clipboard

# Load PDF and convert each page to a PIL Image
def load_pdf_as_images(pdf_path: str, poppler_path: Path=None, last_page: int=None):
    # Convert PDF to list of images (one per page)
    from pdf2image import convert_from_path
    if poppler_path is None:
        poppler_path = Path(r"C:\Users\pho\lib\poppler-24.07.0\Library\bin").resolve()
    images = convert_from_path(pdf_path, poppler_path=poppler_path, last_page=last_page)
    return images

def create_placeholder_image(text, width, height):
    img = Image.new('RGB', (width, height), color='gray')
    d = ImageDraw.Draw(img)
    d.text((10, height // 2 - 10), text, fill=(255, 255, 255))
    return img

# @metadata_attributes(short_name=None, tags=['jupyter-widget', 'interactive', 'gui'], input_requires=[], output_provides=[], uses=['ContextSidebar'], used_by=[], creation_date='2024-10-04 17:48', related_items=[])
class ImageNavigator:
    """ 
    from pyphocorehelpers.gui.Jupyter.JupyterImageNavigatorWidget import ImageNavigator
    
    
    Example 1:
        from pyphocorehelpers.gui.Jupyter.JupyterImageNavigatorWidget import ImageNavigator

        # Create 6 example ImageNavigator instances with different placeholder images and sizes
        image_dict_1 = {
            datetime(2023, 4, 11): create_placeholder_image("Image 1-1", 200, 200),
            datetime(2023, 5, 12): create_placeholder_image("Image 1-2", 200, 200)
        }

        image_dict_2 = {
            datetime(2023, 6, 13): create_placeholder_image("Image 2-1", 250, 150),
            datetime(2023, 7, 14): create_placeholder_image("Image 2-2", 250, 150)
        }

        image_dict_3 = {
            datetime(2023, 8, 15): create_placeholder_image("Image 3-1", 300, 300),
            datetime(2023, 9, 16): create_placeholder_image("Image 3-2", 300, 300)
        }

        image_dict_4 = {
            datetime(2023, 10, 17): create_placeholder_image("Image 4-1", 150, 250),
            datetime(2023, 11, 18): create_placeholder_image("Image 4-2", 150, 250)
        }

        image_dict_5 = {
            datetime(2023, 12, 19): create_placeholder_image("Image 5-1", 350, 200),
            datetime(2024, 1, 20): create_placeholder_image("Image 5-2", 350, 200)
        }

        image_dict_6 = {
            datetime(2024, 2, 21): create_placeholder_image("Image 6-1", 200, 350),
            datetime(2024, 3, 22): create_placeholder_image("Image 6-2", 200, 350)
        }

        # Instantiate the ImageNavigator objects with different sizes
        navigator1 = ImageNavigator(image_dict_1, "Navigator 1")
        navigator2 = ImageNavigator(image_dict_2, "Navigator 2")
        navigator3 = ImageNavigator(image_dict_3, "Navigator 3")
        navigator4 = ImageNavigator(image_dict_4, "Navigator 4")
        navigator5 = ImageNavigator(image_dict_5, "Navigator 5")
        navigator6 = ImageNavigator(image_dict_6, "Navigator 6")

        # Adjust the layout of each navigator to fill its container based on its image size
        navigator1.vbox.layout = widgets.Layout(width='auto', height='auto')
        navigator2.vbox.layout = widgets.Layout(width='auto', height='auto')
        navigator3.vbox.layout = widgets.Layout(width='auto', height='auto')
        navigator4.vbox.layout = widgets.Layout(width='auto', height='auto')
        navigator5.vbox.layout = widgets.Layout(width='auto', height='auto')
        navigator6.vbox.layout = widgets.Layout(width='auto', height='auto')

        # Collect their VBox elements for display
        navigator_widgets = [
            navigator1.vbox,
            navigator2.vbox,
            navigator3.vbox,
            navigator4.vbox,
            navigator5.vbox,
            navigator6.vbox
        ]

        # Define a GridBox layout with 3 columns and a grid gap, allowing the navigators to expand
        grid = widgets.GridBox(
            navigator_widgets,
            layout=widgets.Layout(grid_template_columns="repeat(3, 1fr)", grid_gap="10px")
        )

        # Display the grid
        display(grid)


    """
    def __init__(self, image_dict: Dict[datetime, PILImage.Image], image_title: str):
        assert len(image_dict) > 0
        self.image_dict = image_dict
        self.image_title = image_title
        self.keys = list(image_dict.keys())
        self.current_index = 0
        self.total_images = len(self.keys)
        
        # Widgets
        self.title_label = widgets.Label(value=self.image_title)
        self.image_display = widgets.Image()
        self.date_label = widgets.Label(value=str(self.keys[self.current_index]))
        self.counter_label = widgets.Label(value=f"Image {self.current_index + 1}/{self.total_images}")
        
        self.left_button = widgets.Button(description="←", layout=widgets.Layout(width='50px'))
        self.right_button = widgets.Button(description="→", layout=widgets.Layout(width='50px'))

        # Set up event listeners for the buttons
        self.left_button.on_click(self.on_left_click)
        self.right_button.on_click(self.on_right_click)

        # Initial display setup
        self.update_image()

        # Layout
        self.controls = widgets.HBox([self.counter_label, self.left_button, self.date_label, self.right_button])
        self.vbox = widgets.VBox([self.title_label, self.image_display, self.controls])

    def update_image(self):
        """Updates the image display and the date label based on the current index."""
        current_key = self.keys[self.current_index]
        img = self.image_dict[current_key]
        try:
            if isinstance(img, (Path, str)):
                ## load the image
                if img.name.endswith('.pdf'):
                    img = load_pdf_as_images(img, poppler_path=Path(r"C:\Users\pho\lib\poppler-24.07.0\Library\bin").resolve(), last_page=1)[0] # get the first page only
                else:
                    img = Image.open(img.as_posix())
                self.image_dict[current_key] = img
                
        except (UnidentifiedImageError, BaseException) as e:
            img = None
            print(f'err: {e}, skipping.') 
            img = create_placeholder_image("<No Image>", width=100, height=100)
            # raise e

        # Convert PIL image to bytes for display in ipywidgets.Image
        with BytesIO() as output:
            img.save(output, format="PNG")
            img_data = output.getvalue()

        # Update the image widget and date label
        self.image_display.value = img_data
        self.date_label.value = str(current_key)
        self.counter_label.value = f"Image {self.current_index + 1}/{self.total_images}"

    def on_left_click(self, _):
        """Handle left button click: go to the previous image."""
        self.current_index = (self.current_index - 1) % len(self.keys)
        self.update_image()

    def on_right_click(self, _):
        """Handle right button click: go to the next image."""
        self.current_index = (self.current_index + 1) % len(self.keys)
        self.update_image()

    def display(self):
        """Display the widget."""
        display(self.vbox)

class ContextSidebar:
    """ 
    Usage:
        from pyphocorehelpers.gui.Jupyter.JupyterImageNavigatorWidget import ContextSidebar, ImageNavigator
    
        # Example usage with some example contexts
        context_dict = {
            'Context 1': 'Description or content for Context 1',
            'Context 2': 'Description or content for Context 2',
            'Context 3': 'Description or content for Context 3',
        }

        sidebar = ContextSidebar(context_dict)
        sidebar.display()

    
    """
    def __init__(self, context_dict):
        self.context_dict = context_dict
        self.context_tabs = list(context_dict.keys())

        # Create a sidebar with a vertical tab layout
        self.tab_widget = widgets.Tab()

        # Set the tab titles and content
        self.tab_widget.children = tuple(self.context_dict.values()) # [self.create_tab_content(context) for context in self.context_tabs]
        for i, context in enumerate(self.context_tabs):
            self.tab_widget.set_title(i, context)

        # Layout the sidebar vertically
        self.sidebar = widgets.VBox([self.tab_widget], layout=widgets.Layout(width='auto'))

    def create_tab_content(self, context):
        # Create content for each tab (you can customize this)
        label = widgets.Label(value=f"Currently viewing context: {context}")
        return widgets.VBox([label])

    def display(self):
        """Display the sidebar widget."""
        display(self.sidebar)
        

# @metadata_attributes(short_name=None, tags=['jupyter', 'widget', 'gui', 'images'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-10-04 17:50', related_items=['ImageNavigator'])
class ImageContextViewer:
    """ Displays a drop-down box to select from a list of contexts. For each contexts, enables thumbing through a list of images.
    A bit simpler *but redundant* with `ImageNavigator`
    Usage:
        from pyphoplacecellanalysis.SpecificResults.PendingNotebookCode import ImageContextViewer
        
        # Example usage
        _flattened_context_path_dict = {
            'Context 1': 'path_to_image_1.png',
            'Context 2': 'path_to_image_2.png',
            'Context 3': 'path_to_image_3.png',
            # Add more context-image pairs as needed
        }

        viewer = ImageContextViewer(_flattened_context_path_dict)
        viewer.display()

    
    
    """
    def __init__(self, context_image_dict: dict):
        self.context_image_dict = {k:v for k, v in context_image_dict.items() if len(v)>0} ## only include contexts that have non-empty lists of values
        self.contexts = list(self.context_image_dict.keys())
        self.current_context_index = 0

        # Widgets
        self.context_dropdown = Dropdown(options=self.contexts, description='Context:', layout=widgets.Layout(width='600px'))
        self.image_display = Output()
        self.next_button = Button(description="Next")
        self.previous_button = Button(description="Previous")
        
        button_layout = widgets.Layout(flex='0 1 auto', width='auto', min_width='80px', margin='1px') # The button_layout ensures that buttons don't grow and are only as wide as necessary.
        # right_label_layout = widgets.Layout(flex='1 1 auto', min_width='0px', width='auto') # We use the flex property in the right_label_layout to let the label grow and fill the space, but it can also shrink if needed (flex='1 1 auto'). We set a min_width so it doesn't get too small and width='auto' to let it size based on content
        self.copy_to_clipboard_button = widgets.Button(description='Copy', layout=button_layout, button_style='info', tooltip='Copy to Clipboard', icon='clipboard') # , icon='folder-tree'
        self.copy_to_clipboard_button.on_click(lambda _: copy_to_clipboard(str(self.context_dropdown.value)))
    
        # Set up event listeners
        self.context_dropdown.observe(self.on_context_change, names='value')
        self.next_button.on_click(self.next_context)
        self.previous_button.on_click(self.previous_context)

        # Display the initial image
        self.update_image_display(self.contexts[self.current_context_index])

    # Function to load the image from path
    def load_image(self, path: str) -> bytes:
        with open(path, 'rb') as f:
            return f.read()

    # Function to update the displayed image
    def update_image_display(self, context: str):
        images = self.context_image_dict[context]
        try:
            image_path = images[self.current_context_index]
        except IndexError as e:
            print(f'index error encountered: {e}\n\tcontext: {context}\n\timages: {images}\n\tself.current_context_index:{self.current_context_index}')
            return
        except Exception as e:
            raise e
        
        with self.image_display:
            self.image_display.clear_output(wait=True)
            img_data = self.load_image(image_path)
            image = PILImage.open(BytesIO(img_data))
            display(image)

    # Function to handle dropdown context change
    def on_context_change(self, change):
        self.update_image_display(change['new'])

    # Function to handle the next button click
    def next_context(self, _):
        self.current_context_index = (self.current_context_index + 1) % len(self.contexts)
        self.context_dropdown.value = self.contexts[self.current_context_index]

    # Function to handle the previous button click
    def previous_context(self, _):
        self.current_context_index = (self.current_context_index - 1) % len(self.contexts)
        self.context_dropdown.value = self.contexts[self.current_context_index]

    # Function to display the viewer
    def display(self):
        # display(VBox([self.context_dropdown, self.image_display, HBox([self.previous_button, self.next_button])]))
        display(VBox([HBox([self.context_dropdown, self.copy_to_clipboard_button]), self.image_display, HBox([self.previous_button, self.next_button])]))


    
    
def build_context_images_navigator_widget(curr_context_images_dict, curr_context_desc_str: str, max_num_widget_debug: int = 5):
    """ Builds a single tab's contents (a widget consisting of a title and a `GridBox` of images

    Usage:
    
        from pyphocorehelpers.gui.Jupyter.JupyterImageNavigatorWidget import build_context_images_navigator_widget, ContextSidebar, ImageNavigator
        
        ## INPUTS: _final_out_dict_dict: Dict[ContextDescStr, Dict[ImageNameStr, Dict[datetime, Path]]]
        context_tabs_dict = {curr_context_desc_str:build_context_images_navigator_widget(curr_context_images_dict, curr_context_desc_str=curr_context_desc_str, max_num_widget_debug=2) for curr_context_desc_str, curr_context_images_dict in list(_final_out_dict_dict.items())}
        sidebar = ContextSidebar(context_tabs_dict)
        sidebar.display()


    """
    label_layout = widgets.Layout(width='auto',height='auto')
    # Collect their VBox elements for display
    navigators = []

    for an_image_name, an_image_history_dict in curr_context_images_dict.items():
        if len(navigators) < max_num_widget_debug:
            if len(an_image_history_dict) > 0:
                navigator1 = ImageNavigator(an_image_history_dict, an_image_name)
                navigator1.vbox.layout = widgets.Layout(width='auto', height='auto')
                navigators.append(navigator1)


    navigator_widgets = [nav.vbox for nav in navigators]
    # Define a GridBox layout with 3 columns and a grid gap, allowing the navigators to expand
    # title_label = widgets.Label(value=f"Currently viewing context: {curr_context_desc_str}", layout=label_layout, **label_style_kwargs)
    
    title_label_widget = widgets.HBox([widgets.Label(value=f"Currently viewing context: "),
                                       widgets.Button(description=f"{curr_context_desc_str}", button_style='danger', layout=label_layout),
    ])

    grid = widgets.GridBox(
        navigator_widgets,
        layout=widgets.Layout(grid_template_columns="repeat(3, 1fr)", grid_gap="10px")
    )
    return widgets.VBox([title_label_widget, grid])


