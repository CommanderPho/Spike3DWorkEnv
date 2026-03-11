from contextlib import contextmanager
from typing import Callable, List, Dict, Tuple, Optional, OrderedDict  # for OrderedMeta
from collections import namedtuple # used in `_try_parse_to_dictionary_if_needed`
import sys # needed for `is_reloaded_instance`
from enum import Enum
from enum import unique # GeneratedClassDefinitionType
from pyphocorehelpers.DataStructure.enum_helpers import ExtendedEnum # required for GeneratedClassDefinitionType

import re # for CodeConversion
import numpy as np # for CodeConversion
import pandas as pd
from neuropy.utils.mixins.dict_representable import overriding_dict_with # required for safely_accepts_kwargs
from pyphocorehelpers.programming_helpers import inspect_callable_arguments


"""

## Pho Programming Helpers:
import inspect
from pyphocorehelpers.general_helpers import inspect_callable_arguments, get_arguments_as_optional_dict, GeneratedClassDefinitionType, CodeConversion
from pyphocorehelpers.print_helpers import DocumentationFilePrinter, TypePrintMode, print_keys_if_possible, debug_dump_object_member_shapes, print_value_overview_only, document_active_variables

"""

class OrderedMeta(type):
    """Replaces the inheriting object's dict of attributes with an OrderedDict that preserves enumeration order
    Reference: https://stackoverflow.com/questions/11296010/iterate-through-class-members-in-order-of-their-declaration
    Usage:
        # Set the metaclass property of your custom class to OrderedMeta
        class Person(metaclass=OrderedMeta):
            name = None
            date_of_birth = None
            nationality = None
            gender = None
            address = None
            comment = None

        # Can then enumerate members while preserving order
        for member in Person._orderedKeys:
            if not getattr(Person, member):
                print(member)
    """

    @classmethod
    def __prepare__(metacls, name, bases):
        return OrderedDict()

    def __new__(cls, name, bases, clsdict):
        c = type.__new__(cls, name, bases, clsdict)
        c._orderedKeys = clsdict.keys()
        return c


def safely_accepts_kwargs(fn):
    """ builds a wrapped version of fn that only takes the kwargs that it can use, and shrugs the rest off (without any warning that they're unused, making it a bit dangerous)
    Can be used as a decorator to make any function gracefully accept unhandled kwargs

    Can be used to conceptually "splat" a configuration dictionary of properties against a function that only uses a subset of them, such as might need to be done for plotting, etc)

    Usage:
        @safely_accepts_kwargs
        def _test_fn_with_limited_parameters(item1=None, item2='', item3=5.0):
            print(f'item1={item1}, item2={item2}, item3={item3}')


    TODO: Tests:
        from pyphocorehelpers.general_helpers import safely_accepts_kwargs

        # def _test_fn_with_limited_parameters(newitem, item1=None, item2='', item3=5.0):
        #     print(f'item1={item1}, item2={item2}, item3={item3}')

        @safely_accepts_kwargs
        def _test_fn_with_limited_parameters(item1=None, item2='', item3=5.0):
            print(f'item1={item1}, item2={item2}, item3={item3}')

        @safely_accepts_kwargs
        def _test_fn2_with_limited_parameters(itemA=None, itemB='', itemC=5.0):
            print(f'itemA={itemA}, itemB={itemB}, itemC={itemC}')

        def _test_outer_fn(**kwargs):
            _test_fn_with_limited_parameters(**kwargs)
            _test_fn2_with_limited_parameters(**kwargs)
            # _test_fn_with_limited_parameters(**overriding_dict_with(lhs_dict=fn_spec_default_arg_dict, **kwargs))
            # _test_fn2_with_limited_parameters(**overriding_dict_with(lhs_dict=fn_spec_default_arg_dict, **kwargs))

            # Build safe versions of the functions
            # _safe_test_fn_with_limited_parameters = _build_safe_kwargs(_test_fn_with_limited_parameters)
            # _safe_test_fn2_with_limited_parameters = _build_safe_kwargs(_test_fn2_with_limited_parameters)
            # Call the safe versions:
            # _safe_test_fn_with_limited_parameters(**kwargs)
            # _safe_test_fn2_with_limited_parameters(**kwargs)


        # _test_outer_fn()
        _test_outer_fn(itemB=15) # TypeError: _test_fn_with_limited_parameters() got an unexpected keyword argument 'itemB'

    """
    full_fn_spec, positional_args_names, kwargs_names, default_kwargs_dict = inspect_callable_arguments(fn)
    def _safe_kwargs_fn(*args, **kwargs):
        return fn(*args, **overriding_dict_with(lhs_dict=default_kwargs_dict, **kwargs))
    return _safe_kwargs_fn



# def get_arguments_as_passthrough(**kwargs):




# Enum for size units
class SIZE_UNIT(Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4

def convert_unit(size_in_bytes, unit: SIZE_UNIT):
    """ Convert the size from bytes to other units like KB, MB or GB"""
    if unit == SIZE_UNIT.KB:
        return size_in_bytes/1024
    elif unit == SIZE_UNIT.MB:
        return size_in_bytes/(1024*1024)
    elif unit == SIZE_UNIT.GB:
        return size_in_bytes/(1024*1024*1024)
    else:
        return size_in_bytes


# @metadata_attributes(short_name=None, tags=['contextmanager'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2023-07-05 19:02', related_items=[])
@contextmanager
def disable_function_context(obj, fn_name: str):
    """ Disables a function within a context manager


    https://stackoverflow.com/questions/10388411/possible-to-globally-replace-a-function-with-a-context-manager-in-python

    Could be used for plt.show().
    ```python

    from pyphocorehelpers.general_helpers import disable_function_context
    import matplotlib.pyplot as plt
    with disable_function_context(plt, "show"):
        run_me(x)
    ```



    """
    temp = getattr(obj, fn_name)
    setattr(obj, fn_name, (lambda: None)) # should I add *args, **kwargs to lambda?
    yield
    setattr(obj, fn_name, temp)



# from dataclasses import dataclass


# @dataclass
# class LoadBuildSave(object):
#     """TODO 2023-04-11 - UNFINISHED
#         Tries to load the object from file first
#         If this isn't possible it runs something to compute it
#         Then it saves it so it can be loaded in the future.

#         Combines the code to perform this common procedure in a concise structure instead of requiring it to be spread out over several places.


#     Example 0: from `pyphoplacecellanalysis.General.Batch.NonInteractiveProcessing.batch_extended_computations`

# ```python
#         try:
#             ## Get global 'jonathan_firing_rate_analysis' results:
#             curr_jonathan_firing_rate_analysis = curr_active_pipeline.global_computation_results.computed_data['jonathan_firing_rate_analysis']
#             neuron_replay_stats_df, rdf, aclu_to_idx, irdf = curr_jonathan_firing_rate_analysis.neuron_replay_stats_df, curr_jonathan_firing_rate_analysis.rdf.rdf, curr_jonathan_firing_rate_analysis.rdf.aclu_to_idx, curr_jonathan_firing_rate_analysis.irdf.irdf
#             if progress_print:
#                 print(f'{_comp_name} already computed.')
#         except (AttributeError, KeyError) as e:
#             if progress_print or debug_print:
#                 print(f'{_comp_name} missing.')
#             if debug_print:
#                 print(f'\t encountered error: {e}\n{traceback.format_exc()}\n.')
#             if progress_print or debug_print:
#                 print(f'\t Recomputing {_comp_name}...')
#             curr_active_pipeline.perform_specific_computation(computation_functions_name_includelist=['_perform_jonathan_replay_firing_rate_analyses'], fail_on_exception=True, debug_print=False) # fail_on_exception MUST be True or error handling is all messed up
#             print(f'\t done.')
#             curr_jonathan_firing_rate_analysis = curr_active_pipeline.global_computation_results.computed_data['jonathan_firing_rate_analysis']
#             neuron_replay_stats_df, rdf, aclu_to_idx, irdf = curr_jonathan_firing_rate_analysis.neuron_replay_stats_df, curr_jonathan_firing_rate_analysis.rdf.rdf, curr_jonathan_firing_rate_analysis.rdf.aclu_to_idx, curr_jonathan_firing_rate_analysis.irdf.irdf
#             newly_computed_values.append(_comp_name)
#         except Exception as e:
#             raise e


#     Example 1: from `pyphoplacecellanalysis.Analysis.Decoder.decoder_result.perform_full_session_leave_one_out_decoding_analysis`
#         # Save to file to cache in case we crash:
#         leave_one_out_surprise_result_pickle_path = output_data_folder.joinpath(f'leave_one_out_surprise_results{cache_suffix}.pkl').resolve()
#         print(f'leave_one_out_surprise_result_pickle_path: {leave_one_out_surprise_result_pickle_path}')
#         saveData(leave_one_out_surprise_result_pickle_path, (active_filter_epochs, original_1D_decoder, all_included_filter_epochs_decoder_result,
#                                                             flat_all_epochs_measured_cell_spike_counts, flat_all_epochs_measured_cell_firing_rates,
#                                                             flat_all_epochs_decoded_epoch_time_bins, flat_all_epochs_computed_surprises, flat_all_epochs_computed_expected_cell_firing_rates,
#                                                             flat_all_epochs_difference_from_expected_cell_spike_counts, flat_all_epochs_difference_from_expected_cell_firing_rates,
#                                                             all_epochs_decoded_epoch_time_bins_mean, all_epochs_computed_cell_surprises_mean, all_epochs_all_cells_computed_surprises_mean))


# ```

#     """
#     property: type



# ==================================================================================================================== #
# UNTESTED                                                                                                             #
# ==================================================================================================================== #

# def is_reloaded_instance(obj, classinfo):
#     """ determines if a class instance is a reloaded instance of a class"""
#     return isinstance(obj, classinfo) and sys.getrefcount(classinfo) > 1



# def get_regular_attrs(obj, include_parent=True):
#     """ Intended to get all of the stored attributes of an object, including those inherited from parent classes, while ignoring @properties and other computed variables
#     Example:
#         class ParentClass:
#             def __init__(self, z):
#                 self.z = z

#         class MyClass(ParentClass):
#             def __init__(self, x):
#                 super().__init__(x+1)
#                 self.x = x
#                 self.y = x + 1

#             @property
#             def computed_prop(self):
#                 return self.x + self.y

#         obj = MyClass(5)
#         regular_attrs = get_regular_attrs(obj)
#         print(regular_attrs)  # Output: ['z', 'x', 'y']


#     ISSUE: returns propery when defined this way

#     @property
#     def pdf_normalized_tuning_curves(self):
#         return Ratemap.perform_AOC_normalization(self.tuning_curves)


#     Usage:
#         get_regular_attrs(ratemap_2D, include_parent=False)

#     """
#     regular_attrs = []
#     cls = type(obj)
#     while cls:
#         for attr in cls.__dict__:
#             if not callable(getattr(obj, attr)) and not attr.startswith('__'):
#                 regular_attrs.append(attr)
#         if not include_parent:
#             break
#         cls = cls.__base__
#     return list(set(regular_attrs))



