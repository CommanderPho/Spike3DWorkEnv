import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from pyphocorehelpers.function_helpers import function_attributes


class FilesystemMetadata:
    """ helps with accessing cross-platform filesystem metadata
    
    
    from pyphocorehelpers.Filesystem.metadata_helpers import FilesystemMetadata, get_file_metadata, get_files_metadata
    

    """
    
    @staticmethod
    def get_last_modified_time(file_path: str) -> datetime:
        """
        Returns the last modified time of a file.

        :param file_path: The path to the file.
        :return: The last modified time as a datetime object.
        """
        return datetime.fromtimestamp(os.path.getmtime(file_path))

    @staticmethod
    def get_creation_time(file_path: str) -> datetime:
        """
        Returns the creation time of a file.

        :param file_path: The path to the file.
        :return: The creation time as a datetime object.
        """
        return datetime.fromtimestamp(os.path.getctime(file_path))

    @staticmethod
    def get_file_size_GB(file_path: str) -> float:
        """
        Returns the size of a file in Gigabytes (GB).

        :param file_path: The path to the file.
        :return: The file size in Gigabytes (GB)
        """
        return (os.path.getsize(file_path) / (1024 ** 3))  # Convert to GB


    @classmethod
    def set_modification_time(cls, file_path: str, new_time: datetime):
        """
        Set the access and modification times of a file.

        :param file_path: Path to the file
        :param new_time: datetime.datetime object representing the new time
        """
        if not isinstance(new_time, datetime):
            raise TypeError(f"new_time must be a datetime.datetime instance, but type(new_time): {type(new_time)}, value: {new_time})")

        timestamp = new_time.timestamp()

        try:
            os.utime(file_path, (timestamp, timestamp))
            print(f"Successfully updated times for {file_path}")
        except FileNotFoundError:
            print(f"Error: The file {file_path} does not exist.")
        except PermissionError:
            print(f"Error: Permission denied for {file_path}.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

            


def get_file_metadata(path, round_size_decimals:int=2) -> Optional[Dict]:
    if not path.is_file():
        return None

    modified_time = os.path.getmtime(path)
    created_time = os.path.getctime(path)
    file_size = round((os.path.getsize(path) / (1024 ** 3)), ndigits=round_size_decimals)  # Convert to GB
    return {'path': str(path), 'modification_time': datetime.fromtimestamp(modified_time), 'creation_time': datetime.fromtimestamp(created_time), 'file_size': file_size}
            

@function_attributes(short_name=None, tags=['filesystem','metadata','creation_time','modification_time','datetime','files'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2023-06-07 02:16', related_items=[])
def get_files_metadata(paths) -> pd.DataFrame:
    """
    Get the metadata (modification time, creation time, and file size) for each file specified by a list of pathlib.Path objects.
    :param paths: A list of pathlib.Path objects representing the file paths.
    :return: A pandas DataFrame with columns for path, modification time, creation time, and file size.
    """
    metadata = []

    for path in paths:
        if not isinstance(path, Path):
            path = Path(path).resolve()
            
        if path.is_file():
            modified_time = os.path.getmtime(path)
            created_time = os.path.getctime(path)
            file_size = os.path.getsize(path) / (1024 ** 3)  # Convert to GB
            metadata.append({
                'path': str(path),
                'modification_time': datetime.fromtimestamp(modified_time),
                'creation_time': datetime.fromtimestamp(created_time),
                'file_size': file_size
            })
            
    df = pd.DataFrame(metadata)
    df.style.format("{:.1f}") # suppresses scientific notation display only for this dataframe. Alternatively: pd.options.display.float_format = '{:.2f}'.format
    df['file_size'] = df['file_size'].round(decimals=2)
    
    return df


