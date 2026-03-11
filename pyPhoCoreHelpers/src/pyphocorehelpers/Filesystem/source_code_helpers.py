import os
import sys
import pathlib
import re
import hashlib # for hashing pyproject.toml files and seeing if they changed
import inspect
from typing import Optional, List, Dict, Callable
from attrs import define, field
from urllib.parse import urlencode, quote

"""
from pyphocorehelpers.Filesystem.source_code_helpers import replace_text_in_file # for finding .whl file after building binary repo
from pyphocorehelpers.Filesystem.source_code_helpers import find_py_files
"""
def find_py_files(project_path, exclude_dirs=[]):
    # Find all .py files in the project directory and its subdirectories
    if not isinstance(project_path, pathlib.Path):
        project_path = pathlib.Path(project_path)
    py_files = project_path.glob("**/*.py")
    py_files = [file_path for file_path in py_files] # to list

    excluded_py_files = []
    if exclude_dirs is not None:
        # Find all .py files in the project directory and its subdirectories, excluding the 'my_exclude_dir' directory
        exclude_paths = [project_path.joinpath(a_dir) for a_dir in exclude_dirs]
        for an_exclude_path in exclude_paths:
            excluded_py_files.extend([file_path for file_path in an_exclude_path.glob("**/*.py")])

    included_py_files = [x for x in py_files if x not in excluded_py_files]
    return included_py_files


def replace_text_in_file(file_path, regex_pattern, replacement_string, debug_print=False):
    with open(file_path, 'r') as file:
        file_content = file.read()

    if debug_print:
        print(f"====================== Read from file ({file_path}) ======================:\n{file_content}")
    
    # updated_content = re.sub(regex_pattern, replacement_string, file_content, flags=re.MULTILINE)
    target_replace_strings = re.findall(regex_pattern, file_content, re.MULTILINE)
    assert len(target_replace_strings) == 1
    target_replace_string = target_replace_strings[0]
    if debug_print:
        print(f'Replacing:\n{target_replace_string}')
        print(f"====================== replacing ======================:\n{target_replace_string}\n\n====================== with replacement string ====================== :\n{replacement_string}\n\n")
    updated_content = file_content.replace(target_replace_string, replacement_string, 1)
    if debug_print:
        print(updated_content)

    if debug_print:
        print(f"======================  updated_content ====================== :\n{updated_content}\n\n")
        print(f"====================== saving to {file_path}...")
    with open(file_path, 'w') as file:
        file.write(updated_content)

def insert_text(source_file, insert_text_str:str, output_file, insertion_string:str='<INSERT_HERE>'):
    """Inserts the text from insert_text_str into the source_file at the insertion_string, and saves the result to output_file.

    Args:
        source_file (_type_): _description_
        insert_text_str (str): _description_
        output_file (_type_): _description_
        insertion_string (str, optional): _description_. Defaults to '<INSERT_HERE>'.
    """
    # Load the source text
    with open(source_file, 'r') as f:
        source_text = f.read()

    # Find the insertion point in the source text
    insert_index = source_text.find(insertion_string)

    # Insert the text
    updated_text = source_text[:insert_index] + insert_text_str + source_text[insert_index:]

    # Save the updated text to the output file
    with open(output_file, 'w') as f:
        f.write(updated_text)

def insert_text_from_file(source_file, insert_file, output_file, insertion_string:str='<INSERT_HERE>'):
    """ Wraps insert_text, but loads the insert_text from a file instead of a string. """
    # Load the insert text
    with open(insert_file, 'r') as f:
        insert_text_str = f.read()
    insert_text(source_file, insert_text_str, output_file, insertion_string)

def hash_text_in_file(file_path, ignore_whitespace:bool=True, ignore_line_comments:bool=True, case_insensitive:bool=True):
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Remove all comments from the string by searching for the '#' character and removing everything from that character to the end of the line.
    if ignore_line_comments:
        file_content = '\n'.join(line.split('#')[0] for line in file_content.split('\n'))

    # remove all whitespace characters (space, tab, newline, and so on)
    if ignore_whitespace:
        file_content = ''.join(file_content.split())

    if case_insensitive:
        file_content = file_content.lower()

    return hashlib.sha256(file_content.encode('utf-8')).hexdigest()

def did_file_hash_change(file_path):
    """ Returns True if the file's hash value has changed since the last run by reading f'{file_path}.sha256'. Saves the new hash value to f'{file_path}.sha256'"""
    # Define the path to the previous hash value file
    hash_file_path = f'{file_path}.sha256'

    # Calculate the new hash value
    new_hash_value = hash_text_in_file(file_path)    

    # Check if the hash value file exists
    if os.path.exists(hash_file_path):
        # Read the previous hash value from the file
        with open(hash_file_path, 'r') as f:
            old_hash_value = f.read().strip()

        # Compare the new hash value with the previous hash value
        if new_hash_value == old_hash_value:
            print('The file has *NOT* changed since the last run')
            did_file_change = False
        else:
            print('The file *HAS* changed since the last run')
            did_file_change = True
    else:
        # No previous hash value file exists:
        did_file_change = True

    if did_file_change:
        # Save the new hash value to the file
        with open(hash_file_path, 'w') as f:
            f.write(new_hash_value)

    return did_file_change


@define(slots=False)
class VSCodeLinkGenerator:
    """ builds a clickable VSCode link to a specific function 
        Like 'vscode://file/home/halechr/repos/pyPhoPlaceCellAnalysis/src/pyphoplacecellanalysis/GUI/PyVista/InteractivePlotter/Mixins/LapsVisualizationMixin.py:60'
        
    Usage:
        from pyphocorehelpers.Filesystem.source_code_helpers import VSCodeLinkGenerator
        
        example_function = curr_active_pipeline.registered_display_function_dict['_display_long_and_short_stacked_epoch_slices']
        example_function

    
    ## Testing with workspace root:
        link_generator = VSCodeLinkGenerator(func_obj=example_function, workspace_root='/home/halechr/repos/Spike3D/EXTERNAL/VSCode_Workspaces', use_relative_path=True) # , workspace_root='/path/to/workspace/root'
        link_text: str = link_generator.generate_link()
        print(f'link_text: {link_text}')

        link_generator.link_widget()
        
    """
    func_obj: Callable
    workspace_root: Optional[str] = None  # Root directory of your workspace
    include_column: bool = False  # Include column number in the link
    markdown: bool = False  # Generate markdown link
    use_relative_path: bool = False
    new_window: bool = False  # Open in new window or not
    

    def generate_link(self) -> str:
        source_info = inspect.getsourcelines(self.func_obj)
        start_line = source_info[1]
        file_path = inspect.getsourcefile(self.func_obj)
        
        if not file_path:
            raise Exception("Function source file could not be determined.")
        
        if self.use_relative_path:
            assert self.workspace_root is not None, "No workspace root provided."
                
            relative_path = os.path.relpath(file_path, self.workspace_root)
            active_path = relative_path
        else:
            active_path = file_path

        query = urlencode({'newWindow': 'true' if self.new_window else 'false'})
        url = f"vscode://file{active_path}:{start_line}?{query}"
        
        if self.include_column:
            url += ":1"  # Assuming column 1 since we are linking to the function definition
            
        output = f"[{active_path}:{start_line}]({url})" if self.markdown else url
        
        return output
    
    def link_widget(self):
        from ipywidgets import widgets
        return widgets.HTML(value=f'<a href="{self.generate_link()}" target="_blank">Go to function definition</a>')


@define(slots=False)
class FunctionLinkGenerator:
    """ 
    # Assuming the base URL of the Git repository is 'https://github.com/your_username/your_repository'
    link_generator = FunctionLinkGenerator(func_obj=example_function, base_url='https://github.com/your_username/your_repository')
    link_generator.generate_link()

    """
    func_obj: Callable
    base_url: str  # Base URL of the repository
    
    def generate_link(self) -> str:
        source_info = inspect.getsourcelines(self.func_obj)
        start_line = source_info[1]
        end_line = start_line + len(source_info[0]) - 1
        file_path = inspect.getsourcefile(self.func_obj)
        
        # If the file path is relative, adjust according to your setup
        url = f"{self.base_url}/blob/main/{quote(file_path)}#L{start_line}-L{end_line}"
        return url
    
    def link_widget(self):
        from ipywidgets import widgets
        link_html = f'<a href="{self.generate_link()}" target="_blank">Go to function definition</a>'    
        return widgets.HTML(value=link_html)


""" Pending usages of VSCodeLinkGenerator and FunctionLinkGenerator 

from pyphocorehelpers.Filesystem.source_code_helpers import VSCodeLinkGenerator
from pyphocorehelpers.Filesystem.source_code_helpers import FunctionLinkGenerator
from ipywidgets import widgets, HBox, VBox
from ipywidgets import widgets

@define(slots=False)
class DictionaryTableDisplay:
    data_dict: dict
    workspace_root: str
    
    def display_table(self):
        df = pd.DataFrame.from_dict(self.data_dict, orient='index', columns=['Value'])
        df['Function'] = None

        link_generator = VSCodeLinkGenerator(None, workspace_root=self.workspace_root)
        
        for key, value in self.data_dict.items():
            if callable(value):
                link_generator.func_obj = value
                # url = link_generator.generate_link()
                url = link_generator.generate_link()
                button_html = f'<button onclick="window.open(\'{url}\', \'_blank\')">Go to Function</button>'
                df.at[key, 'Function'] = button_html
                
        display_widget = widgets.Output()
        with display_widget:
            display(df.to_html(escape=False))
        
        return display_widget

# Assuming the root directory of your workspace is '/path/to/workspace/root'
table_display = DictionaryTableDisplay(data_dict=curr_active_pipeline.registered_display_function_dict, workspace_root='/home/halechr/repos')
table_display.display_table()
"""