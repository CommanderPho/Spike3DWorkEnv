import sys
import traceback
from functools import reduce
from itertools import accumulate
from functools import wraps # This convenience func preserves name and docstring
from typing import Dict, List, Callable, Optional, Any # for function composition

from pyphocorehelpers.exception_helpers import CapturedException

""" 
TODO: add a version of compose_functions that's capable of reporting progress of executing the composed functions, and perhaps that is capable of timing them. 
"""

def compose_functions(*args, progress_logger=None, error_logger=None):
    """ Composes n functions passed as input arguments into a single lambda function efficienctly.
    right-to-left ordering (default): compose(f1, f2, ..., fn) == lambda x: f1(...(f2(fn(x))...)
    # OLD: left-to-right ordering: compose(f1, f2, ..., fn) == lambda x: fn(...(f2(f1(x))...)
    Note that functions are composed from right-to-left, meaning that the first function input is the outermost function
    Usage:
        post_load_functions = [lambda a_loaded_sess: estimation_session_laps(a_loaded_sess), lambda a_loaded_sess: a_loaded_sess.filtered_by_neuron_type('pyramidal')]
    composed_post_load_function = compose_functions(*post_load_functions) # functions are composed right-to-left (math order)
    composed_post_load_function(curr_kdiba_pipeline.sess)
    """
    def _(x):
        result = x
        total_num_funcs = len(args)
        for i, f in enumerate(reversed(args)):
            if progress_logger is not None:
                progress_logger(f'Executing [{i}/{total_num_funcs}]: {f}')
            result = f(result)
        return result
    return _

def compose_functions_with_error_handling(*args, progress_logger=None, error_logger=None):
    """ Composes n functions passed as input arguments into a single lambda function efficienctly.
    right-to-left ordering (default): compose(f1, f2, ..., fn) == lambda x: f1(...(f2(fn(x))...)
    # OLD: left-to-right ordering: compose(f1, f2, ..., fn) == lambda x: fn(...(f2(f1(x))...)
    Note that functions are composed from right-to-left, meaning that the first function input is the outermost function
    Usage:
        post_load_functions = [lambda a_loaded_sess: estimation_session_laps(a_loaded_sess), lambda a_loaded_sess: a_loaded_sess.filtered_by_neuron_type('pyramidal')]
        composed_post_load_function = compose_functions(*post_load_functions) # functions are composed right-to-left (math order)
        composed_post_load_function(curr_kdiba_pipeline.sess)
    """
    def _(x):
        """ implicitly captures progress_logger from outer function"""
        result = x # initially set the result to the input
        accumulated_errors = dict() # empty list for keeping track of exceptions
        total_num_funcs = len(args)
        for i, f in enumerate(reversed(args)):
            if progress_logger is not None:
                progress_logger(f'Executing [{i}/{total_num_funcs}]: {f}')
            try:
                temp_result = f(result) # evaluate the function 'f' using the result provided from the previous output or the initial input
            except (TypeError, ValueError, NameError, AttributeError, KeyError, NotImplementedError) as e:
                exception_info = sys.exc_info()
                accumulated_errors[f] = CapturedException(e, exception_info, result)
                # accumulated_errors.append(e) # add the error to the accumulated error array
                temp_result = result # restore the result from prior to the calculations?
                # result shouldn't be updated unless there wasn't an error, so it should be fine to move on to the next function
                if error_logger is not None:
                    error_logger(f'\t Encountered error: {accumulated_errors[f]} continuing.')
            except BaseException as e:
                print(f'UNHANDLED EXCEPTION: {e}')
                raise
                
            else:
                # only if no error occured do we commit the temp_result to result
                result = temp_result
                if progress_logger is not None:
                    progress_logger('\t done.')
                    
            # finally:
            #     # do this no matter what
            #     # result
            #     pass
        return result, accumulated_errors # new function returns both the result and the accumulated errors
    return _



def add_method(cls):
    """Enables post-hoc method adding to any python class using a simple decorator design. Enables easily "extending" classes at runtime or in jupyter notebooks without magic.
        From https://gist.github.com/mgarod/09aa9c3d8a52a980bd4d738e52e5b97a
        Credit to mgarod
        From article https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
        
    Usage: Example of adding two functions to a class named "cls_A"
        # Non-decorator way (note the function must accept self)
        # def foo(self):
        #     print('hello world!')
        # setattr(cls_A, 'foo', foo)

        # def bar(self, s):
        #     print(f'Message: {s}')
        # setattr(cls_A, 'bar', bar)

        # Decorator can be written to take normal functions and make them methods
        @add_method(cls_A)
        def foo():
            print('hello world!')

        @add_method(cls_A)
        def bar(s):
            print(f'Message: {s}')



    """
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator

# ==================================================================================================================== #
# Function Attributes Decorators                                                                                       #
# ==================================================================================================================== #

_custom_function_metadata_attribute_names = dict(short_name=None, tags=None, creation_date=None,
                                         input_requires=None, output_provides=None,
                                         uses=None, used_by=None,
                                         related_items=None, # references to items related to this definition
                                         conforms_to=None, is_global=False, validate_computation_test=None,
                                         requires_global_keys=None, provides_global_keys=None,
)



def function_attributes(short_name=None, tags=None, creation_date=None, input_requires=None, output_provides=None, uses=None, used_by=None, related_items=None, conforms_to=None, is_global:bool=False, validate_computation_test:Optional[Callable]=None, requires_global_keys=None, provides_global_keys=None, **kwargs):
    """Adds function attributes to a function or class

    ```python
        from pyphocorehelpers.function_helpers import function_attributes

        @function_attributes(short_name='pf_dt_sequential_surprise', tags=['tag1','tag2'], input_requires=[], output_provides=[], uses=[], used_by=[], related_items=[])
        def _perform_time_dependent_pf_sequential_surprise_computation(computation_result, debug_print=False):
            # function body
            
        
    ```

    func.short_name, func.tags, func.creation_date, func.input_requires, func.output_provides, func.uses, func.used_by, func.related_items, func.conforms_to, func.is_global, func.validate_computation_test
    """
    def decorator(func):
        func.short_name = short_name
        func.tags = tags
        func.creation_date = creation_date
        func.input_requires = input_requires
        func.output_provides = output_provides
        func.uses = uses
        func.used_by = used_by
        func.related_items = related_items
        func.conforms_to = conforms_to
        func.is_global = is_global
        func.validate_computation_test = validate_computation_test
        func.requires_global_keys = requires_global_keys
        func.provides_global_keys = provides_global_keys
        for k, v in kwargs.items():
            setattr(func, k, v)
        return func
    return decorator


def get_decorated_function_attributes(obj) -> Dict:
    """ returns the `function_attributes` metadata from a function or method is decorated with the `function_attributes` decorator """
    known_key_names = list(_custom_function_metadata_attribute_names.keys())
    _fcn_values_dict = {}
    for k in known_key_names:
        if hasattr(obj, k):
            _fcn_values_dict[k] = getattr(obj, k)
    return _fcn_values_dict


def is_decorated_with_function_attributes(obj) -> bool:
    """ returns True if the function or method is decorated with the metadata consistent with a `function_attributes` decorator """
    known_key_names = list(_custom_function_metadata_attribute_names.keys())
    for k in known_key_names:
        if hasattr(obj, k):
            return True
    return False # had no attributes
    # return hasattr(obj, 'short_name') or hasattr(obj, 'tags') or hasattr(obj, 'creation_date') or hasattr(obj, 'input_requires') or hasattr(obj, 'output_provides')

    
def fn_best_name(a_fn) -> str:
    """ returns the .short_name if the function is decorated with one, otherwise returns the functions name
    from pyphocorehelpers.function_helpers import fn_best_name
    {k:fn_best_name(v) for k, v in curr_active_pipeline.registered_merged_computation_function_dict.items()}
    
    """
    # _comp_specifier.short_name
    return get_decorated_function_attributes(a_fn).get('short_name', a_fn.__name__)


def invocation_log(func):
    """Logs before and after calling a function
    https://towardsdatascience.com/why-you-should-wrap-decorators-in-python-5ac3676835f9
    Args:
        func (_type_): _description_

    Returns:
        _type_: _description_

    Usage:

    @invocation_log
    def say_hello(name):
        '''Say hello to someone'''
        print(f"Hello, {name}!")

    """
    @wraps(func)
    def inner_func(*args, **kwargs):
        """Inner function within the invocation_log"""
        print(f'Before Calling {func.__name__}')
        func(*args, **kwargs)
        print(f'After Calling {func.__name__}')

    return inner_func




def get_fn_kwargs_with_defaults(func: Callable, ignore_kwarg_names: Optional[List[str]]=None) -> Dict[str, Any]:
    """
    Extracts keyword arguments with default values from a function, optionally ignoring specified arguments.

    :param func: The function object to inspect.
    :param ignore_kwarg_names: Optional list of keyword argument names to ignore.
    :return: Dictionary mapping keyword argument names to their default values.
    
    Usage:
    
        from pyphocorehelpers.function_helpers import get_fn_kwargs_with_defaults

        ignore_kwarg_names = ['include_includelist', 'debug_print']
        registered_merged_computation_function_default_kwargs_dict = {k:get_fn_kwargs_with_defaults(v, ignore_kwarg_names=ignore_kwarg_names) for k, v in curr_active_pipeline.registered_merged_computation_function_dict.items()}
        registered_merged_computation_function_default_kwargs_dict
    """
    import inspect
    from inspect import Parameter
    # Get the signature of the function
    sig = inspect.signature(func)
    # Initialize the dictionary to hold keyword arguments with defaults
    kwargs_with_defaults = {}
    
    # Convert ignore list to a set for efficiency
    if ignore_kwarg_names is not None:
        ignore_kwarg_names = set(ignore_kwarg_names)
    else:
        ignore_kwarg_names = set()
    
    for param in sig.parameters.values():
        # Determine if parameter has a default value
        has_default = param.default is not Parameter.empty
        # Determine if parameter is a keyword argument
        is_kwarg = (param.kind == Parameter.KEYWORD_ONLY or
                    param.kind == Parameter.POSITIONAL_OR_KEYWORD)
        # Determine if parameter should be ignored
        is_ignored = param.name in ignore_kwarg_names
        # Add to dictionary if conditions are met
        if has_default and is_kwarg and not is_ignored:
            kwargs_with_defaults[param.name] = param.default
    return kwargs_with_defaults