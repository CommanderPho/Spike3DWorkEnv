"""
Async execution helper for Jupyter notebooks.

Provides a simple interface for running functions asynchronously in the background
with progress logging and callback support for updating notebook variables.

Usage:
------
from pyphocorehelpers.gui.Jupyter.AsyncExecutionHelper import run_async, AsyncExecutionHelper

############### Usage:

## USAGE 1: Updating workspace/globals variable on completion:

	from pyphocorehelpers.gui.Jupyter.AsyncExecutionHelper import run_async, AsyncExecutionHelper

	def load_data_DecodingLocalityMeasures(curr_active_pipeline, pkl_path):
		from pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.PredictiveDecodingComputations import DecodingLocalityMeasures
		return DecodingLocalityMeasures.from_file(pkl_path=pkl_path)

	pkl_output_path: Path = curr_active_pipeline.get_output_path().joinpath('2025-12-16_DecodingLocalityMeasures_result.pkl')
	future_load_DecodingLocalityMeasures = run_async(
		load_data_DecodingLocalityMeasures,
		curr_active_pipeline,
		pkl_output_path,
		on_success=lambda result: globals().update({'decoding_locality_measures': result}),
		# on_success=lambda result: setattr(curr_active_pipeline.global_computation_results.computed_data, 'DirectionalDecodersDecoded', result),
	)


## USAGE 2: Updating property of captured instance/dict on completion:

	from pyphocorehelpers.gui.Jupyter.AsyncExecutionHelper import run_async, AsyncExecutionHelper

	def load_data_DirectionalDecodersContinuouslyDecodedResult(curr_active_pipeline, pkl_path):
		from pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.DirectionalPlacefieldGlobalComputationFunctions import DirectionalDecodersContinuouslyDecodedResult
		return DirectionalDecodersContinuouslyDecodedResult.from_file(pkl_path=pkl_path)

	directional_decoders_decode_result_pkl_output_path: Path = curr_active_pipeline.get_output_path().joinpath('2025-12-16_directional_decoders_decode_result.pkl')
	future = run_async(
		load_data_DirectionalDecodersContinuouslyDecodedResult,
		curr_active_pipeline,
		directional_decoders_decode_result_pkl_output_path,
		on_success=lambda result: setattr(curr_active_pipeline.global_computation_results.computed_data, 'DirectionalDecodersDecoded', result)
	)


############### ALT AI-written usage:

	from pyphocorehelpers.gui.Jupyter.AsyncExecutionHelper import run_async, AsyncExecutionHelper

	# Simple usage with automatic output widget
	result = run_async(
		load_data_function,
		arg1, arg2,
		on_success=lambda result: setattr(some_object, 'data', result),
		on_error=lambda e: print(f"Error: {e}")
	)

	# Advanced usage with custom configuration
	helper = AsyncExecutionHelper(
		show_output=True,
		output_layout={"border": "1px solid gray", "max_height": "400px"}
	)
	future = helper.submit(
		load_data_function,
		arg1, arg2,
		on_success=lambda result: setattr(some_object, 'data', result)
	)


"""

import concurrent.futures
import traceback
from typing import Callable, Optional, Dict, Any, List
import ipywidgets as widgets
from IPython.display import display


class AsyncExecutionHelper:
    """
    Helper class for running functions asynchronously in Jupyter notebooks.
    
    Provides output widgets for logging, progress tracking, and callback support
    for updating notebook variables when tasks complete.
    """
    
    def __init__(self, show_output: bool = True, output_layout: Optional[Dict] = None, 
                 max_workers: int = 1, auto_display: bool = True):
        """
        Initialize the async execution helper.
        
        Parameters:
        -----------
        show_output : bool
            Whether to create and display an output widget for logging
        output_layout : dict, optional
            Layout dictionary for the output widget (passed to widgets.Output)
        max_workers : int
            Maximum number of worker threads (default: 1)
        auto_display : bool
            Whether to automatically display the output widget if show_output is True
        """
        self.show_output = show_output
        self.output_layout = output_layout or {"border": "1px solid gray"}
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        if show_output:
            self.output_widget = widgets.Output(layout=widgets.Layout(**self.output_layout))
            if auto_display:
                display(self.output_widget)
        else:
            self.output_widget = None
    
    def log(self, message: str):
        """Log a message to the output widget if available."""
        if self.output_widget is not None:
            self.output_widget.append_stdout(f"{message}\n")
        else:
            print(message)
    
    def _print_traceback(self):
        """Print traceback to output widget if available, otherwise to stderr."""
        import io
        tb_str = io.StringIO()
        traceback.print_exc(file=tb_str)
        tb_content = tb_str.getvalue()
        if self.output_widget is not None:
            self.output_widget.append_stderr(tb_content)
        else:
            traceback.print_exc()
    
    def submit(self, func: Callable, *args, on_success: Optional[Callable] = None, 
               on_error: Optional[Callable] = None, on_finally: Optional[Callable] = None,
               **kwargs) -> concurrent.futures.Future:
        """
        Submit a function to run asynchronously.
        
        Parameters:
        -----------
        func : callable
            The function to execute. If it accepts a parameter named 'out_widget',
            the output widget will be passed to it automatically.
        *args
            Positional arguments to pass to the function
        on_success : callable, optional
            Callback function(result) called when the function completes successfully
        on_error : callable, optional
            Callback function(exception) called when the function raises an exception
        on_finally : callable, optional
            Callback function() called after success or error (always called)
        **kwargs
            Keyword arguments to pass to the function
        
        Returns:
        --------
        concurrent.futures.Future
            Future object that can be used to check status and get results
        """
        def wrapped_func(*fargs, **fkwargs):
            """Wrapper that handles logging and callbacks."""
            try:
                self.log(f"[bg] Starting execution of {func.__name__}...")
                
                # If function accepts 'out_widget' parameter, pass it
                import inspect
                sig = inspect.signature(func)
                if 'out_widget' in sig.parameters and self.output_widget is not None:
                    fkwargs['out_widget'] = self.output_widget
                
                # Execute the function
                result = func(*fargs, **fkwargs)
                
                self.log(f"[bg] Execution of {func.__name__} completed successfully!")
                
                # Call success callback if provided
                if on_success is not None:
                    try:
                        on_success(result)
                        self.log(f"[bg] Success callback executed")
                    except Exception as callback_error:
                        self.log(f"[bg] ERROR in success callback: {callback_error}")
                        self._print_traceback()
                
                return result
                
            except Exception as e:
                error_msg = f"[bg] ERROR in {func.__name__}: {e}"
                self.log(error_msg)
                self._print_traceback()
                
                # Call error callback if provided
                if on_error is not None:
                    try:
                        on_error(e)
                        self.log(f"[bg] Error callback executed")
                    except Exception as callback_error:
                        self.log(f"[bg] ERROR in error callback: {callback_error}")
                        self._print_traceback()
                else:
                    # Re-raise if no error callback (preserve original behavior)
                    raise
                    
            finally:
                # Call finally callback if provided
                if on_finally is not None:
                    try:
                        on_finally()
                        self.log(f"[bg] Finally callback executed")
                    except Exception as callback_error:
                        self.log(f"[bg] ERROR in finally callback: {callback_error}")
                        self._print_traceback()
        
        # Submit to executor
        future = self.executor.submit(wrapped_func, *args, **kwargs)
        return future
    
    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=wait)


def run_async(func: Callable, *args, on_success: Optional[Callable] = None,
              on_error: Optional[Callable] = None, on_finally: Optional[Callable] = None,
              show_output: bool = True, output_layout: Optional[Dict] = None,
              max_workers: int = 1, **kwargs) -> concurrent.futures.Future:
    """
    Convenience function to run a function asynchronously with minimal boilerplate.
    
    This is a simplified interface that creates an AsyncExecutionHelper internally.
    For more control, use AsyncExecutionHelper directly.
    
    Parameters:
    -----------
    func : callable
        The function to execute. If it accepts a parameter named 'out_widget',
        the output widget will be passed to it automatically.
    *args
        Positional arguments to pass to the function
    on_success : callable, optional
        Callback function(result) called when the function completes successfully.
        Use this to update notebook variables, e.g.:
        on_success=lambda result: setattr(some_object, 'data', result)
    on_error : callable, optional
        Callback function(exception) called when the function raises an exception
    on_finally : callable, optional
        Callback function() called after success or error (always called)
    show_output : bool
        Whether to create and display an output widget for logging
    output_layout : dict, optional
        Layout dictionary for the output widget
    max_workers : int
        Maximum number of worker threads (default: 1)
    **kwargs
        Keyword arguments to pass to the function
    
    Returns:
    --------
    concurrent.futures.Future
        Future object that can be used to check status and get results
    
    Examples:
    ---------
    # Simple usage - just run a function
    future = run_async(load_data, file_path)
    
    # With success callback to update notebook variable
    future = run_async(
        load_data,
        file_path,
        on_success=lambda result: setattr(curr_active_pipeline.global_computation_results.computed_data, 
                                         'DirectionalDecodersDecoded', result)
    )
    
    # With multiple callbacks
    future = run_async(
        compute_result,
        input_data,
        on_success=lambda r: print(f"Got result: {r}"),
        on_error=lambda e: print(f"Failed: {e}"),
        on_finally=lambda: print("Done!")
    )
    
    # Check if done later
    if future.done():
        result = future.result(timeout=0)
    """
    helper = AsyncExecutionHelper(
        show_output=show_output,
        output_layout=output_layout,
        max_workers=max_workers
    )
    return helper.submit(func, *args, on_success=on_success, on_error=on_error, 
                        on_finally=on_finally, **kwargs)


def update_notebook_variable(var_name: str, value: Any, namespace: Optional[Dict] = None):
    """
    Helper function to update a notebook variable by name.
    
    This is useful as a callback to update notebook variables when async tasks complete.
    
    Parameters:
    -----------
    var_name : str
        Name of the variable to update in the notebook namespace
    value : Any
        Value to assign to the variable
    namespace : dict, optional
        Namespace dictionary to update. If None, attempts to get the calling frame's
        globals (may not work in all contexts - use on_success callback with setattr instead)
    
    Examples:
    ---------
    # In a callback
    on_success=lambda result: update_notebook_variable('my_result', result)
    
    Note: For updating object attributes, prefer using setattr directly:
    on_success=lambda result: setattr(some_object, 'attribute', result)
    """
    if namespace is None:
        import inspect
        frame = inspect.currentframe().f_back
        namespace = frame.f_globals
    
    namespace[var_name] = value

