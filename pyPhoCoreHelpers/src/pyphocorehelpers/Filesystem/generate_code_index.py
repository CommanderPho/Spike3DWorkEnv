import subprocess
import pathlib
from typing import Optional

from pyphocorehelpers.Filesystem.source_code_helpers import find_py_files

def build_code_index(project_path, exclude_dirs=[], project_name:Optional[str]=None, details_print=True):
    """ 2023-05-11 - Tries to build a CodeQuery code index. Not quite working.
    from pyphocorehelpers.Filesystem.generate_code_index import build_code_index
    Original Bash Commands:
    

        cd "C:/Users/pho/repos/Spike3DWorkEnv/NeuroPy/neuropy"
        dir /b/a/s *.py    > cscope.files
        pycscope -i cscope.files
        ctags --fields=+i -n -L cscope.files
        cqmakedb -s .\myproject.db -c cscope.out -t tags -p


        cd "C:/Users/pho/repos/Spike3DWorkEnv/pyPhoCoreHelpers/src"
        dir /b/a/s *.py    > cscope.files
        pycscope -i cscope.files
        ctags --fields=+i -n -L cscope.files
        cqmakedb -s .\myproject.db -c cscope.out -t tags -p


        cd "C:/Users/pho/repos/Spike3DWorkEnv/pyPhoPlaceCellAnalysis/src"
        dir /b/a/s *.py | find /i /v "External\\" | findstr /i /v "\\External\\"   > cscope.files 

        # NOTE: Works when excluding all External/* files
        pycscope -i cscope.files
        ctags --fields=+i -n -L cscope.files
        cqmakedb -s .\myproject.db -c cscope.out -t tags -p

        
        # This does not work: the idea of adding them all to a shared database
        cqmakedb -s ..\..\full_project.db -c cscope.out -t tags -p

        
        
        
    
    Example:
        project_path = "C:/Users/pho/repos/Spike3DWorkEnv/pyPhoPlaceCellAnalysis/src"
        exclude_dirs = ["pyphoplacecellanalysis/External"]
        
    Usage:
        from pyphocorehelpers.Filesystem.generate_code_index import build_code_index
        project_outputs = build_code_index("C:/Users/pho/repos/Spike3DWorkEnv/NeuroPy/neuropy")
        project_path, project_db_file_path, tags_file_path, cscope_out_file_path, cscope_files_file_path = project_outputs # unpack


    """
    project_path = pathlib.Path(project_path)
    assert project_path.exists()
    if project_name is None:
        # infer project name from the path:
        project_name = project_path.name
    if details_print:
        print(f'project_name: {project_name}')

    cscope_files_file_path = project_path / "cscope.files"
    cscope_out_file_path = project_path / "cscope.out"
    tags_file_path = project_path / "tags"
    project_db_file_path = project_path / "myproject.db"

    # Find all .py files in the project directory and its subdirectories
    included_py_files = find_py_files(project_path, exclude_dirs=exclude_dirs)
    if details_print:
        print(f'\tfound {len(included_py_files)} .py files in project.')

    # Write the file paths to cscope.files
    with open(cscope_files_file_path, "w") as f:
        for file_path in included_py_files:
            f.write(str(file_path) + "\n")

    assert cscope_files_file_path.exists()

    # Generate the cscope index
    subprocess.run(["pycscope", "-i", str(cscope_files_file_path)], cwd=str(project_path), check=True)

    # Generate the ctags index
    subprocess.run(["ctags", "--fields=+i", "-n", "-L", str(cscope_files_file_path)], cwd=str(project_path), check=True)
    assert cscope_out_file_path.exists()

    # Generate the CodeQL database
    subprocess.run(["cqmakedb", "-s", str(project_db_file_path), "-c", str(cscope_out_file_path), "-t", str(tags_file_path), "-p"], cwd=str(project_path), check=True)

    return project_path, project_db_file_path, tags_file_path, cscope_out_file_path, cscope_files_file_path


if __name__ == "__main__":
    build_code_index("C:/Users/pho/repos/Spike3DWorkEnv/NeuroPy/neuropy")
    build_code_index("C:/Users/pho/repos/Spike3DWorkEnv/pyPhoCoreHelpers/src")
    build_code_index("C:/Users/pho/repos/Spike3DWorkEnv/pyPhoPlaceCellAnalysis/src", exclude_dirs = ["pyphoplacecellanalysis/External"])





# "C:\Program Files\Microsoft VS Code\Code.exe" --goto "%f:%n"