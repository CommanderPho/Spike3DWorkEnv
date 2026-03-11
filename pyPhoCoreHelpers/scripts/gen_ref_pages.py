"""Generate the code reference pages and navigation.

See https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages
Requires

poetry add mkdocs-gen-files mkdocs-literate-nav mkdocs-section-index mkdocs-matplotlib mkdocs-jupyter

# mkdocs-gen-files mkdocs-literate-nav mkdocs-section-index mkdocs-matplotlib mkdocs-jupyter

mkdocs-gen-files
mkdocs-literate-nav
mkdocs-section-index
mkdocs-matplotlib
mkdocs-jupyter

"""
import os
import sys
from pathlib import Path

import mkdocs_gen_files

debug_print: bool = True

nav = mkdocs_gen_files.Nav()

scripts_dir = Path(os.path.dirname(os.path.abspath(__file__))) # /home/halechr/repos/Spike3D/docs
print(f'scripts_dir: "{scripts_dir}"')
root_dir = scripts_dir.parent # Spike3D root repo dir

root_dir_path = Path(root_dir).resolve()
assert root_dir_path.exists(), f"root_dir_path: '{root_dir_path}' does not exist!"
docs_dir: Path = root_dir_path.joinpath('docs').resolve() # /home/halechr/repos/Spike3D/docs
assert docs_dir.exists(), f"docs_dir: '{docs_dir}' does not exist!"
# docs_dir = Path(os.path.dirname(os.path.abspath(__file__))) # /home/halechr/repos/Spike3D/docs
print(f'docs_dir: {docs_dir}')
docs_reference_subdir: Path = docs_dir.joinpath('reference').resolve()
if not docs_reference_subdir.exists():
    docs_reference_subdir.mkdir(exist_ok=True)

# sources_path: Path = root_dir_path.joinpath('src', 'pyphocorehelpers').resolve()
sources_path: Path = root_dir_path.joinpath('src').resolve()
assert sources_path.exists(), f"sources_path: '{sources_path}' does not exist!"
print(f'sources_path: "{sources_path}"')

# str_path_root: str = "src"
str_path_root: str = sources_path.as_posix()


for path in sorted(sources_path.rglob("*.py")):
    if debug_print:
        print(f'for path "{path}"')
    rel_module_path = path.relative_to(str_path_root).with_suffix("")
    rel_doc_path = path.relative_to(str_path_root).with_suffix(".md")
    full_doc_path = docs_reference_subdir.joinpath(rel_doc_path)

    parts = tuple(rel_module_path.parts)
    
    if parts[-1] == "__init__":
        parts = parts[:-1]
        rel_doc_path = rel_doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue
    
    if debug_print:
        print(f'\t"parts: {parts}"')
        print(f'\t"rel_doc_path: {rel_doc_path}"')
        
    if len(parts) == 0:
        if debug_print:
            print(f'\t\tparts empty. Skipping.')        
        continue # skip
    else:
        ## Non-empty parts
        if debug_print:
             print(f'\t\tparts good. len(parts): {len(parts)}: {rel_doc_path.as_posix()}"')
        nav[parts] = rel_doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
