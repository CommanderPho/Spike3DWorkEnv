from pathlib import Path
from typing import Dict, List, Tuple
import h5py
import numpy as np
import pandas as pd
import tables

ignored_keys = ['#subsystem#', '#refs#']





def h5dump(path, group='/', enable_print_attributes=False):
    """ print HDF5 file metadata
    group: you can give a specific group, defaults to the root group                 
    """
    with h5py.File(path,'r') as f:
         HDF5_Helper.descend_obj(f[group], enable_print_attributes=enable_print_attributes)

class HDF5_Helper(object):
    """docstring for hdf5Helper."""
    
    def __init__(self, path, group='/'):
        super(HDF5_Helper, self).__init__()
        self.path = path
        self.group = group
        self.output_tree = {}
        self.perform_enumerate()


    def perform_descend_obj(self, obj, sep='\t', enable_print_attributes=False, debug_print=False):
        """ Iterate through groups in a HDF5 file and prints the groups and datasets names and datasets attributes
        """
        children_subtree_dict = {}
        if type(obj) in [h5py._hl.group.Group, h5py._hl.files.File]:
            obj_description = obj.name # full path to the group
            
            obj_keys = [a_key for a_key in obj.keys() if '#' not in a_key]
            for key in obj_keys:
                if debug_print:
                    print(sep, '-', key, ':', obj[key])
                child_output = self.perform_descend_obj(obj[key], sep=sep+'\t', enable_print_attributes=enable_print_attributes, debug_print=debug_print)
                # child_output: should either be a dict or None depending on whether the child is a leaf
                if child_output is None:
                    print(f'leaf encountered for child: {key} of {obj}')
                    # children_subtree_dict[key] = obj[key] # set the child directly
                    children_subtree_dict[key] = obj_description # set the child directly
                else:
                    print(f'non-leaf encountered for child: {key} of {obj}')
                    children_subtree_dict[key] = child_output
            return children_subtree_dict # return the dictionary containing the children's subtree
                
        elif type(obj)==h5py._hl.dataset.Dataset:
            obj_description = f'{obj.name} - Dataset'
            if enable_print_attributes:
                obj_keys = [a_key for a_key in obj.attrs.keys() if '#' not in a_key]
                for key in obj_keys:
                    # Do not descend any further, just print the attributes
                    print(sep+'\t', '-', key, ':', obj.attrs[key])
            # Base case for Recurrsion:
            return None
                    
    def perform_enumerate(self, debug_print=False):
        self.output_tree = {}
        with h5py.File(self.path,'r') as f:
            self.output_tree = self.perform_descend_obj(f[self.group], enable_print_attributes=False, debug_print=debug_print)
        return self.output_tree
        
    @classmethod
    def descend_obj(cls, obj, sep='\t', enable_print_attributes=False):
        """
            Iterate through groups in a HDF5 file and prints the groups and datasets names and datasets attributes
        """
        if type(obj) in [h5py._hl.group.Group, h5py._hl.files.File]:
            obj_keys = [a_key for a_key in obj.keys() if '#' not in a_key]
            for key in obj_keys:
                print(sep, '-', key, ':', obj[key]) # - behavioral_epochs : <HDF5 dataset "behavioral_epochs": shape (1, 6), type "<u4">
                cls.descend_obj(obj[key], sep=sep+'\t', enable_print_attributes=enable_print_attributes)
        elif type(obj)==h5py._hl.dataset.Dataset:
            if enable_print_attributes:
                obj_keys = [a_key for a_key in obj.attrs.keys() if '#' not in a_key]
                for key in obj_keys:
                    # Do not descend any further, just print the attributes
                    print(sep+'\t', '-', key, ':', obj.attrs[key])
            
    @classmethod
    def h5dump(cls, path, group='/', enable_print_attributes=False):
        """ print HDF5 file metadata

        group: you can give a specific group, defaults to the root group
        
            ## For enable_print_attributes == False:
                    - behavioral_epochs : <HDF5 dataset "behavioral_epochs": shape (1, 6), type "<u4">
                    - behavioral_periods_table : <HDF5 dataset "behavioral_periods_table": shape (1, 6), type "<u4">
                    - definitions : <HDF5 group "/active_processing/definitions" (3 members)>
                    - behavioral_epoch : <HDF5 group "/active_processing/definitions/behavioral_epoch" (2 members)>
                            - classNames : <HDF5 dataset "classNames": shape (3, 1), type "|O">
                            - classValues : <HDF5 dataset "classValues": shape (3, 1), type "<f8">
                    - behavioral_state : <HDF5 group "/active_processing/definitions/behavioral_state" (2 members)>
                            - classNames : <HDF5 dataset "classNames": shape (4, 1), type "|O">
                            - classValues : <HDF5 dataset "classValues": shape (4, 1), type "<f8">
                    - speculated_unit_info : <HDF5 group "/active_processing/definitions/speculated_unit_info" (2 members)>
                            - classCutoffValues : <HDF5 dataset "classCutoffValues": shape (4, 1), type "<f8">
                            - classNames : <HDF5 dataset "classNames": shape (3, 1), type "|O">
                    - earliest_start_timestamp : <HDF5 dataset "earliest_start_timestamp": shape (1, 1), type "<f8">
                    - position_table : <HDF5 dataset "position_table": shape (1, 6), type "<u4">
                    - processed_array : <HDF5 dataset "processed_array": shape (1, 2), type "|O">
                    - speed_table : <HDF5 dataset "speed_table": shape (1, 6), type "<u4">
                    - spikes : <HDF5 dataset "spikes": shape (1, 6), type "<u4">

            ## For enable_print_attributes == True:
                    - behavioral_epochs : <HDF5 dataset "behavioral_epochs": shape (1, 6), type "<u4">
                            - H5PATH : b'/active_processing'
                            - MATLAB_class : b'table'
                            - MATLAB_object_decode : 3
                    - behavioral_periods_table : <HDF5 dataset "behavioral_periods_table": shape (1, 6), type "<u4">
                            - H5PATH : b'/active_processing'
                            - MATLAB_class : b'table'
                            - MATLAB_object_decode : 3
                    - definitions : <HDF5 group "/active_processing/definitions" (3 members)>
                    - behavioral_epoch : <HDF5 group "/active_processing/definitions/behavioral_epoch" (2 members)>
                            - classNames : <HDF5 dataset "classNames": shape (3, 1), type "|O">
                                    - H5PATH : b'/active_processingdefinitionsbehavioral_epoch'
                                    - MATLAB_class : b'cell'
                            - classValues : <HDF5 dataset "classValues": shape (3, 1), type "<f8">
                                    - H5PATH : b'/active_processingdefinitionsbehavioral_epoch'
                                    - MATLAB_class : b'double'
                    - behavioral_state : <HDF5 group "/active_processing/definitions/behavioral_state" (2 members)>
                            - classNames : <HDF5 dataset "classNames": shape (4, 1), type "|O">
                                    - H5PATH : b'/active_processingdefinitionsbehavioral_state'
                                    - MATLAB_class : b'cell'
                            - classValues : <HDF5 dataset "classValues": shape (4, 1), type "<f8">
                                    - H5PATH : b'/active_processingdefinitionsbehavioral_state'
                                    - MATLAB_class : b'double'
                    - speculated_unit_info : <HDF5 group "/active_processing/definitions/speculated_unit_info" (2 members)>
                            - classCutoffValues : <HDF5 dataset "classCutoffValues": shape (4, 1), type "<f8">
                                    - H5PATH : b'/active_processingdefinitionsspeculated_unit_info'
                                    - MATLAB_class : b'double'
                            - classNames : <HDF5 dataset "classNames": shape (3, 1), type "|O">
                                    - H5PATH : b'/active_processingdefinitionsspeculated_unit_info'
                                    - MATLAB_class : b'cell'
                    - earliest_start_timestamp : <HDF5 dataset "earliest_start_timestamp": shape (1, 1), type "<f8">
                            - H5PATH : b'/active_processing'
                            - MATLAB_class : b'double'
                    - position_table : <HDF5 dataset "position_table": shape (1, 6), type "<u4">
                            - H5PATH : b'/active_processing'
                            - MATLAB_class : b'table'
                            - MATLAB_object_decode : 3
                    - processed_array : <HDF5 dataset "processed_array": shape (1, 2), type "|O">
                            - H5PATH : b'/active_processing'
                            - MATLAB_class : b'cell'
                    - speed_table : <HDF5 dataset "speed_table": shape (1, 6), type "<u4">
                            - H5PATH : b'/active_processing'
                            - MATLAB_class : b'table'
                            - MATLAB_object_decode : 3
                    - spikes : <HDF5 dataset "spikes": shape (1, 6), type "<u4">
                            - H5PATH : b'/active_processing'
                            - MATLAB_class : b'table'
                            - MATLAB_object_decode : 3
                    
        """
        with h5py.File(path,'r') as f:
            cls.descend_obj(f[group], enable_print_attributes=enable_print_attributes)
            

    @classmethod
    def get_leaf_datasets(cls, file_path: Path):
        """
        Retrieve all leaf datasets from an HDF5 file.

        Args:
            file_path (Path): Path to the HDF5 file.

        Returns:
            list: A list of leaf dataset paths.
            
        Usage:
            from pyphocorehelpers.Filesystem.HDF5.hdf5_file_helpers import HDF5_Helper
            load_path = Path('output/all_decoded_epoch_posteriors.h5').resolve()
            assert load_path.exists()
            leaf_datasets = HDF5_Helper.get_leaf_datasets(load_path)
            print(leaf_datasets)

        """
        leaf_datasets = []

        def visit_func(name, node):
            # Check if the node is a dataset and add to list if true
            if isinstance(node, h5py.Dataset):
                leaf_datasets.append(name)

        # Open the HDF5 file in read mode and apply the visit function
        with h5py.File(file_path, 'r') as f:
            f.visititems(visit_func)

        return leaf_datasets

    @classmethod
    def find_groups_by_name(cls, file_path: Path, group_name: str):
        """
        Search for groups with a specific name in an HDF5 file and return their paths.

        Args:
            file_path (Path): Path to the HDF5 file.
            group_name (str): Name of the group to search for.

        Returns:
            list: A list of paths to groups that match the specified name.
            
        Usage:
            load_path = Path('output/all_decoded_epoch_posteriors.h5').resolve()
            assert load_path.exists()
            found_groups = HDF5_Helper.find_groups_by_name(load_path, 'save_decoded_posteriors_to_HDF5')
            print(found_groups) # ['kdiba/gor01/one/2006-6-08_14-26-15/save_decoded_posteriors_to_HDF5']


        """
        matching_groups = []

        def visit_func(name, node):
            # Check if the node is a group and its name matches the search criteria
            if isinstance(node, h5py.Group) and name.endswith(group_name):
                matching_groups.append(name)

        # Open the HDF5 file in read mode and apply the visit function
        with h5py.File(file_path, 'r') as f:
            f.visititems(visit_func)

        return matching_groups


# ==================================================================================================================== #
# 2024-04-01 - Unfinished                                                                                              #
# ==================================================================================================================== #
            

# # Raw h5py ___________________________________________________________________________________________________________ #
# def _hdf5_to_dict_recurr(hdf5_object):
#     """
#     Recursively reads HDF5 file objects and constructs a nested dictionary
#     of datasets and arrays.
    
#     Parameters:
#         hdf5_object: An h5py.Group or h5py.File object.
        
#     Returns:
#         A nested dictionary with the HDF5 hierarchy's structure.
#     """
#     result = {}
#     for name, item in hdf5_object.items():
#         if isinstance(item, h5py.Dataset):  # Found a dataset
#             result[name] = item[()]  # Load the dataset's content into the dict
#         elif isinstance(item, h5py.Group):  # Found a group, recurse
#             result[name] = _hdf5_to_dict_recurr(item)  # Recursively call on the group
#     return result

# def hdf5_to_dict(hdf5_path: Path):
#     """
#     Recursively reads HDF5 file objects and constructs a nested dictionary
#     of datasets and arrays.
    
#     Parameters:
#         hdf5_object: An h5py.Group or h5py.File object.
        
#     Returns:
#         A nested dictionary with the HDF5 hierarchy's structure.
#     """
#     data_dict = {}
#     failed_keys = []

#     # Open the HDF5 file and start the conversion process
#     with h5py.File(hdf5_path, 'r') as hdf_file:
#         data_dict = _hdf5_to_dict_recurr(hdf_file)

#     return data_dict, failed_keys


def write_hdf5_data_manifest(hdf5_path: Path, manifest_key_strings: List[str], datamanifest_key: str = 'data_manifest'):
    """ tries to write a list of keys as a manifest of the data contained within the file for easier loading.
    
    Usage:
        from pyphocorehelpers.Filesystem.HDF5.hdf5_file_helpers import write_hdf5_data_manifest

        hdf5_path = debug_output_hdf5_file_path # 'your_existing_file.h5'
        # nested_strings = [['provided/long_LR/laps_df', 'provided/long_LR/train_df', 'provided/long_LR/test_df'], ['valid/long_LR/train_df', 'valid/long_LR/test_df'], ['provided/long_RL/laps_df', 'provided/long_RL/train_df', 'provided/long_RL/test_df'], ['valid/long_RL/train_df', 'valid/long_RL/test_df'], ['provided/short_LR/laps_df', 'provided/short_LR/train_df', 'provided/short_LR/test_df'], ['valid/short_LR/train_df', 'valid/short_LR/test_df'], ['provided/short_RL/laps_df', 'provided/short_RL/train_df', 'provided/short_RL/test_df'], ['valid/short_RL/train_df', 'valid/short_RL/test_df']]
        # Flatten the nested list into a single list of strings
        # strings = [item for sublist in nested_strings for item in sublist]
        manifest_key_strings = ['provided/long_LR/laps_df', 'provided/long_LR/train_df', 'provided/long_LR/test_df', 'valid/long_LR/train_df', 'valid/long_LR/test_df', 'provided/long_RL/laps_df', 'provided/long_RL/train_df', 'provided/long_RL/test_df', 'valid/long_RL/train_df', 'valid/long_RL/test_df', 'provided/short_LR/laps_df', 'provided/short_LR/train_df', 'provided/short_LR/test_df', 'valid/short_LR/train_df', 'valid/short_LR/test_df', 'provided/short_RL/laps_df', 'provided/short_RL/train_df', 'provided/short_RL/test_df', 'valid/short_RL/train_df', 'valid/short_RL/test_df']
        write_hdf5_data_manifest(hdf5_path=hdf5_path, manifest_key_strings=manifest_key_strings)

    """
    # Convert the list of strings to a fixed-size numpy array of strings. 
    # This is necessary because HDF5 datasets require fixed-size elements.
    # variable_length_string_dtype = h5py.special_dtype(vlen=str)
    # string_arr = np.array(strings, dtype=variable_length_string_dtype)
    # variable_length_data = np.array(strings, dtype=variable_length_string_dtype)

    # Convert variable-length strings to fixed-length strings (truncating if necessary)
    fixed_length_dtype = 'S200'  # This example creates strings with a fixed length of 100 chars
    string_arr = np.array(manifest_key_strings, dtype=fixed_length_dtype)
    # string_arr = np.array(variable_length_data.astype(fixed_length_dtype), dtype=fixed_length_dtype)
    # Path to your existing HDF5 file
    
    # Open the HDF5 file in append mode (or "a" mode)
    with h5py.File(hdf5_path, 'a') as hdf_file:
        # Create a new dataset within the file to hold your array of strings,
        # or overwrite an existing one.
        dataset_name = 'data_manifest'
        
        # Check if the dataset already exists and if so, delete it.
        if dataset_name in hdf_file:
            del hdf_file[dataset_name]
        
        # Create a new dataset to store the list of strings
        hdf_file.create_dataset(dataset_name, data=string_arr)

        # Optionally you can specify compression to save space:
        # hdf_file.create_dataset('strings_dataset', data=string_arr, compression='gzip')



# # PyTables ___________________________________________________________________________________________________________ #
# def _pytables_to_dict_recurr(hdf5_node):
#     """
#     Recursively reads HDF5 file nodes stored with PyTables and constructs a
#     nested dictionary of tables and arrays.
    
#     Parameters:
#         hdf5_node: A PyTables Group or File node.
        
#     Returns:
#         A nested dictionary with the HDF5 hierarchy's structure.
#     """
#     result = {}
#     for node in hdf5_node:
#         if isinstance(node, tables.Group):
#             # Recurse into the group
#             result[node._v_name] = _pytables_to_dict_recurr(node) # call recurrsively
#         elif isinstance(node, tables.Table) or isinstance(node, tables.Array):
#             # Read the Table or Array data
#             # print(f'found node: "{node._v_name}" that is a Table or Array')
#             result[node._v_name] = node.read()
#             # if (node._v_name) == 'table':
#             #     result[node._v_name] = node.read()
#             #     node.read
#             #     node.t
#             # else:
#             #     print(f'\t not dataframe.')
#             #     result[node._v_name] = node.read()

#     return result

# def pytables_to_dict(hdf5_path: Path):
#     """
#     Recursively reads HDF5 file nodes stored with PyTables and constructs a
#     nested dictionary of tables and arrays.
    
#     Parameters:
#         hdf5_node: A PyTables Group or File node.
        
#     Returns:
#         A nested dictionary with the HDF5 hierarchy's structure.
#     """


#     data_dict = {}
#     failed_keys = []

#     # Open the HDF5 file using PyTables and start the conversion process
#     with tables.open_file(hdf5_path, 'r') as hdf_file:
#         data_dict = _pytables_to_dict_recurr(hdf_file.root)

#     return data_dict


# pandas _____________________________________________________________________________________________________________ #
def hdf5_to_pandas_df_dict(hdf5_path: Path) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
    # Using the pandas HDFStore to manage access to the file

    data_dict = {}
    failed_keys = []

    with pd.HDFStore(hdf5_path, 'r') as store:
        # Iterate over all the keys in the HDFStore and read each one as a DataFrame
        for key in store.keys():
            # Use exception handling to catch errors for non-DataFrame data
            try:
                data_dict[key] = pd.read_hdf(store, key)
            except (ValueError, TypeError) as e:
                print(f"Could not read key '{key}': {e}")
                # Handle non-DataFrame data differently or skip
                # For example, store the keys that failed for further investigation
                failed_keys.append(key)



    # Now `data_dict` is a nested dictionary structure with the HDF5 file's content.
    # You can access the datasets and groups just like you would with a normal Python dict.
    return data_dict, failed_keys


