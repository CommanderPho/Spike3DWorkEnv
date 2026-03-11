"""Generate documentation stubs for all Python modules in src/ directory.

This script uses mkdocs-gen-files to automatically create virtual markdown files
for every Python module found in the src/ directory. It also generates a
SUMMARY.md file that mkdocs-literate-nav uses to build the navigation structure.

Usage:
    This script is automatically run by mkdocs-gen-files plugin when building docs.
    It can also be run standalone for testing.

Requirements:
    - mkdocs-gen-files
    - mkdocs-literate-nav
    - mkdocstrings[python]

See: https://mkdocstrings.github.io/recipes/#automatic-code-reference-pages
"""
import os
from pathlib import Path

import mkdocs_gen_files

# Configuration
DEBUG = False
REFERENCE_DIR = "reference"  # Output directory for generated docs

# Get project root directory
scripts_dir = Path(__file__).parent.resolve()
root_dir = scripts_dir.parent.resolve()
src_dir = root_dir / "src"

if not src_dir.exists():
    raise FileNotFoundError(f"Source directory not found: {src_dir}")

# When running standalone, we need to ensure mkdocs context is initialized
# The mkdocs_gen_files.open() call will trigger plugin initialization
# We've already configured autorefs in mkdocs.yml, so it should work

# Initialize navigation structure
nav = mkdocs_gen_files.Nav()

# Walk through all Python files in src/
for py_file in sorted(src_dir.rglob("*.py")):
    # Skip __pycache__ directories
    if "__pycache__" in py_file.parts:
        continue
    
    # Get relative path from src/ directory
    rel_module_path = py_file.relative_to(src_dir).with_suffix("")
    rel_doc_path = rel_module_path.with_suffix(".md")
    
    # Convert to module parts
    parts = tuple(rel_module_path.parts)
    
    # Handle __init__.py files (they become index.md for packages)
    if parts[-1] == "__init__":
        parts = parts[:-1]
        if len(parts) == 0:
            continue  # Skip root __init__.py if it exists
        rel_doc_path = rel_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue  # Skip __main__.py files
    
    # Skip empty parts
    if len(parts) == 0:
        continue
    
    # Build full documentation path
    full_doc_path = Path(REFERENCE_DIR) / rel_doc_path
    
    if DEBUG:
        print(f"Processing: {py_file}")
        print(f"  Module parts: {parts}")
        print(f"  Doc path: {full_doc_path}")
    
    # Add to navigation
    nav[parts] = str(rel_doc_path)
    
    # Generate markdown stub with mkdocstrings syntax
    module_identifier = ".".join(parts)
    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        f.write(f"::: {module_identifier}\n")
    
    # Set edit path so users can jump to source from docs
    mkdocs_gen_files.set_edit_path(full_doc_path, py_file)

# Generate SUMMARY.md for mkdocs-literate-nav
with mkdocs_gen_files.open(f"{REFERENCE_DIR}/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())

if DEBUG:
    print(f"\nGenerated documentation stubs in {REFERENCE_DIR}/")
    print(f"Generated navigation file: {REFERENCE_DIR}/SUMMARY.md")

