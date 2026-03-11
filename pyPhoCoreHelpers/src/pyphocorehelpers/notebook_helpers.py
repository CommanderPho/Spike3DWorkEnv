import os
import sys
import attr
from attrs import define, field, Factory
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from typing_extensions import TypeAlias
import nptyping as ND
from nptyping import NDArray
from IPython.core.magics.execution import _format_time
from datetime import datetime
import json
from pyphocorehelpers.Filesystem.path_helpers import sanitize_filename_for_Windows
from pyphocorehelpers.programming_helpers import IPythonHelpers
from ipywidgets import get_ipython # required for IPythonHelpers.cell_vars
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import requests # used by NotebookProcessor.get_running_notebook_path(...)
from IPython.display import display, Javascript

import nbformat as nbf # convert_script_to_notebook


# @function_attributes(short_name=None, tags=['notebook', 'conversion', 'batch'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-10-30 07:45', related_items=[])
def convert_script_to_notebook(script_path: str, notebook_path: str, custom_delimiter: Optional[str]="# ~ # NBSplit", enable_auto_reload:bool=True, enable_qt_interactive:bool=True) -> None:
    """ Converts a python script to a jupyter notebook (.ipynb) based on either its markdown headers or a custom_delimiter. 
    WORKING!
    # Split script based on custom delimiter
    custom_delimiter = "# ~ # NBSplit"
    
    NOTE: unless custom_delimiter=None, no markdown cells will be created.
    
    Useful for building interactive notebooks for testing batch computations
    
    # Usage:
     
        from pyphocorehelpers.notebook_helpers import convert_script_to_notebook
        
        script_path = Path(r"K:\scratch\gen_scripts\run_kdiba_gor01_one_2006-6-12_15-55-31\run_kdiba_gor01_one_2006-6-12_15-55-31.py").resolve()
        script_dir = script_path.parent.resolve()
        notebook_path = script_path.with_suffix('.ipynb')
        convert_script_to_notebook(script_path, notebook_path)
        # convert_script_to_notebook(script_path, notebook_path, custom_delimiter=None)

    
    """
    with open(script_path, 'r') as script_file:
        lines = script_file.readlines()

    nb = nbf.v4.new_notebook()
    cells = []
    
    if not isinstance(notebook_path, Path):
        notebook_path = Path(notebook_path).resolve()

    # Create the constant first cell with the specific content
    constant_first_cell_content: str = """%config IPCompleter.use_jedi = False
# %xmode Verbose
# %xmode context
%pdb off
"""

    if enable_auto_reload:
        _auto_reload_block: str = """
%load_ext autoreload
%autoreload 3
"""
        constant_first_cell_content = f"{constant_first_cell_content}{_auto_reload_block}"

    _last_import_block: str = """
import sys
from pathlib import Path

"""
    constant_first_cell_content = f"{constant_first_cell_content}{_last_import_block}"
    if enable_qt_interactive:
        _qt_interactive_import_block: str = """
# required to enable non-blocking interaction:
%gui qt5"""                                            
        constant_first_cell_content = f"{constant_first_cell_content}{_qt_interactive_import_block}"


    first_cell = nbf.v4.new_code_cell(constant_first_cell_content)
    first_cell.metadata.tags = ["run-main"]
    cells.append(first_cell)
    

    code_buffer = []

    def flush_code_buffer():
        if code_buffer:
            code_cell = nbf.v4.new_code_cell(''.join(code_buffer))
            code_cell.metadata.tags = ["run-main"]
            cells.append(code_cell)
            code_buffer.clear()

    for line in lines:
        if custom_delimiter is not None:
            if line.strip().startswith(custom_delimiter):
                flush_code_buffer()  # Create a new cell when custom delimiter is found
            else:
                line = line.replace('__file__', f"r'{notebook_path.as_posix()}'") ## replace any __File__ instances because they won't work in the notebook
                code_buffer.append(line) 
        else:
              # no custom delimiter
            if line.startswith('# '):  # Treat lines starting with '# ' as section titles
                flush_code_buffer()
                markdown_cell = nbf.v4.new_markdown_cell(line[2:].strip())
                markdown_cell.metadata.tags = ["run-main"]
                cells.append(markdown_cell)
            else:
                line = line.replace('__file__', f"r'{notebook_path.as_posix()}'") ## replace any __File__ instances because they won't work in the notebook
                code_buffer.append(line)

    # Flush any remaining code
    flush_code_buffer()

    nb.cells = cells

    with open(notebook_path, 'w') as notebook_file:
        nbf.write(nb, notebook_file)
          

def _safely_remove_all_module_registered_callbacks():
    """ safely remove all callbacks registered by my custom module even if we lost references to them

    from pyphocorehelpers.notebook_helpers import _safely_remove_all_module_registered_callbacks

    """
    ip = get_ipython()
    # print(f"ip.events.callbacks: {ip.events.callbacks}")
    # ip.events.callbacks:
        # {'pre_execute': [<bound method InteractiveShell._clear_warning_registry of <ipykernel.zmqshell.ZMQInteractiveShell object at 0x0000021DBB8B56D0>>],
        # 'pre_run_cell': [<bound method AutoreloadMagics.pre_run_cell of <IPython.extensions.autoreload.AutoreloadMagics object at 0x0000021DBBA59940>>,
        # <function pyphocorehelpers.notebook_helpers.NotebookCellExecutionLogger.record_execution_details.<locals>.pre_run_cell(info)>,
        # <function pyphocorehelpers.notebook_helpers.NotebookCellExecutionLogger.record_execution_details.<locals>.cell_create_or_modify(info)>],
        # 'post_execute': [<bound method AutoreloadMagics.post_execute_hook of <IPython.extensions.autoreload.AutoreloadMagics object at 0x0000021DBBA59940>>,
        # <function matplotlib.pyplot._draw_all_if_interactive() -> 'None'>],
        # 'post_run_cell': [<function pyphocorehelpers.notebook_helpers.NotebookCellExecutionLogger.record_execution_details.<locals>.post_run_cell(result)>],
        # 'shell_initialized': []}
    for a_callback_type, cb_list in ip.events.callbacks.items():
        for a_fn in cb_list:
            if a_fn.__module__ in ['pyphocorehelpers.notebook_helpers']:
                ip.events.unregister(a_callback_type, a_fn)


@define(slots=False, eq=False)
class CellExecution:
    start_time: datetime = field(factory=datetime.now)
    end_time: datetime = field(default=None)
    duration: float = field(default=None)
    status: str = field(default="running")
    output: str = field(default="", metadata={'notes': 'Added field to store output history'})  # Added field to store output history

    def to_dict(self):
        return attr.asdict(self, recurse=True)
        # return attr.asdict(self, recurse=True, value_serializer=self.serializer)

    # @staticmethod
    # def serializer(value, attr, obj, is_key):
    #     if isinstance(value, datetime):
    #         return value.isoformat()
    #     if isinstance(value, (list, dict)):
    #         return value
    #     return str(value)
    


@define(slots=False, eq=False)
class CellInfo:
    created_at: datetime = field(factory=datetime.now)
    modified_at: datetime = field(default=None)
    code: str = field(default="")
    executions: List[CellExecution] = field(factory=list)

    def to_dict(self):
        return attr.asdict(self, recurse=True) # , value_serializer=self.serializer

    # @staticmethod
    # def serializer(value, attr, obj, is_key):
    #     if isinstance(value, datetime):
    #         return value.isoformat()
    #     if isinstance(value, (list, dict)):
    #         return value
    #     return str(value)
    


@define(slots=False, eq=False)
class NotebookCellExecutionLogger:
    """ Logs jupyter notebook execution activity and history
    
    Usage:
        import IPython
        from pyphocorehelpers.programming_helpers import IPythonHelpers
        from pyphocorehelpers.notebook_helpers import NotebookCellExecutionLogger

        _notebook_path:Path = Path(IPythonHelpers.try_find_notebook_filepath(IPython.extract_module_locals())).resolve() # Finds the path of THIS notebook
        _notebook_execution_logger: NotebookCellExecutionLogger = NotebookCellExecutionLogger(notebook_path=_notebook_path, enable_logging_to_file=True) # Builds a logger that records info about this notebook

    """
    notebook_path: Path = field()
    enable_logging_to_file: bool = field(default=True)
    debug_print: bool = field(default=False)
    log_file: Path = field(default=None, init=False)
    cell_info: Dict[str, CellInfo] = field(default=Factory(dict))
    use_logging_subdirectory: bool = field(default=True, metadata={'notes': "if true, logs to the notebook's parent folder/._cell_execution_logs subdirectory"}) # 
    _callback_references: Dict[str, List[Callable]] = field(default=Factory(dict))

    def __attrs_post_init__(self):
        _did_logging_file_change: bool = self.rebuild_logging_file_info()
        self.register_callbacks()

    def __del__(self):
        self.unregister_callbacks()



    def rebuild_logging_file_info(self) -> bool:
        """ called when options change to recompute the logging output variables:

        Updates:
            self.log_file

        """
        assert self.notebook_path.exists()
        notebook_directory = self.notebook_path.parent.resolve()
        notebook_filename: str = self.notebook_path.stem
        log_filename = f"_cell_execution_log_{notebook_filename}.json"
        log_filename: str = sanitize_filename_for_Windows(log_filename)
        
        if self.use_logging_subdirectory:
            log_directory = notebook_directory.joinpath('._cell_execution_logs').resolve()
            log_directory.mkdir(exist_ok=True)
        else:
            log_directory = notebook_directory

        new_log_File_directory = log_directory.joinpath(log_filename).resolve()

        did_logging_file_change: bool = ((self.log_file is None) or (self.log_file != new_log_File_directory))
        self.log_file = log_directory.joinpath(log_filename) # update the logging file
        return did_logging_file_change


    
    def update_log_file(self):
        if self.enable_logging_to_file:
            with open(self.log_file, 'w') as f:
                # cell_info_dict = {k:attr.asdict(v, recurse=True) for k, v in self.cell_info.items()}
                cell_info_dict = {k: v.to_dict() for k, v in self.cell_info.items()}
                json.dump(cell_info_dict, f, default=str, indent=4)



    def register_callbacks(self):
        """ main start function """
        from ipywidgets import get_ipython # required for IPythonHelpers.cell_vars

        ip = get_ipython()
        self.unregister_callbacks() ## unregister existing callbacks

        def pre_run_cell(info):
            cell_id = info.cell_id
            if cell_id not in self.cell_info:
                self.cell_info[cell_id] = CellInfo(code=info.raw_cell)
            self.cell_info[cell_id].executions.append(CellExecution())
            self.update_log_file()

        def post_run_cell(result):
            cell_id = result.info.cell_id
            if cell_id in self.cell_info and self.cell_info[cell_id].executions:
                exec_info = self.cell_info[cell_id].executions[-1]
                exec_info.end_time = datetime.now()
                exec_info.duration = (exec_info.end_time - exec_info.start_time).total_seconds()
                exec_info.status = "failed" if result.error_in_exec else "success"
                if result.result is None:
                    exec_info.output = ''
                else:
                    # Capture the output. A list of things
                    try:
                        # might be a list/tuple of strings
                        exec_info.output = '_________________________________________________________________ \n'.join([str(v) for v in result.result]) # combine multiple outputs into a single cell # bool object is not iterable
                    except BaseException as err:
                        # not iterable most likely
                        exec_info.output = str(result.result) 
    
                    if self.debug_print:
                        print(f"Cell executed in: {_format_time(exec_info.duration)}")

                self.update_log_file()

        def cell_create_or_modify(info):
            cell_id = info.cell_id
            if cell_id in self.cell_info:
                self.cell_info[cell_id].modified_at = datetime.now()
                self.cell_info[cell_id].code = info.raw_cell
            else:
                self.cell_info[cell_id] = CellInfo(code=info.raw_cell)
            self.update_log_file()

        # ip.events.register('pre_run_cell', pre_run_cell)
        # ip.events.register('post_run_cell', post_run_cell)
        # ip.events.register('pre_run_cell', cell_create_or_modify)

        ## hardcoded
        self._callback_references = {'pre_run_cell': [pre_run_cell, cell_create_or_modify],
            'post_run_cell': [post_run_cell],
        }

        for a_callback_type, a_callback_fns_list in self._callback_references.items():
            # a_callback_type: like 'pre_run_cell'
            for a_fn in a_callback_fns_list:
                ip.events.register(a_callback_type, a_fn)


    def unregister_callbacks(self):
        """ unregister all ipynb callbacks 
        """
        ip = get_ipython()
        if ip:
            try:
                for a_callback_type, a_callback_fns_list in self._callback_references.items():
                    # a_callback_type: like 'pre_run_cell'
                    for a_fn in a_callback_fns_list:
                        ip.events.unregister(a_callback_type, a_fn)
            except BaseException as err:
                print(f'could not remove all callbacks due to {err}')
            finally:
                ## ensure that all are removed no matter what:
                _safely_remove_all_module_registered_callbacks
                self._callback_references = {} # empty


@define(slots=False)
class NotebookProcessor:
    """ processes Jupyter Notebooks

    from pyphocorehelpers.notebook_helpers import NotebookProcessor

    notebook_path = Path(r"C:/Users/pho/repos/Spike3DWorkEnv/Spike3D/ReviewOfWork_2024-01-22.ipynb").resolve()
    processor = NotebookProcessor(path=notebook_path)

    History:
        `pyphocorehelpers.programming_helpers.NotebookProcessor` -> `pyphocorehelpers.notebook_helpers.NotebookProcessor`
        
    Usage:
    
        from pyphocorehelpers.notebook_helpers import NotebookCellExecutionLogger, NotebookProcessor

        _notebook_path:Path = Path(IPythonHelpers.try_find_notebook_filepath(IPython.extract_module_locals())).resolve() # Finds the path of THIS notebook
        _notebook_execution_logger: NotebookCellExecutionLogger = NotebookCellExecutionLogger(notebook_path=_notebook_path, enable_logging_to_file=False) # Builds a logger that records info about this notebook
        _notebook_processor: NotebookProcessor = NotebookProcessor(path=_notebook_path)

        ## Capturing the history:
        _notebook_processor.export_notebook_run_history()

        
        ## indexed by the cell_idx

        in_cell_ids: List[int] = list(In.keys())
        out_cell_ids: List[int] = list(Out.keys())
        # an_out: Dict[int, Any] = Out
        in_cell_ids
        out_cell_ids

    """
    path: Path = field()
    cells: List = field(default=Factory(list))

    def __attrs_post_init__(self):
        self.load_cells()

    def load_cells(self):
        self.cells = IPythonHelpers.extract_cells(self.path)
        print(self.cells)

    def get_cells_with_tags(self) -> Dict[str, List]:
        """ returns a dictionary with keys equal to all tags, and values containing the list of cells containing those tags.
        """
        # _out = []
        _out = {}
        for i, cell in enumerate(self.cells):
            _curr_tags = cell['metadata'].get('tags', [])
            for a_tag in _curr_tags:
                if a_tag not in _out:
                    _out[a_tag] = [] # init to new array
                # update the value:
                _curr_cell = {'i': i, 'content': cell['source'], 'tags': cell['metadata'].get('tags', [])}
                _out[a_tag].append(_curr_cell)            
            # _out.append(_curr_cell)
        return _out
    
    
    def get_cells_with_any_tags(self) -> List:
        """ returns all cells containing any tags.
        """
        return [{'i': i, 'content': cell['source'], 'tags': cell['metadata'].get('tags', [])}
                 for i, cell in enumerate(self.cells) if cell['metadata'].get('tags', [])]
    

    def get_cells_with_tag(self, tag: str) -> List:
        return [{'i': i, 'content': cell['source'], 'tags': cell['metadata'].get('tags')}
                for i, cell in enumerate(self.cells) if (tag in cell['metadata'].get('tags', []))]


    def get_cells_with_run_groups(self) -> Dict[str, List]:
        """
        
        "metadata": {
            "notebookRunGroups": {
                "groupValue": "1"
            }
        },
        
        """
        _out = {}
        for i, cell in enumerate(self.cells):
            # _curr_run_groups = cell['metadata'].get('notebookRunGroups', {}).get("groupValue", None)
            a_run_group = cell['metadata'].get('notebookRunGroups', {}).get("groupValue", None)
            if a_run_group is not None:
            # for a_run_group in _curr_run_groups:
                if a_run_group not in _out:
                    _out[a_run_group] = [] # init to new array
                # update the value:
                _curr_cell = {'i': i, 'content': cell['source'], 'notebookRunGroups': cell['metadata'].get('notebookRunGroups'),
                            #   'tags': cell['metadata'].get('tags', []),
                              }
                _out[a_run_group].append(_curr_cell)            
            # _out.append(_curr_cell)
        return _out
    

    def get_cells_with_images(self):
        cells_with_images = []
        for i, cell in enumerate(self.cells):
            cell_content = cell['source']
            cell_attachments = cell.get('attachments', None)
            if cell_attachments:
                cells_with_images.append({'i': i, 'content': cell_content, 'attachments': cell_attachments})

        return cells_with_images



    def get_empty_cells(self):
        return [cell for i, cell in enumerate(self.cells) if not cell['source'] or cell['source'].isspace()]


    def remove_empty_cells_and_save(self, new_path):
        """
        ## Remove all empty cells, and save the resultant notebook as the current notebook with the '_cleaned' filename suffix (but same extention)
        new_path = processor.path.with_stem(f'{processor.path.stem}_cleaned').resolve()
        processor.remove_empty_cells_and_save(new_path=new_path)


        """
        # spawn a new list omitting empty cells
        original_n_cells = len(self.cells)
        cleaned_cells = [cell for i, cell in enumerate(self.cells) if cell['source'] and not cell['source'].isspace()]
        post_clean_n_cells = len(cleaned_cells)
        n_changed_cells = original_n_cells - post_clean_n_cells
        if n_changed_cells > 0:
            print(f'original_n_cells: {original_n_cells}, post_clean_n_cells: {post_clean_n_cells}, n_changed_cells: {n_changed_cells} cells changed. Saving to {new_path}...')
            # Commit changes back to a notebook
            IPythonHelpers.write_notebook(cleaned_cells, new_path)
            print(f"Cleaned notebook saved to: {new_path}")
        else:
            print(f'no cells changed.')

    @classmethod
    def get_running_notebook_path(cls, debug_print=True):
        """ 
        
        NotebookProcessor.get_running_notebook_path()
        
        """
        import ipykernel
        import os
        import re
        from notebook import notebookapp
        fullpath_connection_file = ipykernel.get_connection_file()
        connection_file = os.path.basename(fullpath_connection_file)
        kernel_id = connection_file.split('-', 1)[1].split('.')[0]
        
        jupyter_runtime_dir = Path(notebookapp.jupyter_runtime_dir()).resolve()
        assert jupyter_runtime_dir.exists()
        jupyter_running_servers = list(notebookapp.list_running_servers(runtime_dir=jupyter_runtime_dir))
        

        if debug_print:
            print(f'jupyter_runtime_dir: "{jupyter_runtime_dir}"')
            print(f'fullpath_connection_file: "{fullpath_connection_file}"')
            print(f'connection_file: "{connection_file}"')
            print(f'kernel_id: "{kernel_id}"')
            print(f'jupyter_running_servers: "{jupyter_running_servers}"')
        
        # for srv in notebookapp.list_running_servers():
        for srv in jupyter_running_servers:
            if debug_print:
                print(f'srv: {srv}')
            response = requests.get(os.path.join(srv['url'], 'api/sessions'), params={'token': srv.get('token', '')})
            for sess in response.json():
                if sess['kernel']['id'] == kernel_id:
                    return os.path.join(srv['notebook_dir'], sess['notebook']['path'])
        return None



    @classmethod
    def get_running_vscode_jupyter_server_info(cls, debug_print=True):
        """ gets the connection information for the current notebook
        
        Usage:
        
            from pyphocorehelpers.notebook_helpers import NotebookProcessor

            latest_connection_file, connection_info = NotebookProcessor.get_running_vscode_jupyter_server_info()
            connection_info

        
        Outputs:
        
        Connection info: {
            "key": "8d669f8c-24d6-4d50-b32c-d3cae7ae7b0d",
            "signature_scheme": "hmac-sha256",
            "transport": "tcp",
            "ip": "127.0.0.1",
            "hb_port": 9005,
            "control_port": 9006,
            "shell_port": 9007,
            "stdin_port": 9008,
            "iopub_port": 9009,
            "kernel_name": "spike3d-2025"
        }


        """
        import json
        from jupyter_core.paths import jupyter_runtime_dir
        import os
        import glob
        
        # Get the ID of the current kernel
        import IPython
        ipython = IPython.get_ipython()
        connection_file = ipython.kernel.config.get('IPKernelApp', {}).get('connection_file', None) ## get directly from config - 'c:\\Users\\pho\\AppData\\Roaming\\jupyter\\runtime\\kernel-v3c54b3d2299720ec05d3bff91d2d179ae240ad212.json'
        if (connection_file is not None) and os.path.exists(connection_file):
            ## good connection file, continue
            pass
        else:
            ## try to build the path:
            current_kernel_id = ipython.kernel.session.key # ipython.kernel.session.msg_id            
            # ipython.kernel.ident
            # 'a681b47c-ef8c-4619-8316-2d129842ed4e'

            if debug_print:
                print(f"Current kernel ID: {current_kernel_id}")
            
            # Find the connection file for this specific kernel
            connection_file = os.path.join(jupyter_runtime_dir(), f'kernel-{current_kernel_id}.json')
            
            if not os.path.exists(connection_file):
                # Fallback to searching
                connection_files = glob.glob(os.path.join(jupyter_runtime_dir(), 'kernel-*.json'))
                if debug_print:
                    print(f'Falling back to search. Available files: {connection_files}')
                
                # Look through each file to find a matching kernel
                for file in connection_files:
                    with open(file, 'r') as f:
                        try:
                            info = json.load(f)
                            # Some connection files might have a kernel_id field
                            if 'kernel_id' in info and info['kernel_id'] == current_kernel_id:
                                connection_file = file
                                break
                        except:
                            continue
                
                # If still not found, use the original method as last resort
                if not os.path.exists(connection_file):
                    if debug_print:
                        print("Couldn't find exact kernel match, using most recent connection file")
                    connection_file = max(connection_files, key=os.path.getctime)
        

        assert (connection_file is not None)
        assert os.path.exists(connection_file)
        
        # Display the connection information
        with open(connection_file, 'r') as f:
            connection_info = json.load(f)
            
        if debug_print:
            print(f"Connection file: {connection_file}")
            print(f"Connection info: {json.dumps(connection_info, indent=4)}")
            
        return connection_file, connection_info
    


    @classmethod
    def launch_standalone_qtconsole_connected_to_existing_kernel(cls, connection_info: Optional[Path]=None, latest_connection_file: Optional[Path]=None, run_in_UV_env:bool=True, run_in_poetry_env:bool=False, debug_print=True, start_new_session:bool=False, **kwargs):
        """ gets the connection information for the current notebook
        
        Usage:
        
            from pyphocorehelpers.notebook_helpers import NotebookProcessor

            latest_connection_file, connection_info = NotebookProcessor.get_running_vscode_jupyter_server_info()
            
            NotebookProcessor.launch_standalone_qtconsole_connected_to_existing_kernel(latest_connection_file=latest_connection_file)
            

        
        Outputs:
        
        Connection info: {
            "key": "8d669f8c-24d6-4d50-b32c-d3cae7ae7b0d",
            "signature_scheme": "hmac-sha256",
            "transport": "tcp",
            "ip": "127.0.0.1",
            "hb_port": 9005,
            "control_port": 9006,
            "shell_port": 9007,
            "stdin_port": 9008,
            "iopub_port": 9009,
            "kernel_name": "spike3d-2025"
        }


        """
        assert (not (run_in_UV_env and run_in_poetry_env)), f'must run in either UV OR poetry, not both!'
        if run_in_UV_env:
            command_args = ["uv", "run"] ## run in poetry env
        elif run_in_poetry_env:
            command_args = ["poetry", "run"] ## run in poetry env
        else:
            command_args = [] ## empty list to start
        
        command_args = [*command_args, "jupyter", "qtconsole", "--existing"] ## add common args
        
        import subprocess
        if (connection_info is None) and (latest_connection_file is None):
            if debug_print:
                print(f'getting via get_running_vscode_jupyter_server_info()...')
            latest_connection_file, connection_info = cls.get_running_vscode_jupyter_server_info(debug_print=debug_print)
            assert Path(latest_connection_file).exists()
            command_args = [*command_args, latest_connection_file]
            command_str = ' '.join(command_args)
            print(f'command: `{command_str}`')
            subprocess.Popen(command_args, start_new_session=start_new_session, **kwargs)
            return True    
        elif (latest_connection_file is not None):
            ## just use the existing file
            # Launch QTConsole with the existing kernel
            assert Path(latest_connection_file).exists()
            command_args = [*command_args, latest_connection_file]
            command_str = ' '.join(command_args)
            print(f'command: `{command_str}`')
            subprocess.Popen(command_args, start_new_session=start_new_session, **kwargs)
            return True
        
        elif (latest_connection_file is None) and (connection_info is not None):
            import json
            import tempfile
            ## write out to a temp file            
            # Create a temporary connection file
            temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
            temp_file_path = temp_file.name
            with open(temp_file_path, 'w') as f:
                json.dump(connection_info, f)

            # Launch QTConsole with the existing kernel
            command_args = [*command_args, temp_file_path]
            command_str = ' '.join(command_args)
            print(f'command: `{command_str}`')
            subprocess.Popen(command_args, start_new_session=start_new_session, **kwargs)
            
            # Optional: Set up cleanup for the temp file
            # import atexit
            # atexit.register(lambda: os.unlink(temp_file_path))
            return True
        else:
            raise NotImplementedError(f'latest_connection_file: "{latest_connection_file}", connection_info: {connection_info}')
            return False
    



    @classmethod
    def export_notebook_run_history(cls, In=None, Out=None, save_path: Path = None):
        """ 
        Exports the executed cells of the current notebook session to a python file.
        
        Args:
            In (list, optional): The global 'In' list from the notebook. If None, attempts to auto-discover.
            Out (dict, optional): The global 'Out' dict. Currently unused in this implementation.
            save_path (Path, optional): Destination file. Defaults to 'session_history.py'.
        """
        
        # 1. Auto-discover 'In' if not provided
        if In is None:
            ip = get_ipython()
            if ip and 'In' in ip.user_ns:
                In = ip.user_ns['In']
            else:
                print("Error: Could not find execution history. Are you running this from a Jupyter Notebook?")
                return

        # 2. Handle Filename Generation
        if save_path is None:           
            parent_path = Path('EXTERNAL/NOTEBOOK_RUN_LOGS').resolve()
            if (not parent_path.exists()) or (not parent_path.is_dir()):
                parent_path = None
 
            # Create a timestamp string: YYYY-MM-DD_HH-MM-SS
            # Example result: notebook_history_2026-01-12_13-30-05.py
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"notebook_history_{timestamp}.py"
            if parent_path is not None:
                save_path = parent_path.joinpath(filename).resolve()
            else:
                save_path = Path(filename).resolve()
        else:
            save_path = Path(save_path).resolve()
            

        # 3. Write to file
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(f"# History exported on {save_path.stat().st_mtime if save_path.exists() else 'New File'}\n")
                f.write(f"# Source: {cls.__name__}\n\n")
                
                for i, code in enumerate(In):
                    # Skip empty cells or purely whitespace
                    if code and code.strip(): 
                        f.write(f"# Input [{i}]\n{code}\n\n")
                        
            print(f"Successfully saved execution history to: {save_path}")
            
        except Exception as e:
            print(f"Failed to write history file: {e}")



    # from IPython.display import display, Javascript

    # def add_cell_below():
    # 	# js_code = """
    # 	# var cell = Jupyter.notebook.insert_cell_below();
    # 	# """
    # 	# display(Javascript(js_code))
    # 	## VSCode:
    # 	display({
    # 	"cell.insertCodeBelow": {
    # 		"code": 'print("This is a new cell")'
    # 	}
    # 	}, raw=True)
    
