---
name: Recursive deps update for uv sync
overview: Resolve the pyvista version conflict between Spike3D and pyPhoCoreHelpers, then iteratively fix any further lock/sync failures by updating dependency versions across the workspace until `uv sync --all-extras` succeeds.
todos: []
isProject: false
---

# Recursive dependency update for `uv sync --all-extras`

## Root cause of current failure

The resolver fails because **pyvista** version ranges do not overlap:

- **[pyPhoCoreHelpers](D:\pho\repos\Spike3DEnv\pyPhoCoreHelpers\pyproject.toml)** (dependency-group `viz`): `pyvista>=0.43.0,<0.44`
- **[Spike3D](D:\pho\repos\Spike3DEnv\Spike3D\pyproject.toml)**: `pyvista>=0.36.1,<0.37` and `pyvistaqt>=0.9.0,<0.10`

Spike3D also depends on `pyphocorehelpers` (workspace), and the root [pyproject.toml](D:\pho\repos\Spike3DEnv\pyproject.toml) pulls in all four workspace members with default groups. So when resolving with `--all-extras` / default-groups, both pyvista ranges are required and are unsatisfiable.

**Compatibility note:** PyVistaQt 0.11.x on PyPI declares `pyvista>=0.32.0` only, so it is compatible with pyvista 0.43. Upgrading Spike3D to pyvista 0.43.x and pyvistaqt 0.11.x is the correct direction.

---

## Implementation plan

### Phase 1: Resolve pyvista / pyvistaqt conflict

1. **Spike3D** [Spike3D/pyproject.toml](D:\pho\repos\Spike3DEnv\Spike3D\pyproject.toml)
  - Change `pyvista>=0.36.1,<0.37` → `pyvista>=0.43.0,<0.44` (align with pyPhoCoreHelpers:viz).  
  - Change `pyvistaqt>=0.9.0,<0.10` → `pyvistaqt>=0.11.0,<0.12` (current PyVistaQt 0.11.3 supports pyvista 0.43).
2. **pyPhoCoreHelpers**
  - No change; already on `pyvista>=0.43.0,<0.44`.
3. **Optional consistency**
  - [pyPhoCoreHelpers/templating/base_pyproject.toml_fragment.toml](D:\pho\repos\Spike3DEnv\pyPhoCoreHelpers\templating\base_pyproject.toml_fragment.toml) currently has `pyvista = "^0.38.0"`. If this fragment is used to generate configs that share the same environment as the main pyproject, update to `^0.43.0` so templates stay aligned.

### Phase 2: Lock and sync; handle next conflicts

1. From repo root run:
  - `uv lock`
  - `uv sync --all-extras`
2. If resolution or sync still fails:
  - Read the new solver error (e.g. another package or extra with an incompatible range).
  - Update the **declaring** package’s `pyproject.toml` to a newer compatible range (or relax the range) and repeat from step 4.

Likely secondary conflicts (only if they appear):

- **NeuroPy** [NeuroPy/pyproject.toml](D:\pho\repos\Spike3DEnv\NeuroPy\pyproject.toml): Very old pins `numpy~=1.20` and `scipy~=1.6`. The rest of the workspace uses `numpy>=1.23` and `scipy>=1.10`. If the solver or sync fails on numpy/scipy, relax NeuroPy to e.g. `numpy>=1.23,<2` and `scipy>=1.10,<2` (or compatible bounds that match the rest of the stack).
- **Spike3D** pins (e.g. `matplotlib==3.8.4`, `neo==0.13.2`, `jinja2==3.0.3`): Only relax or bump if a concrete conflict is reported by `uv lock` or `uv sync`.

### Phase 3: Recursive “latest compatible” where needed

1. For any dependency that the solver explicitly flags as conflicting, prefer **upgrading to the latest compatible version** (or a range that includes it) in the package that declares it, then re-run lock/sync.
2. Repeat until `uv lock` and `uv sync --all-extras` both succeed.

---

## Order of edits (minimal)


| Package                     | File                                                                     | Change                                                                                        |
| --------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Spike3D                     | [Spike3D/pyproject.toml](D:\pho\repos\Spike3DEnv\Spike3D\pyproject.toml) | `pyvista` → `>=0.43.0,<0.44`; `pyvistaqt` → `>=0.11.0,<0.12`                                  |
| pyPhoCoreHelpers            | —                                                                        | None                                                                                          |
| pyPhoPlaceCellAnalysis      | —                                                                        | None (no direct pyvista)                                                                      |
| NeuroPy                     | —                                                                        | Only if a subsequent lock/sync failure points to numpy/scipy (then relax to match workspace). |
| pyPhoCoreHelpers templating | base_pyproject.toml_fragment.toml                                        | Optional: `pyvista` to `^0.43.0` for consistency.                                             |


---

## Verification

- From workspace root: `uv lock` then `uv sync --all-extras`.
- Ensure no remaining solver errors and that the environment installs and is usable for the four packages (Spike3D, pyPhoPlaceCellAnalysis, pyPhoCoreHelpers, NeuroPy).

---

## Note on “split (markers: sys_platform == 'darwin')”

The error can mention resolution failing for a **split** environment (e.g. `sys_platform == 'darwin'`). Fixing the pyvista conflict addresses the underlying unsatisfiable constraint; if you only need Windows, you could later add `[tool.uv.environments]` to limit resolution to the current platform, but the correct fix is to make the declared versions compatible across the workspace first.