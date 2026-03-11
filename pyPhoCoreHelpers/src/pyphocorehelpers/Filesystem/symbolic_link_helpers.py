import sys
import os
import shutil # used in `restore_symlink_folder`
from shutil import copytree # used in `make_specific_items_local`
from pathlib import Path
from typing import Optional, Dict, Optional, Tuple, List, Union
from datetime import datetime, timedelta
import numpy as np
from pyphocorehelpers.Filesystem.metadata_helpers import FilesystemMetadata, get_file_metadata
from pyphocorehelpers.Filesystem.path_helpers import discover_data_files, generate_copydict, copy_movedict, copy_file
from attrs import define, field, Factory


# ==================================================================================================================== #
# Symlink Helper Functions - 2024-01-11                                                                                #
# ==================================================================================================================== #
"""


Main Functions:

make_specific_items_local


"""


def nearest_symlink_ancestor_path(path: Path) -> Union[Path, None]:
    """Returns the path of the nearest parent directory of 'path' that is a symbolic link.
    If no parent directories are symbolic links, returns None.
    
    Usage:
        existing_symlink_path: Path = Path('/home/halechr/FastData/KDIBA/pin01/one/11-09_22-4-5/11-09_22-4-5IN.5.numclu')
        nearest_symlink_ancestor_path(existing_symlink_path)
        
    """

    for parent in path.parents:
        if parent.is_symlink():
            return parent
    return None


def symlinked_item_to_full_local_item(existing_symlink_path: Path, dryrun: bool=False, debug_print=True) -> bool:
    """ takes a path to an existing symlink on disk. Replaces that symlink with a local file/folder of the same name, copied from the symlink target.

    returns bool: true if symlink was localized
        
    WARNING:
        DO NOT CALL .resolve() on the input path, this resolves the symlink!!!
            
    Usage:

        existing_symlink_path: Path = Path('/home/halechr/FastData/KDIBA/pin01/one/fet11-01_12-58-54') ## DO NOT CALL .resolve() on the input path, this resolves the symlink!!!
        print(f'existing_symlink_path: {existing_symlink_path}')
        assert existing_symlink_path.exists()
        symlinked_item_to_full_local_item(existing_symlink_path, dryrun=False, debug_print=True)
        
        
    Potential Issue:
        if '/home/halechr/FastData/KDIBA/pin01' is a symlink to '/media/MAX/Data/KDIBA/pin01'
            If `symlinked_item_to_full_local_item` is called with existing_symlink_path='/home/halechr/FastData/KDIBA/pin01/one/fet11-01_12-58-54', doesn't it create a symlink to itself?


        '/media/MAX/Data/KDIBA/pin01/one/fet11-01_12-58-54'
    """
    def _subfn_try_link_to_full_item(a_symlink_path):
        """ 
        captures: dryrun, debug_print
        
        """
         # Resolve the symlink without following it
        unlinked_target = a_symlink_path.resolve(strict=False)
        # Check if the target's parent isn't under the symlink itself
        if unlinked_target.parent in a_symlink_path.parents:
            print(f"Error: cannot copy a folder or file into its child '{a_symlink_path}'!")
            return False
        
        # resolve the symlink and ensure it exists
        symlink_target = a_symlink_path.resolve()
        if not symlink_target.exists():
            print(f"Symlink target {symlink_target} does not exist.")
            return False
        
        # delete the original symlink and replace with a copy of the symlink target
        if symlink_target.is_dir():        # if it's a directory
            if dryrun:
                print(f'Would delete symlink: {a_symlink_path}')
                print(f'Would copy directory {symlink_target} to {a_symlink_path}')
            else:
                if debug_print:
                     print(f'Copy folder {symlink_target} to {a_symlink_path}')
                os.remove(a_symlink_path)
                shutil.copytree(symlink_target, a_symlink_path)
        else:    # it's a file
            if dryrun:
                print(f'Would delete symlink: {a_symlink_path}')
                print(f'Would copy file {symlink_target} to {a_symlink_path}')
            else:
                if debug_print:
                     print(f'Copy file {symlink_target} to {a_symlink_path}')
                os.remove(a_symlink_path)
                shutil.copy(symlink_target, a_symlink_path)

        return True
    

    # check that existing_symlink_path exists and is a symlink
    if existing_symlink_path.is_symlink():
        return _subfn_try_link_to_full_item(existing_symlink_path)
    else:
        print(f"{existing_symlink_path} is not a symlink.")
        nearest_symlink_ancestor = nearest_symlink_ancestor_path(existing_symlink_path)
        if (nearest_symlink_ancestor is None):
             print(f"{existing_symlink_path} is not a symlink and none of its ancestors are symlinks either.")
             return False
        else:
            if debug_print:
                print(f"found symlink ancestor: {nearest_symlink_ancestor}.")
            assert nearest_symlink_ancestor.exists()
            assert nearest_symlink_ancestor.is_symlink()

            # Need to convert the symlink to local folders containing symlinks using `symlinked_folder_to_local_folder_containing_symlinks(...)`
            relative_to_symlink_ancestor = None
            assert nearest_symlink_ancestor.is_symlink()
            try:
                relative_to_symlink_ancestor = existing_symlink_path.parent.relative_to(nearest_symlink_ancestor)
            except ValueError:
                # existing_symlink_path is not a subpath of nearest_ancestor_path
                relative_to_symlink_ancestor = None
                print(f'could not get path relative to ancestor.')
                return False
            
            if debug_print:
                print(f'relative_to_symlink_ancestor: {relative_to_symlink_ancestor}') # PosixPath('one/2006-4-18_13-6-1/output')

            ancestor_path_parts_to_resolve = relative_to_symlink_ancestor.parts # ('one', '2006-4-18_13-6-1', 'output')
            num_paths_to_partial_localize = len(relative_to_symlink_ancestor.parts)
            if debug_print:
                print(f'num_paths_to_partial_localize: {num_paths_to_partial_localize}')

            ancestor_paths_to_resolve = [nearest_symlink_ancestor.joinpath(*ancestor_path_parts_to_resolve[:i]) for i in np.arange(num_paths_to_partial_localize+1)] # [(), ('one',), ('one', '2006-4-18_13-6-1'), ('one', '2006-4-18_13-6-1', 'output')]
            if dryrun or debug_print:
                 print(f'ancestor_paths_to_resolve: {ancestor_paths_to_resolve}')
                 
            # resolve them sequentially:
            for an_ancestor in ancestor_paths_to_resolve:
                did_work = symlinked_folder_to_local_folder_containing_symlinks(an_ancestor, dryrun=dryrun, debug_print=debug_print)
                if not did_work:
                    print(f"ERR: symlinked_folder_to_local_folder_containing_symlinks({an_ancestor}) did not work!")
                    return False
            # done with all now
            assert existing_symlink_path.is_symlink(), f"existing_symlink_path: '{existing_symlink_path}' is still not a symlink even after apprent successful linking"
            return _subfn_try_link_to_full_item(existing_symlink_path) # try one last time.

        return False


def symlinked_folder_to_local_folder_containing_symlinks(existing_symlink_folder_path: Path, dryrun: bool=False, debug_print=True) -> bool:
    """ takes a path to an existing symlink on disk. Replaces that symlink with a local folder it creates in the same place, and then creates symlinks inside the new folder to all items in the symlinked folder.

    returns bool: true if symlink was changed
        
    WARNING:
        DO NOT CALL .resolve() on the input path, this resolves the symlink!!!
            
            
    Usage:

        existing_symlink_folder_path: Path = Path('/home/halechr/FastData/KDIBA/pin01') ## DO NOT CALL .resolve() on the input path, this resolves the symlink!!!
        print(f'existing_symlink_folder_path: {existing_symlink_folder_path}')
        assert existing_symlink_folder_path.exists()
        symlinked_folder_to_local_folder_containing_symlinks(existing_symlink_folder_path, dryrun=False)

    """
    # check that existing_symlink_folder_path exists, is a symlink, and links to a folder
    if existing_symlink_folder_path.is_symlink():
        destination_folder = existing_symlink_folder_path.resolve(strict=False)
        if destination_folder.is_dir():
            if dryrun:
                print(f'Would delete symlink: {existing_symlink_folder_path}')
                print(f'Would create directory: {existing_symlink_folder_path}')
                # print(f'Would create symlinks in {existing_symlink_folder_path} for all items in {destination_folder}')
            else:
                if debug_print:
                    print(f'Will create directory: {existing_symlink_folder_path}')
                # delete the original symlink
                os.unlink(existing_symlink_folder_path)
                
                # create new folder where the symlink was
                os.mkdir(existing_symlink_folder_path)
                
            # create symlinks in the new folder for each file/folder in the original symlinked folder
            for item in destination_folder.iterdir():
                symlink_path = existing_symlink_folder_path / item.name
                if dryrun:
                    print(f'\t Would create symlinks in {symlink_path}\t->\t{item}')
                else:	
                    if debug_print:
                        print(f'\t Will create symlinks in {symlink_path}\t->\t{item}')            
                    os.symlink(item, symlink_path)
                    
            return True
        
        else:
            print(f"Err: Original symlink destination {destination_folder} is not a directory.")
            return False

    else:
        print(f"{existing_symlink_folder_path} is not a symlink.")
        print(f'if this above shows an unexpected path (the target and not the symlink location you thought you passed in), make sure you are not calling `existing_symlink_folder_path.resolve()` on the input, this resolves the symlink!\n')
        return False


def restore_symlink_folder(original_folder_path: Path, dryrun: bool=False) -> bool:
    """
    This function takes a path to an existing directory filled with symlinked files and restores it to be one single symlink.
    Inverse of `symlinked_folder_to_local_folder_containing_symlinks`


    It works as follows:
    - Check if `original_folder_path` is a directory
    - If it is, scan its contents
    - All contents should be symbolic links. If not, print an error message/exit
    - All symbolic links should direct to the same directory. If not, print an error message/exit
    - With the target directory established, delete `original_folder_path` and all contents
    - Create a new symlink at `original_folder_path` pointing to the target directory


    Usage:

        restore_symlink_folder(existing_symlink_folder_path, dryrun=False)

    """

    if original_folder_path.is_dir():
        # Collect all unique destinations this folder points to (should only be one)
        destinations = set(path.resolve().parent for path in original_folder_path.iterdir() if path.is_symlink()) # `set(...)` here is what make it so only unique entries are used

        if len(destinations) > 1:
            print(f'Error: multiple symlink destinations found in directory {original_folder_path}.\n\tdestinations: {destinations}')
            return False
        elif len(destinations) == 0:
            print(f'Error: no symlinks found in directory {original_folder_path}.')
            return False
        else:
            target_dir = destinations.pop()

            if dryrun:
                print(f'Would delete folder {original_folder_path} and its contents.')
                print(f'Would create symlink: {original_folder_path} -> {target_dir}')
            else:
                # delete the directory and its content
                shutil.rmtree(original_folder_path)

                # create the symlink
                os.symlink(target_dir, original_folder_path)
        
            return True
    else:
        print(f"Error: {original_folder_path} is not a directory.")
        return False


def make_specific_items_local(existing_symlink_folder_path: Path, desired_local_folder_paths: List[Path], dryrun: bool=False, debug_print=True) -> Dict[Path, bool]:
    """ 
    Takes a path you wish to clone to a local folder from a symlink.
    It then proceeds to copy the directories from the source directory to the destination directory using `shutil.copytree()`
    This will handle going into subdirectories as well.

    existing_symlink_folder_path: a path to the symlinked folder.
    desired_local_folder_paths: a list of paths you wish to copy locally from the file.
    
    Usage:
        from pyphocorehelpers.Filesystem.symbolic_link_helpers import make_specific_items_local

        ## DO NOT CALL .resolve() on the input path, this resolves the symlink!!!
        a_symlink_path: Path = Path('/home/halechr/FastData/KDIBA/pin01/one')
        print(f'existing_symlink_folder_path: {a_symlink_path}')
        assert a_symlink_path.exists()
        desired_local_folder_paths: List[Path] = [Path(v) for v in ['/home/halechr/FastData/KDIBA/vvp01/one/2006-4-18_13-6-1/output/global_computation_results.pkl', '/home/halechr/FastData/KDIBA/vvp01/one/2006-4-18_13-6-1/loadedSessPickle.pkl',
                                                                    '/home/halechr/FastData/KDIBA/vvp01/one/2006-4-18_13-6-1/output/global_computation_results.pkl', '/home/halechr/FastData/KDIBA/vvp01/one/2006-4-18_13-6-1/loadedSessPickle.pkl',
                                                                    '/home/halechr/FastData/KDIBA/vvp01/one/2006-4-18_13-6-1/output/global_computation_results.pkl', '/home/halechr/FastData/KDIBA/vvp01/one/2006-4-18_13-6-1/loadedSessPickle.pkl',
                                                                    ]]
        make_specific_items_local(a_symlink_path, desired_local_folder_paths=desired_local_folder_paths, dryrun=True)


    """
    status_dict = {}
    for a_symlink_path in desired_local_folder_paths:
        if debug_print:
            print(f'>> a_symlink_path: {a_symlink_path}')
        assert a_symlink_path.exists(), f"a_symlink_path: '{a_symlink_path}' does not exist."
        status_dict[a_symlink_path] = symlinked_item_to_full_local_item(a_symlink_path, dryrun=dryrun, debug_print=debug_print)

    return status_dict



# ==================================================================================================================== #
# SymlinkManager  - 2024-01-02                                                                                         #
# ==================================================================================================================== #
## Related Notebook: `SCRATCH/2023-01-02 - Symlink Helper.ipynb`


@define(slots=False)
class SymlinkManager:
    """ 2024-01-02 - stores references to multiple alternative versions of a filesystem directory (such as a .venv folder) and allows easily switching between these by modifying a symbolic link at a given location 
    
    from pyphocorehelpers.Filesystem.symbolic_link_helpers import SymlinkManager

    ## Related Notebook: `SCRATCH/2023-01-02 - Symlink Helper.ipynb`

    
    """
    alternative_destination_directories: Dict[str, Path] = field() # the list of filesystem directories that will be symlinked to. The key is a shortname, otherwise the full path will be used.
    target_symlink_location: Path = field() # the location the symlink will be created
    

    def current_symlink_target(self) -> Tuple[Optional[str], Optional[Path]]:
        """ returns the current target the `target_symlink_location` points to. """
        if os.path.islink(self.target_symlink_location):
            found_target_path = Path(os.readlink(self.target_symlink_location)).resolve()
            found_known_destination_key = self.try_find_path_key_in_known_alternative_destination_directories(found_target_path)
            return (found_known_destination_key, found_target_path)
        else:
            return (None, None)

    def try_find_path_key_in_known_alternative_destination_directories(self, test_target_path: Path, debug_print=True) -> Optional[str]:
        found_known_destination_keys = [k for k, v in self.alternative_destination_directories.items() if v.resolve() == test_target_path]
        if len(found_known_destination_keys) > 0:
            if debug_print:
                print(f'equivalent to key: "{found_known_destination_keys[0]}"')
            return found_known_destination_keys[0]
        else:
            if debug_print:
                print(f'path "{test_target_path}" not found in self.alternative_destination_directories')
            return None # key not found
        
        
    def establish_symlink(self, new_target_path: Path):
        # Symlink the whl file to a generic version:
        new_target_path = new_target_path.resolve()
        found_known_destination_key = self.try_find_path_key_in_known_alternative_destination_directories(new_target_path)
        if found_known_destination_key is None:
            print(f'WARNING: new_target_path: "{new_target_path}" is not in self.alternative_destination_directories. Adding.')
            self.alternative_destination_directories[str(new_target_path)] = new_target_path


        symlink_path = self.target_symlink_location.resolve() # the path to the symlink
        # dst_path = 'current.whl'
        # Create the symbolic link
        try:
            print(f'\t symlinking {new_target_path} to {symlink_path}')
            os.symlink(new_target_path, symlink_path)
        except FileExistsError as e:
            print(f'\t WARNING: symlink {symlink_path} already exists. Removing it.')
            # Remove the symlink
            os.unlink(symlink_path)
            # Create the symlink
            os.symlink(new_target_path, symlink_path)
        except Exception as e:
            raise e
        

    @classmethod
    def version_real_folder(cls, real_folder_path: Path, destination_storage_parent_folder: Path, override_destination_storage_name: Optional[str]=None) -> "SymlinkManager":
        """ takes a real (non-symlink) folder path that will be moved to a different destination and then symlinked back to the directory with the same name. 
        
        Usage:    
            ## Copy
            real_folder = Path(r"C:/Users/pho/.pyenv/pyenv-win/versions/3.9.13new").resolve()
            destination_storage_parent_folder = Path(r'K:/FastSwap/Environments/pyenv/versions').resolve()
            _new_pyenv_symlinker = SymlinkManager.version_real_folder(real_folder, destination_storage_parent_folder=destination_storage_parent_folder, override_destination_storage_name='3.9.13new')
            _new_pyenv_symlinker
        """
        # Ensure that `real_folder_path` isn't already a symlink
        if os.path.islink(real_folder_path):
            raise ValueError("The provided path is already a symlink.")

        if override_destination_storage_name is None:
            override_destination_storage_name = real_folder_path.name
            
        destination_storage_folder: Path = destination_storage_parent_folder.joinpath(override_destination_storage_name).resolve()

        # destination_storage_folder should not already exist:
        assert (not destination_storage_folder.exists()), f"destination_storage_folder: {destination_storage_folder} already exists! Cannot symlink here. Specify a `override_destination_storage_name` if needed."
        
        # Make a full recursive copy of `real_folder_path` to the destination location (`destination_storage_folder`)
        shutil.copytree(real_folder_path, destination_storage_folder)

        # Replace the real directory at `real_folder_path` with a symlink back to the new_copy_destination
        if os.path.exists(real_folder_path):
            shutil.rmtree(real_folder_path)
        
        os.symlink(destination_storage_folder, real_folder_path)

        # Return a new SymlinkManager instance
        return cls(
            alternative_destination_directories={override_destination_storage_name: destination_storage_folder},
            target_symlink_location=real_folder_path
        )


# _venv_symlinker = SymlinkManager(
#     alternative_destination_directories={
#         'pypoetry': Path(r'K:\FastSwap\Environments\pypoetry\pypoetry\Cache\virtualenvs\spike3d-UP7QTzFM-py3.9'),
#         'original': Path(r'K:\FastSwap\Environments\.venv_original')
#     },
#     target_symlink_location=Path(r'C:\Users\pho\repos\Spike3DWorkEnv\Spike3D\.venv')
# )
# _venv_symlinker

# _venv_symlinker.current_symlink_target()


# ## Copy
# real_folder = Path(r"C:\Users\pho\.pyenv\pyenv-win\versions\3.9.13new").resolve()
# destination_storage_parent_folder = Path(r'K:\FastSwap\Environments\pyenv\versions').resolve()

# _new_pyenv_symlinker = SymlinkManager.version_real_folder(real_folder, destination_storage_parent_folder=destination_storage_parent_folder, override_destination_storage_name='3.9.13new')
# _new_pyenv_symlinker

