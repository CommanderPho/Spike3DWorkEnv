from attrs import define, field
from ipywidgets import Accordion, Label
from IPython.display import display

@define(slots=False)
class ObjectBrowser:
    """ 
    from pyphocorehelpers.gui.Jupyter.PhoObjectBrowser_JupyterWidget import ObjectBrowser
    browser = ObjectBrowser(object_to_browse=curr_active_pipeline.global_computation_results.computed_data)
    browser.show()

    """
    object_to_browse: object

    def display_object(self, obj, level=0):
        accordion = Accordion(children=[])
        accordion.selected_index = None # Start with all collapsed

        for key, value in vars(obj).items():
            label = Label(f'{key}: {value}')
            accordion.children += (label,)
            accordion.set_title(level, key)
            
            if hasattr(value, '__dict__'):
                inner_accordion = self.display_object(value, level+1)
                accordion.children += (inner_accordion,)

        return accordion

    def show(self):
        root_accordion = self.display_object(self.object_to_browse)
        display(root_accordion)
        