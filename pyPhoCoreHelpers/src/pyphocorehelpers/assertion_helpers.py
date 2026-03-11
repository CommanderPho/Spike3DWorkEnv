import traceback
import warnings
from contextlib import contextmanager
from typing import Dict, List, Tuple, Optional, Callable, Union, Any
import nptyping as ND
from nptyping import NDArray
import numpy as np
import pandas as pd
from pyphocorehelpers.indexing_helpers import get_variable_shape, safe_get_variable_shape

class Assert:
    """ Convenince assertion helpers that print out the value that causes the assertion along with a reasonable message instead of showing nothing
    
    
    from pyphocorehelpers.assertion_helpers import Assert
        
        
    """
    # Controls whether failed assertions raise or only warn and continue
    _warn_only: bool = False

    class AssertionWarning(UserWarning):
        pass

    @classmethod
    def set_warn_only(cls, warn_only: bool = True) -> None:
        """Enable/disable warn-only mode.

        When warn-only is True, failed checks emit a warning and continue instead of raising.
        """
        cls._warn_only = warn_only

    @classmethod
    @contextmanager
    def temporarily_warn_only(cls):
        """Context manager to temporarily enable warn-only mode.

        Usage:
            with Assert.temporarily_warn_only():
                Assert.same_length(a, b)
        """
        prev = cls._warn_only
        try:
            cls._warn_only = True
            yield
        finally:
            cls._warn_only = prev

    @classmethod
    def _handle_assertion(cls, condition: bool, message) -> None:
        """Internal handler that either raises an AssertionError or emits a warning.

        Accepts a string or a zero-arg callable for lazy message evaluation.
        """
        if condition:
            return
        # compute message lazily if a callable was provided
        try:
            computed_message = message() if callable(message) else message
        except Exception as e:
            computed_message = f"<failed to compute assertion message: {e}>"
        if cls._warn_only:
            warnings.warn(computed_message, category=cls.AssertionWarning, stacklevel=3)
        else:
            raise AssertionError(computed_message)
    @classmethod
    def path_exists(cls, path):
        """
        # Usage:
            Assert.path_exists(global_batch_result_inst_fr_file_path)
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        # Extract the variable name from the caller's local variables
        var_name = [name for name, val in frame.f_locals.items() if val is path]
        # Use the first matched variable name or 'unknown' if not found
        var_name = var_name[0] if var_name else 'unknown'
        
        cls._handle_assertion(path.exists(), f"{var_name} does not exist! {var_name}: '{path}'") # Perform the assertion with detailed error message
        


    # ==================================================================================================================================================================================================================================================================================== #
    # Binary Comparisons                                                                                                                                                                                                                                                                   #
    # ==================================================================================================================================================================================================================================================================================== #
    @classmethod
    def not_None(cls, *args):
        """ Ensures all passed *args are non-None, if it fails, it prints the actual values of each arg.
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        
        var_name_dict = {}
        n_unknown_variables: int = 0
            
        for a_equal_checkable_var in args:
            # Extract the variable name from the caller's local variables
            var_name = [name for name, val in frame.f_locals.items() if val is a_equal_checkable_var]
            # Use the first matched variable name or 'unknown' if not found
            if var_name: 
                var_name = var_name[0] 
            else:
                var_name = f'unknown[{n_unknown_variables}]' # var_name = var_name[0] if var_name else 'unknown'
                n_unknown_variables += 1 ## increment    
                
            if var_name not in var_name_dict:
                var_name_dict[var_name] = a_equal_checkable_var ## turn into dictionary
            else:
                raise NotImplementedError(f'have same name! var_name: "{var_name}", var_name_dict: {var_name_dict}')            

        ## END for a_equal_checkab...
            
        if len(var_name_dict) == 0:
            # return True # empty arrays are all equal
            pass
        elif len(var_name_dict) == 1:
            # if only a single array, make sure it's not accidentally passed in incorrect
            reference_var = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            return (reference_var is not None)
        else:
            ## It has more than two elements:
            values_dict = {k:v for k, v in var_name_dict.items()}
            for var_name, a_val in values_dict.items():
                if a_val is None:
                    cls._handle_assertion((a_val is None), f"{var_name} must be non-None but instead {var_name}: {a_val}.\nvalues_dict: {values_dict}\n{var_name}: {a_val}\n") # Perform the assertion with detailed error message


    @classmethod
    def is_None(cls, *args):
        """ Ensures all passed *args are equal in value, if it fails, it prints the actual values of each arg.
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        
        var_name_dict = {}
        n_unknown_variables: int = 0
            
        for a_equal_checkable_var in args:
            # Extract the variable name from the caller's local variables
            var_name = [name for name, val in frame.f_locals.items() if val is a_equal_checkable_var]
            # Use the first matched variable name or 'unknown' if not found
            if var_name: 
                var_name = var_name[0] 
            else:
                var_name = f'unknown[{n_unknown_variables}]' # var_name = var_name[0] if var_name else 'unknown'
                n_unknown_variables += 1 ## increment    
                
            if var_name not in var_name_dict:
                var_name_dict[var_name] = a_equal_checkable_var ## turn into dictionary
            else:
                raise NotImplementedError(f'have same name! var_name: "{var_name}", var_name_dict: {var_name_dict}')            

        ## END for a_equal_checkab...
            
        if len(var_name_dict) == 0:
            # return True # empty arrays are all equal
            pass
        elif len(var_name_dict) == 1:
            # if only a single array, make sure it's not accidentally passed in incorrect
            reference_var = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            return (reference_var is not None)
        else:
            ## It has more than two elements:
            values_dict = {k:v for k, v in var_name_dict.items()}
            for var_name, a_val in values_dict.items():
                if a_val is not None:
                    cls._handle_assertion((a_val is not None), f"{var_name} must be None but instead {var_name}: {a_val}.\nvalues_dict: {values_dict}\n{var_name}: {a_val}\n") # Perform the assertion with detailed error message



    # ==================================================================================================================================================================================================================================================================================== #
    # Iterables                                                                                                                                                                                                                                                                            #
    # ==================================================================================================================================================================================================================================================================================== #
    @classmethod
    def all_equal(cls, *args):
        """ Ensures all passed *args are equal in value, if it fails, it prints the actual values of each arg.
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        
        var_name_dict = {}
        # var_names_list = [name for name, val in frame.f_locals.items()]
        
        n_unknown_variables: int = 0
            
        for a_equal_checkable_var in args:
            # Extract the variable name from the caller's local variables
            var_name = [name for name, val in frame.f_locals.items() if val is a_equal_checkable_var]
            # Use the first matched variable name or 'unknown' if not found
            if var_name: 
                var_name = var_name[0] 
            else:
                var_name = f'unknown[{n_unknown_variables}]' # var_name = var_name[0] if var_name else 'unknown'
                n_unknown_variables += 1 ## increment
                
            if var_name not in var_name_dict:
                var_name_dict[var_name] = a_equal_checkable_var ## turn into dictionary
            
            # assert var_name not in var_name_dict, f"var_name: {var_name} already exists in var_name_dict: {var_name_dict}"            
            # ## could append suffix like "f{var_name}[1]"
            # var_name_dict[var_name] = a_equal_checkable_var ## turn into dictionary
        ## END for a_equal_checkab...
        
        if len(var_name_dict) == 0:
            # return True # empty arrays are all equal
            pass
        elif len(var_name_dict) == 1:
            # if only a single array, make sure it's not accidentally passed in incorrect
            reference_var = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            # assert isinstance(reference_array, (np.ndarray))
            # assert hasattr(reference_var, 'len')
            # return True # as long as imput is intended, always True
            pass
        else:
            ## It has more than two elements:
            reference_var = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            reference_val: Any = reference_var
            values_dict = {k:v for k, v in var_name_dict.items()}
            for var_name, a_val in values_dict.items():
                if a_val != reference_val:
                    cls._handle_assertion((a_val == reference_val), f"{var_name} must be == {reference_val} but instead {var_name}: {a_val}.\nvalues_dict: {values_dict}\n{var_name}: {a_val}\n") # Perform the assertion with detailed error message
            # Check equivalence for each array in the list
            # return np.all([pairwise_numpy_fn(reference_array, an_arr, **kwargs) for an_arr in list_of_arrays[1:]]) # can be used without the list comprehension just as a generator if you use all(...) instead.
            # return all(np.all(np.array_equiv(reference_array, an_arr) for an_arr in list_of_arrays[1:])) # the outer 'all(...)' is required, otherwise it returns a generator object like: `<generator object NumpyHelpers.all_array_equiv.<locals>.<genexpr> at 0x00000128E0482AC0>`


    @classmethod
    def len_equals(cls, arr_or_list, required_length: int):
        """ Ensures the length is equal to the required_length (a specific length), if it fails, it prints the actual length
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        # Extract the variable name from the caller's local variables
        var_name = [name for name, val in frame.f_locals.items() if val is arr_or_list]
        # Use the first matched variable name or 'unknown' if not found
        var_name = var_name[0] if var_name else 'unknown'

        cls._handle_assertion((len(arr_or_list) == required_length), f"{var_name} must be of length {required_length} but instead len({var_name}): {len(arr_or_list)}.\n{var_name}: {arr_or_list}\n") # Perform the assertion with detailed error message

    @classmethod
    def same_length(cls, *args):
        """ Ensures all passed *args are the same length (according to len(...), if it fails, it prints the actual length of each arg.
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        
        var_name_dict = {}
        for arr_or_list in args:
            # Extract the variable name from the caller's local variables
            var_name = [name for name, val in frame.f_locals.items() if val is arr_or_list]
            # Use the first matched variable name or 'unknown' if not found
            var_name = var_name[0] if var_name else 'unknown'
            cls._handle_assertion(var_name not in var_name_dict, f"var_name: {var_name} already exists in var_name_dict: {var_name_dict}")
            ## could append suffix like "f{var_name}[1]"
            var_name_dict[var_name] = arr_or_list ## turn into dictionary
            
        if len(var_name_dict) == 0:
            # return True # empty arrays are all equal
            pass
        elif len(var_name_dict) == 1:
            # if only a single array, make sure it's not accidentally passed in incorrect
            reference_array = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            # assert isinstance(reference_array, (np.ndarray))
            cls._handle_assertion(hasattr(reference_array, 'len'), f"reference_array must have attribute 'len', got type: {type(reference_array)}")
            # return True # as long as imput is intended, always True
            pass        
        else:
            ## It has more than two elements:
            reference_array = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            reference_len: int = len(reference_array)
            lengths_dict = {k:len(v) for k, v in var_name_dict.items()}
            for var_name, a_len in lengths_dict.items():
                if a_len != reference_len:
                    cls._handle_assertion((a_len == reference_len), f"{var_name} must be of length {reference_len} but instead len({var_name}): {a_len}.\nreference_lengths: {lengths_dict}\n{var_name}: {arr_or_list}\n") # Perform the assertion with detailed error message
            # Check equivalence for each array in the list
            # return np.all([pairwise_numpy_fn(reference_array, an_arr, **kwargs) for an_arr in list_of_arrays[1:]]) # can be used without the list comprehension just as a generator if you use all(...) instead.
            # return all(np.all(np.array_equiv(reference_array, an_arr) for an_arr in list_of_arrays[1:])) # the outer 'all(...)' is required, otherwise it returns a generator object like: `<generator object NumpyHelpers.all_array_equiv.<locals>.<genexpr> at 0x00000128E0482AC0>`

    @classmethod
    def shape_equals(cls, arr_or_list, required_shape: Union[Tuple[int], int]):
        """ Ensures the length is equal to the required_length, if it fails, it prints the actual length
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        # Extract the variable name from the caller's local variables
        var_name = [name for name, val in frame.f_locals.items() if val is arr_or_list]
        # Use the first matched variable name or 'unknown' if not found
        var_name = var_name[0] if var_name else 'unknown'
        cls._handle_assertion(np.alltrue(get_variable_shape(arr_or_list) == required_shape), f"{var_name} must be of length {required_shape} but instead len({var_name}): {len(arr_or_list)}.\n{var_name}: {arr_or_list}\n") # Perform the assertion with detailed error message

    @classmethod
    def same_shape(cls, *args):
        """ Ensures all passed *args are the same length (according to len(...), if it fails, it prints the actual length of each arg.
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        
        var_name_dict = {}
        for arr_or_list in args:
            # Extract the variable name from the caller's local variables
            var_name = [name for name, val in frame.f_locals.items() if val is arr_or_list]
            # Use the first matched variable name or 'unknown' if not found
            var_name = var_name[0] if var_name else 'unknown'
            cls._handle_assertion(var_name not in var_name_dict, f"var_name: {var_name} already exists in var_name_dict: {var_name_dict}")
            ## could append suffix like "f{var_name}[1]"
            var_name_dict[var_name] = arr_or_list ## turn into dictionary
            
        if len(var_name_dict) == 0:
            # return True # empty arrays are all equal
            pass
        elif len(var_name_dict) == 1:
            # if only a single array, make sure it's not accidentally passed in incorrect
            reference_array = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            # assert isinstance(reference_array, (np.ndarray))
            a_shape = get_variable_shape(reference_array, should_fail_when_cannot_determine=True)
            cls._handle_assertion(a_shape is not None, f"Could not determine shape for variable: {reference_array}")
            # return True # as long as imput is intended, always True
            pass        
        else:
            ## It has more than two elements:
            reference_array = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
            reference_shape: int = get_variable_shape(reference_array, should_fail_when_cannot_determine=True)
            shapes_dict = {k:get_variable_shape(v, should_fail_when_cannot_determine=True) for k, v in var_name_dict.items()}
            for var_name, a_shape in shapes_dict.items():
                if np.alltrue(a_shape == reference_shape):
                # if a_shape != reference_shape:
                    cls._handle_assertion((a_shape == reference_shape), f"{var_name} must be of shape {reference_shape} but instead shape({var_name}): {a_shape}.\nreference_lengths: {shapes_dict}\n{var_name}: {arr_or_list}\n") # Perform the assertion with detailed error message
            # Check equivalence for each array in the list
            # return np.all([pairwise_numpy_fn(reference_array, an_arr, **kwargs) for an_arr in list_of_arrays[1:]]) # can be used without the list comprehension just as a generator if you use all(...) instead.
            # return all(np.all(np.array_equiv(reference_array, an_arr) for an_arr in list_of_arrays[1:])) # the outer 'all(...)' is required, otherwise it returns a generator object like: `<generator object NumpyHelpers.all_array_equiv.<locals>.<genexpr> at 0x00000128E0482AC0>`


    @classmethod
    def all_are_not_None(cls, *args):
        """ Ensures all passed *args are non-None, if it fails, it prints the actual values of each arg.
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        
        var_name_dict = {}
        n_unknown_variables: int = 0
            
        for an_equal_checkable_var in args:
            # Extract the variable name from the caller's local variables
            var_name = [name for name, val in frame.f_locals.items() if val is an_equal_checkable_var]
            # Use the first matched variable name or 'unknown' if not found
            if var_name: 
                var_name = var_name[0] 
            else:
                var_name = f'unknown[{n_unknown_variables}]' # var_name = var_name[0] if var_name else 'unknown'
                n_unknown_variables += 1 ## increment    
                
            if var_name not in var_name_dict:
                var_name_dict[var_name] = an_equal_checkable_var ## turn into dictionary
            else:
                raise NotImplementedError(f'have same name! var_name: "{var_name}", var_name_dict: {var_name_dict}')            

        ## END for a_equal_checkab...
            
        if len(var_name_dict) == 0:
            # return True # empty arrays are all equal
            pass
        # elif len(var_name_dict) == 1:
        #     # if only a single array, make sure it's not accidentally passed in incorrect
        #     reference_var = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
        #     assert (reference_var is not None), f"{var_name} must be non-None but instead {var_name}: {a_val}.\nvalues_dict: {values_dict}\n{var_name}: {a_val}\n"
        else:
            ## It has more than two elements:
            values_dict = {k:v for k, v in var_name_dict.items()}
            for var_name, a_val in values_dict.items():
                if (a_val is None):
                    cls._handle_assertion((a_val is None), f"{var_name} must be non-None but instead {var_name}: {a_val}.\nvalues_dict: {values_dict}\n{var_name}: {a_val}\n") # Perform the assertion with detailed error message


    @classmethod
    def all_are_None(cls, *args):
        """ Ensures all passed *args are None, if it fails, it prints the actual values of each arg.
        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        
        var_name_dict = {}
        n_unknown_variables: int = 0
            
        for a_equal_checkable_var in args:
            # Extract the variable name from the caller's local variables
            var_name = [name for name, val in frame.f_locals.items() if val is a_equal_checkable_var]
            # Use the first matched variable name or 'unknown' if not found
            if var_name: 
                var_name = var_name[0] 
            else:
                var_name = f'unknown[{n_unknown_variables}]' # var_name = var_name[0] if var_name else 'unknown'
                n_unknown_variables += 1 ## increment    
                
            if var_name not in var_name_dict:
                var_name_dict[var_name] = a_equal_checkable_var ## turn into dictionary
            else:
                raise NotImplementedError(f'have same name! var_name: "{var_name}", var_name_dict: {var_name_dict}')            

        ## END for a_equal_checkab...
            
        if len(var_name_dict) == 0:
            # return True # empty arrays are all equal
            pass
        # elif len(var_name_dict) == 1:
        #     # if only a single array, make sure it's not accidentally passed in incorrect
        #     reference_var = list(var_name_dict.values())[0] # Use the first array as a reference for comparison
        #     assert (reference_var is not None)
        else:
            ## It has more than two elements:
            values_dict = {k:v for k, v in var_name_dict.items()}
            for var_name, a_val in values_dict.items():
                if a_val is not None:
                    cls._handle_assertion((a_val is not None), f"{var_name} must be None but instead {var_name}: {a_val}.\nvalues_dict: {values_dict}\n{var_name}: {a_val}\n") # Perform the assertion with detailed error message


    @classmethod
    def is_in(cls, curr_variable_value: Any, allowed_variable_list: List):
        """ Ensures the element is in the required literal list, if it fails, it prints the actual value and the available values

        Usage:
            Assert.is_in(self.posterior_variable_to_render, allowed_variable_list=['p_x_given_n', 'p_x_given_n_and_x_prev'])

        """
        import inspect
        # Get the caller's frame
        frame = inspect.currentframe().f_back
        # Extract the variable name from the caller's local variables
        var_name = [name for name, val in frame.f_locals.items() if val is curr_variable_value]
        # Use the first matched variable name or 'unknown' if not found
        var_name: str = var_name[0] if var_name else 'unknown'
        cls._handle_assertion(curr_variable_value in allowed_variable_list, f"{var_name} not in allowed list: {allowed_variable_list} but instead {var_name} ={curr_variable_value}.\n{var_name}: {curr_variable_value}\n")



    # ==================================================================================================================================================================================================================================================================================== #
    # Dataframes                                                                                                                                                                                                                                                                           #
    # ==================================================================================================================================================================================================================================================================================== #
    @classmethod
    def require_columns(cls, dfs: Union[pd.DataFrame, List[pd.DataFrame], Dict[Any, pd.DataFrame]], required_columns: List[str]) -> bool:
        """
        Check if all DataFrames in the given container have the required columns.
        
        Parameters:
            dfs: A container that may be a single DataFrame, a list/tuple of DataFrames, or a dictionary with DataFrames as values.
            required_columns: A list of column names that are required to be present in each DataFrame.
            print_changes: If True, prints the columns that are missing from each DataFrame.
        
        Returns:
            True if all DataFrames contain all the required columns, otherwise False.

        Usage:

            required_cols = ['missing_column', 'congruent_dir_bins_ratio', 'coverage', 'direction_change_bin_ratio', 'jump', 'laplacian_smoothness', 'longest_sequence_length', 'longest_sequence_length_ratio', 'monotonicity_score', 'sequential_correlation', 'total_congruent_direction_change', 'travel'] # Replace with actual column names you require
            has_required_columns = PandasHelpers.require_columns({a_name:a_result.filter_epochs for a_name, a_result in filtered_decoder_filter_epochs_decoder_result_dict.items()}, required_cols, print_missing_columns=True)
            has_required_columns
            


        """
        from neuropy.utils.indexing_helpers import PandasHelpers

        all_have_all_required_columns, debug_tuple = PandasHelpers.check_columns(dfs=dfs, required_columns=required_columns, return_only_dfs_missing_columns=True)
        # missing_columns, all_have_all_required_columns = PandasHelpers.check_columns(dfs=dfs, required_columns=required_columns, print_missing_columns=True)
        
        cls._handle_assertion(
            all_have_all_required_columns,
            lambda: (
                "Missing required columns; details unavailable."
                if debug_tuple is None
                else f"num_missing_columns: {debug_tuple[0]}, missing_columns: {debug_tuple[1]}, found_columns: {debug_tuple[2]}, all_df_columns: {debug_tuple[3]}"
            ),
        )

        # if not all_have_all_required_columns:
        #     ## missing some columns
        #     assert debug_tuple is not None
        #     num_missing_columns, missing_columns, found_columns, all_df_columns = debug_tuple
        #     raise ValueError(f'num_missing_columns: {num_missing_columns}, missing_columns: {missing_columns}, found_columns: {found_columns}, all_df_columns: {all_df_columns} ')

        # has_all_columns: bool = PandasHelpers.require_columns(dfs=dfs, required_columns=required_columns, print_missing_columns=True)
        # assert has_all_columns
        
        # has_all_columns: bool = PandasHelpers.require_columns(dfs=dfs, required_columns=required_columns, print_missing_columns=True)
        # assert has_all_columns
        
             

    # @classmethod
    # def _helper_all_array_generic(cls, pairwise_numpy_fn, list_of_arrays: List[NDArray], **kwargs) -> bool:
    #     """ A n-element generalization of a specified pairwise numpy function such as `np.array_equiv`
    #     Usage:
        
    #         list_of_arrays = list(xbins.values())
    #         NumpyHelpers._helper_all_array_generic(list_of_arrays=list_of_arrays)

    #     """
    #     # Input type checking
    #     if not np.all(isinstance(arr, np.ndarray) for arr in list_of_arrays):
    #         raise ValueError("All elements in 'list_of_arrays' must be NumPy arrays.")        
    
    #     if len(list_of_arrays) == 0:
    #         return True # empty arrays are all equal
    #     elif len(list_of_arrays) == 1:
    #         # if only a single array, make sure it's not accidentally passed in incorrect
    #         reference_array = list_of_arrays[0] # Use the first array as a reference for comparison
    #         assert isinstance(reference_array, np.ndarray)
    #         return True # as long as imput is intended, always True
        
    #     else:
    #         ## It has more than two elements:
    #         reference_array = list_of_arrays[0] # Use the first array as a reference for comparison
    #         # Check equivalence for each array in the list
    #         return np.all([pairwise_numpy_fn(reference_array, an_arr, **kwargs) for an_arr in list_of_arrays[1:]]) # can be used without the list comprehension just as a generator if you use all(...) instead.
    #         # return all(np.all(np.array_equiv(reference_array, an_arr) for an_arr in list_of_arrays[1:])) # the outer 'all(...)' is required, otherwise it returns a generator object like: `<generator object NumpyHelpers.all_array_equiv.<locals>.<genexpr> at 0x00000128E0482AC0>`


    # @classmethod
    # def all_array_equal(cls, list_of_arrays: List[NDArray], equal_nan=True) -> bool:
    #     """ A n-element generalization of `np.array_equal`
    #     Usage:
        
    #         list_of_arrays = list(xbins.values())
    #         NumpyHelpers.all_array_equal(list_of_arrays=list_of_arrays)

    #     """
    #     return cls._helper_all_array_generic(np.array_equal, list_of_arrays=list_of_arrays, equal_nan=equal_nan)
    
    # @classmethod
    # def all_array_equiv(cls, list_of_arrays: List[NDArray]) -> bool:
    #     """ A n-element generalization of `np.array_equiv`
    #     Usage:
        
    #         list_of_arrays = list(xbins.values())
    #         NumpyHelpers.all_array_equiv(list_of_arrays=list_of_arrays)

    #     """
    #     return cls._helper_all_array_generic(np.array_equiv, list_of_arrays=list_of_arrays)


    # @classmethod
    # def all_allclose(cls, list_of_arrays: List[NDArray], rtol:float=1.e-5, atol:float=1.e-8, equal_nan:bool=True) -> bool:
    #     """ A n-element generalization of `np.allclose`
    #     Usage:
        
    #         list_of_arrays = list(xbins.values())
    #         NumpyHelpers.all_allclose(list_of_arrays=list_of_arrays)

    #     """
    #     return cls._helper_all_array_generic(np.allclose, list_of_arrays=list_of_arrays, rtol=rtol, atol=atol, equal_nan=equal_nan)
    
    
