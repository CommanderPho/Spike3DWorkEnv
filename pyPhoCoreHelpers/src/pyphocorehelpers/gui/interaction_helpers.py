from typing import Callable
import numpy as np
from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes

@metadata_attributes(short_name=None, tags=['callback', 'sequence'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2023-05-08 14:51', related_items=[])
class CallbackSequence:
    """ Helper class to call a list of callbacks with the same argument sequentally """
    def __init__(self, callbacks_list, is_debug=False):
        self.is_debug=is_debug
        self.callbacks_list = callbacks_list

    def __call__(self, state):    
        # call the callbacks in order
        for i in np.arange(len(self.callbacks_list)):
            self.callbacks_list[i](state)
      
 

@metadata_attributes(short_name=None, tags=['callback', 'sequence', 'wrapper'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2023-05-08 14:51', related_items=[])
class CallbackWrapper(object):
    """ A simple wrapper class to handle defining separate user-provided setup(...), update(...) functions
    
    The conceptual idea is that many plots require separate setup code that is executed only once, and then once this is complete can be updated much more cheaply by calling an update(...) method. 
    
    Usage:
        def perform_draw_predicted_position_difference(frame, ax=None):
            return _temp_debug_draw_predicted_position_difference(active_one_step_decoder.most_likely_positions, active_resampled_measured_positions, frame, ax=ax)

        def perform_update_predicted_position_difference(frame, ax=None, predicted_line=None, measured_line=None, **kwargs):
            return _temp_debug_draw_update_predicted_position_difference(active_one_step_decoder.most_likely_positions, active_resampled_measured_positions, frame, ax=ax, predicted_line=predicted_line, measured_line=measured_line, **kwargs)

        active_predicted_position_difference_plot_callback_wrapper = CallbackWrapper(perform_draw_predicted_position_difference, perform_update_predicted_position_difference, dict())    
    """
    def __init__(self, on_setup, on_update, state):
        super(CallbackWrapper, self).__init__()
        self.state = state
        self.on_setup = on_setup
        self.on_update = on_update
        self._is_setup = False
        self.output_data = dict()
        
    def setup(self, *args, **kwargs):
        updated_output_data = self.on_setup(*args, **kwargs)
        self.output_data = self.output_data | updated_output_data
        self._is_setup = True
        return self.output_data

    def update(self, *args, **kwargs):
        if not self._is_setup:
            self.setup(*args, **kwargs)
            assert self._is_setup, "just ran self.setup(...) but self._is_setup is still False!"
        self.output_data = (self.output_data | kwargs) # update the output data with any explicitly passed keyword args, like the ax object.
        return self.on_update(*args, **self.output_data) # pass the output data as keyword arguments to the update function

    def __call__(self, state, **kwargs):
        self.update(state, **kwargs)
        
        