# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

This is a UV workspace monorepo (`neuro-monorepo`) for hippocampal electrophysiology place cell analysis with 3D visualization. It contains 4 packages: `NeuroPy`, `pyPhoCoreHelpers`, `pyPhoPlaceCellAnalysis`, and `Spike3D`. There are no external services (databases, web servers) required — this is a pure scientific computing toolkit.

### Python and dependencies

- **Python 3.9** is required (`>=3.9, <3.12`). The UV-managed Python 3.9.13 is used.
- **UV** is the mandated package manager. Run `uv sync --all-extras` from the workspace root.
- System packages needed: `python3.9-dev`, `libhdf5-dev`, `libcairo2-dev`, `libgl1-mesa-dev`, `xvfb`, and Qt5 xcb libs. The default `c++` must point to `g++` (not clang) for native extension compilation (e.g. `annoy`).

### Running tests

- `uv run python -m pytest NeuroPy/tests/ -v` — runs NeuroPy tests. Skip `test_position.py` (uses relative import `unittesting_extensions` that needs the tests dir as CWD or on sys.path).
- `uv run python -m pytest pyPhoPlaceCellAnalysis/tests/ -v` — runs pyPhoPlaceCellAnalysis tests. Skip GUI tests (`test_externalGUI.py`, `test_custom_pyqt_placefield_visibility_control.py`, `test_CustomSpikeRasters.py`) and `test_HDF5_functions.py` in headless environments.
- Many tests depend on DVC-tracked data files (Google Drive) that are not available in cloud VMs. Tests that don't require data files pass cleanly.

### Lint and type checking

- `uv run python -m pyflakes <file>` for lint checks.
- `uv run python -m pyrefly check <file>` for type checking (pyrefly is installed, pyright is not in the default deps).

### Known caveats

- **PyVista + VTK compatibility**: The workspace overrides vedo's vtk constraint to `vtk>=9.2.4`. pyvista 0.36.x has runtime issues with vtk 9.6.x (e.g. `vtkPoints` missing `dtype` attribute). Avoid importing modules that trigger `pv.Sphere()` at module load time (e.g. `pyphoplacecellanalysis.Pho3D.PyVista.spikeAndPositions`). Non-PyVista computation and analysis paths work fine.
- **GUI components** (PyQt5, PyVista, Napari) require a display server. Use `xvfb-run` for headless execution or set `QT_QPA_PLATFORM=offscreen`.
- **Workspace source references**: Sub-package `tool.uv.sources` entries for other workspace members must use `{ workspace = true }` (not path references) for UV workspace resolution.
- The `Spike3D/pyproject.toml` `[project.scripts]` entries are commented out because they pointed to shell scripts rather than Python entry points.
- Spike3D uses `hatchling` as its build backend with `packages = ["scripts"]` to avoid setuptools auto-discovery conflicts.
