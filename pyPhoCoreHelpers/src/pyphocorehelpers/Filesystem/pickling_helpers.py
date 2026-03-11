import sys
import io
import types
# from types import ModuleType
from typing import List, Dict

# import pickle
# import dill
import dill as pickle
import pandas as pd
from pyphocorehelpers.assertion_helpers import Assert
from pathlib import Path

# ==================================================================================================================================================================================================================================================================================== #
# Move modules list is defined in `vscode://file/c:/Users/pho/repos/Spike3DWorkEnv/pyPhoPlaceCellAnalysis/src/pyphoplacecellanalysis/General/Pipeline/Stages/Loading.py:146`                                                                                                           #
# ==================================================================================================================================================================================================================================================================================== #
default_global_move_modules_list = {'pyphoplacecellanalysis.SpecificResults.PhoDiba2023Paper.SingleBarResult':'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.LongShortTrackComputations.SingleBarResult',
    'pyphoplacecellanalysis.SpecificResults.PhoDiba2023Paper.InstantaneousSpikeRateGroupsComputation':'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.LongShortTrackComputations.InstantaneousSpikeRateGroupsComputation',
    'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.DirectionalPlacefieldGlobalComputationFunctions.DirectionalMergedDecodersResult':'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.DirectionalPlacefieldGlobalComputationFunctions.DirectionalPseudo2DDecodersResult',
    'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.DirectionalPlacefieldGlobalComputationFunctions.DirectionalDecodersDecodedResult':'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.DirectionalPlacefieldGlobalComputationFunctions.DirectionalDecodersContinuouslyDecodedResult',
    'pyphocorehelpers.indexing_helpers.BinningInfo':'neuropy.utils.mixins.binning_helpers.BinningInfo',
    'pyphoplacecellanalysis.General.Model.Configs.DynamicConfigs.BaseConfig':'neuropy.core.parameters.BaseConfig',
    'neuropy.core.session.Formats.BaseDataSessionFormats.ParametersContainer':'neuropy.core.parameters.ParametersContainer',
    # 'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions.GeneralDecoderDictDecodedEpochsDictResult': "pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions._DEP_GeneralDecoderDictDecodedEpochsDictResult", # AttributeError: Can't get attribute 'GeneralDecoderDictDecodedEpochsDictResult' on <module 'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions' from 'C:\\Users\\pho\\repos\\Spike3DWorkEnv\\pyPhoPlaceCellAnalysis\\src\\pyphoplacecellanalysis\\General\\Pipeline\\Stages\\ComputationFunctions\\EpochComputationFunctions.py'>
    'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions.NonPBEDimensionalDecodingResult':'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions.DecodingResultND',  # AttributeError: Can't get attribute 'NonPBEDimensionalDecodingResult' on <module 'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions' from 'C:\\Users\\pho\\repos\\Spike3DWorkEnv\\pyPhoPlaceCellAnalysis\\src\\pyphoplacecellanalysis\\General\\Pipeline\\Stages\\ComputationFunctions\\EpochComputationFunctions.py'>
}

# Custom unpickling to remove property 'b'
def remove_property(obj_dict):
    if 'b' in obj_dict:
        del obj_dict['b']
    return obj_dict


class RenameUnpickler(pickle.Unpickler):
    """ 
    # global_move_modules_list: Dict[str, str] - a dict with keys equal to the old full path to a class and values equal to the updated (replacement) full path to the class. Used to update the path to class definitions for loading previously pickled results after refactoring.
        Example: 	{'pyphoplacecellanalysis.SpecificResults.PhoDiba2023Paper.SingleBarResult':'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.LongShortTrackComputations.SingleBarResult',
                    'pyphoplacecellanalysis.SpecificResults.PhoDiba2023Paper.InstantaneousSpikeRateGroupsComputation':'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.MultiContextComputationFunctions.LongShortTrackComputations.InstantaneousSpikeRateGroupsComputation',
                    }

    Usage:
        from pyphocorehelpers.Filesystem.pickling_helpers import RenameUnpickler, renamed_load
    

    pkl_path = curr_active_pipeline.global_computation_results_pickle_path
    with open(pkl_path, 'rb') as dbfile:
        # db = pickle.load(dbfile, **kwargs) # replace previous ` pickle.load(dbfile, **kwargs)` calls with `db = renamed_load(dbfile, **kwargs)`
        db = renamed_load(dbfile, **kwargs)
        
    """
    def find_class(self, module:str, name:str):
        original_full_name:str = '.'.join((module, name))
        renamed_module = module
        assert self._move_modules_list is not None
        
        found_full_replacement_name = self._move_modules_list.get(original_full_name, None)
        found_full_replacement_import_name = None
        if found_full_replacement_name is not None:
            found_full_replacement_module, found_full_replacement_import_name = found_full_replacement_name.rsplit('.', 1)
            renamed_module = found_full_replacement_module
            
        # Pandas 1.5.* -> 2.0.* pickle compatibility:
        # after upgrading Pandas from 1.5.* -> 2.0.* I was getting `ModuleNotFoundError: No module named 'pandas.core.indexes.numeric'` when trying to unpickle the pipeline.
        if module.startswith('pandas.'):
            key = (module, name)
            renamed_module, name = self._pandas_rename_map.get(key, key)
    
        if found_full_replacement_import_name is not None:
            return super(RenameUnpickler, self).find_class(renamed_module, found_full_replacement_import_name) # AttributeError: Can't get attribute '_DEP_GeneralDecoderDictDecodedEpochsDictResult' on <module 'pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions' from 'C:\\Users\\pho\\repos\\Spike3DWorkEnv\\pyPhoPlaceCellAnalysis\\src\\pyphoplacecellanalysis\\General\\Pipeline\\Stages\\ComputationFunctions\\EpochComputationFunctions.py'>
        else:
            return super(RenameUnpickler, self).find_class(renamed_module, name)

    def __init__(self, *args, **kwds):
        # settings = pickle.Pickler.settings
        # _ignore = kwds.pop('ignore', None)
        _move_modules_list = kwds.pop('move_modules_list', None)        
        pickle.Unpickler.__init__(self, *args, **kwds)
        # self._ignore = settings['ignore'] if _ignore is None else _ignore
        # self._move_modules_list = settings['move_modules_list'] if _move_modules_list is None else _move_modules_list
        assert _move_modules_list is not None, f'Requires at least a custom empty move_modules_dict'
        self._move_modules_list = (default_global_move_modules_list | _move_modules_list)
        self._pandas_rename_map = pd.compat.pickle_compat._class_locations_map

def renamed_load(file_obj, move_modules_list:Dict=None, **kwargs):
    """ from pyphocorehelpers.Filesystem.pickling_helpers import renamed_load """
    return RenameUnpickler(file_obj, move_modules_list=move_modules_list, **kwargs).load()

def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)


exclude_modules_list = ['pyphoplacecellanalysis.External.pyqtgraph'] # , 'pyphoplacecellanalysis.External.pyqtgraph.Qt.QtWidgets', 'pyphoplacecellanalysis.External.pyqtgraph.Qt.QtWidgets.QApplication'
exclude_type_names = ["QApplication"]  # Add the type names you want to exclude as strings


class ModuleExcludesPickler(pickle.Pickler):
    """ 
    TypeError: cannot pickle 'QApplication' object
    
    """
    def save_module(self, obj, name=None):
        # Replace 'module_to_exclude' with the actual module name you want to exclude
        # valid_module_to_include: bool = True
        # for a_module_to_exclude in exclude_modules_list:
        #     if a_module_to_exclude in obj.__name__:
        #         valid_module_to_include = False
        #         return
        # if valid_module_to_include:
        #     super().save_module(obj, name)        
        if any(obj.__name__.startswith(excluded_module) for excluded_module in exclude_modules_list):
                return  # Skip pickling this module
        else:
            print(f'ModuleExcludesPickler.save_module(...): obj.__name__: {obj.__name__}')
            super().save_module(obj, name)
                
    # def save(self, obj, save_persistent_id=True):
    #     # Exclude specific types by name
    #     obj_type_name = type(obj).__name__
    #     if obj_type_name in exclude_type_names:
    #         return  # Skip this object
    #     super().save(obj, save_persistent_id)

    def save(self, obj, save_persistent_id=True):
        # Exclude specific modules
        if isinstance(obj, types.ModuleType):
            if any(obj.__name__.startswith(mod) for mod in exclude_modules_list):
                return  # Skip this module
        # Exclude specific types by name
        elif type(obj).__name__ in exclude_type_names:
            return  # Skip this object
        # Handle functions and built-in functions
        elif isinstance(obj, (types.FunctionType, types.BuiltinFunctionType)):
            try:
                super().save(obj, save_persistent_id)
            except pickle.PicklingError as e:
                print(f'WARN: ModuleExcludesPickler.save(...) encountered pickling error: {e}')
                return  # Skip if function cannot be pickled
        else:
            super().save(obj, save_persistent_id)
            

# save_module_dict


def custom_dump(obj, file, protocol=None, byref=None, fmode=None, recurse=None, **kwds):#, strictio=None):
    """
    Pickle an object to a file.

    See :func:`dumps` for keyword arguments.
    """
    from dill.settings import settings
    protocol = settings['protocol'] if protocol is None else int(protocol)
    _kwds = kwds.copy()
    _kwds.update(dict(byref=byref, fmode=fmode, recurse=recurse))
    _exclude_pickler = ModuleExcludesPickler(file, protocol, **_kwds)
    _exclude_pickler.dump(obj)
    return

def custom_dumps(obj, protocol=None, byref=None, fmode=None, recurse=None, **kwds):#, strictio=None):
    """
    Pickle an object to a string.

    *protocol* is the pickler protocol, as defined for Python *pickle*.

    If *byref=True*, then dill behaves a lot more like pickle as certain
    objects (like modules) are pickled by reference as opposed to attempting
    to pickle the object itself.

    If *recurse=True*, then objects referred to in the global dictionary
    are recursively traced and pickled, instead of the default behavior
    of attempting to store the entire global dictionary. This is needed for
    functions defined via *exec()*.

    *fmode* (:const:`HANDLE_FMODE`, :const:`CONTENTS_FMODE`,
    or :const:`FILE_FMODE`) indicates how file handles will be pickled.
    For example, when pickling a data file handle for transfer to a remote
    compute service, *FILE_FMODE* will include the file contents in the
    pickle and cursor position so that a remote method can operate
    transparently on an object with an open file handle.

    Default values for keyword arguments can be set in :mod:`dill.settings`.
    """
    file = io.StringIO()
    custom_dump(obj, file, protocol, byref, fmode, recurse, **kwds)#, strictio)
    return file.getvalue()


# def custom_dump(obj):
#     with open("my_object.pkl", "wb") as file:
#         pickler = ModuleExcludesPickler(file)
#         pickler.dump(obj)



# def custom_dumps(obj):
#     with open("my_object.pkl", "wb") as file:
#         pickler = ModuleExcludesPickler(file)
#         pickler.dump(obj)
        

# @function_attributes(short_name=None, tags=['pickle', 'dill', 'debug', 'tool'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-01-01 00:00', related_items=[])
def diagnose_pickling_issues(object_to_pickle, stop_after_first_problemmatic_attribute: bool=False):
   """Intellegently diagnoses which property on an object is causing pickling via Dill to fail.
   
   Usage:
        import dill as pickle
        from pyphocorehelpers.Filesystem.pickling_helpers import diagnose_pickling_issues

        diagnose_pickling_issues(curr_active_pipeline.global_computation_results.computed_data['RankOrder'])
        diagnose_pickling_issues(v_dict)
   """

   try:
       # Attempt to pickle the object directly
       pickle.dumps(object_to_pickle)
   except pickle.PicklingError as e:
       # If pickling fails, initiate a diagnostic process
       print(f"Pickling error encountered: {e}")

       # Gather information about the object's attributes
       object_attributes = [attr for attr in dir(object_to_pickle) if not attr.startswith("__")]

       # Isolate problematic attributes through iterative testing
       #    problematic_attribute = None
       problematic_attributes = {}
    
       for attribute in object_attributes:
           try:
               pickle.dumps(getattr(object_to_pickle, attribute))
           except pickle.PicklingError:
            #    problematic_attribute = attribute
               problematic_attributes[attribute] = True
               if stop_after_first_problemmatic_attribute:
                   break

       # Provide informative output
       if problematic_attributes:
           print(f"Identified problematic attribute: {problematic_attributes}")
           print("Potential causes:")
           print("- Attribute contains unpicklable data types (e.g., lambda functions, file objects).")
           print("- Attribute refers to external resources (e.g., database connections).")
           print("- Attribute has circular references within the object's structure.")
       else:
           print("Unable to isolate the specific attribute causing the pickling error.")
           print("Consider:")
           print("- Examining the object's structure and dependencies for potential conflicts.")
           print("- Providing a minimal reproducible example for further analysis.")

   else:
       # If pickling succeeds, indicate no issues found
       print("No pickling issues detected.")



def save_split_pickled_obj(obj_to_split, save_root_path: Path, include_includelist=None, debug_print = True):
    """ 
    param_typed_parameters: object to be pickled
    
    Usage:
        from pyphocorehelpers.Filesystem.pickling_helpers import save_split_pickled_obj
        
        save_root_path = Path(r"C:/Users/pho/repos/Spike3DWorkEnv/Spike3D/output").resolve()
        Assert.path_exists(save_root_path)
        split_save_folder, (split_save_paths, split_save_output_types), (succeeded_keys, failed_keys, skipped_keys) = save_split_pickled_obj(param_typed_parameters, save_root_path=save_root_path)
            
    """
    if include_includelist is None:
        ## include all keys if none are specified
        include_includelist = list(obj_to_split.__dict__.keys())
        
    if debug_print:
        print(f'include_includelist: {include_includelist}')

    ## In split save, we save each result separately in a folder
    split_save_folder: Path = save_root_path.joinpath(f'split').resolve()
    if debug_print:
        print(f'split_save_folder: {split_save_folder}')
    # make if doesn't exist
    split_save_folder.mkdir(exist_ok=True)

    ## only saves out the `global_computation_results` data:
    computed_data = obj_to_split.__dict__ # param_typed_parameters.to_dict()
    split_save_paths = {}
    split_save_output_types = {}
    failed_keys = []
    skipped_keys = []
    for k, v in computed_data.items():
        if k in include_includelist:
            curr_split_result_pickle_path = split_save_folder.joinpath(f'Split_{k}.pkl').resolve()
            if debug_print:
                print(f'curr_split_result_pickle_path: {curr_split_result_pickle_path}')
            was_save_success = False
            curr_item_type = type(v)
            try:
                ## try get as dict                
                v_dict = v.__dict__ #__getstate__()
                db = (v_dict, str(curr_item_type.__module__), str(curr_item_type.__name__))                
                with open(curr_split_result_pickle_path, 'w+b') as dbfile: 
                    # source, destination
                    # pickle.dump(db, dbfile)
                    custom_dump(db, dbfile) # ModuleExcludesPickler

                    dbfile.close()
                    
                was_save_success = True
            except KeyError as e:
                print(f'{k} encountered {e} while trying to save {k}. Skipping')
                pass
            if was_save_success:
                split_save_paths[k] = curr_split_result_pickle_path
                split_save_output_types[k] = curr_item_type
            else:
                failed_keys.append(k)
        else:
            if debug_print:
                print(f'skipping key "{k}" because it is not included in include_includelist: {include_includelist}')
            skipped_keys.append(k)
            
    if len(failed_keys) > 0:
        print(f'WARNING: failed_keys: {failed_keys} did not save for global results! They HAVE NOT BEEN SAVED!')
    succeeded_keys = list(split_save_paths.keys())
    return split_save_folder, (split_save_paths, split_save_output_types), (succeeded_keys, failed_keys, skipped_keys)