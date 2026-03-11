from ipywidgets import DOMWidget
from traitlets import Unicode

class MyWidget(DOMWidget):
    _view_name = Unicode('MyWidgetView').tag(sync=True)
    _view_module = Unicode('pho_jupyter_preview_widget').tag(sync=True)
    _view_module_version = Unicode('0.1.0').tag(sync=True)

    action = Unicode('').tag(sync=True)
