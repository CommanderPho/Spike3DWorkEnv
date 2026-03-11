---
name: uv-deps-switcher workspace mode
overview: Add a third template mode "workspace" to uv-deps-switcher that writes `dep = { workspace = true }` for repo-like deps (those with path in dev), and optionally generate the workspace fragment from existing dev/release fragments when missing.
todos: []
isProject: false
---

# Workspace template mode for uv-deps-switcher

## Goal

Add a **workspace** mode (alongside `dev` and `release`) that switches `[tool.uv.sources]` to use `dep = { workspace = true }` for dependencies that are “repos” (path-based in dev), so the project works inside a uv monorepo (e.g. [Spike3DEnv](D:\pho\repos\Spike3DEnv\pyproject.toml)). If a repo has no workspace template yet, generate it from that repo’s dev/release fragments in `./templating` before switching.

## Current behavior (reference)

- Modes: `dev` (path, editable) and `release` (git).
- Per-repo templates live under `**templating/`** (not `templates/`) as:
  - `templating/pyproject_template_dev.toml_fragment`
  - `templating/pyproject_template_release.toml_fragment`
- [main.py](c:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\src\uv_deps_switcher\main.py): `read_template(project_path, mode)` reads `templating/pyproject_template_{mode}.toml_fragment`; `switch_repos` uses that content to update `pyproject.toml` via `update_pyproject_sources`. Validity: both dev and release fragments must exist (`is_valid_project`, `find_projects_with_templating`).

## Implementation plan

### 1. Add workspace fragment generation from dev + release

**New function** (e.g. in [main.py](c:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\src\uv_deps_switcher\main.py)):

- `generate_workspace_fragment_from_templates(project_path: Path, dry_run: bool = False) -> Optional[str]`
  - Read dev and release fragments via existing `read_template(project_path, "dev")` and `read_template(project_path, "release")`. If either is missing, return `None`.
  - Parse sources with existing `parse_template_sources()` for both.
  - **Workspace keys**: all keys that have a `path` entry in the dev sources (these are the “repos” to turn into workspace deps).
  - Build the workspace fragment:
    - Header: `[tool.uv.sources]`.
    - Iterate over the **release** fragment lines (to preserve order and non-repo entries). For each line with a key: if key is in workspace keys, emit `key = { workspace = true }`; otherwise keep the release line.
    - Append any workspace keys that appear in dev but not in release (so dev-only path deps get `key = { workspace = true }`).
  - Return the full fragment string (so the caller can write it and/or use it). Optionally accept a `dry_run` and only return content without writing.

**Write the fragment when missing:**

- When switching to workspace, **before** `read_template(repo_path, "workspace")`:
  - If `templating/pyproject_template_workspace.toml_fragment` does not exist, call `generate_workspace_fragment_from_templates(repo_path)` to get content; if content is not `None`, write it to that path (creating `templating/` if needed), then proceed to read (or use the in-memory content directly to avoid a second read).

### 2. Wire workspace into switch flow

- `**read_template(project_path, "workspace")`**: Already works if the file exists (same pattern `pyproject_template_workspace.toml_fragment`).
- `**switch_repos(repos, mode, ...)`**:
  - When `mode == "workspace"`: for each repo, if the workspace template file does not exist, generate it from dev/release (as above) and write it; then obtain template content (read or use generated string) and call `update_pyproject_sources` as for dev/release. Do not run clone logic (that’s dev-only).
- **CLI**: Add `"workspace"` to the mode `choices` and update help text to describe workspace mode (monorepo, `workspace = true`).

### 3. Project validity for workspace

- **No change to `is_valid_project`**: Keep requiring dev + release (so we can always generate the workspace fragment when needed). Projects valid for dev/release remain valid for workspace.
- **No change to `find_projects_with_templating`**: Still “has dev and release”; those are the projects that can be switched to workspace (with on-the-fly generation of the workspace fragment if missing).

### 4. Optional: deploy-templates also creates workspace fragment

- **Package-level Jinja2**: Add [pyproject_template_workspace.toml_fragment.j2](c:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\src\uv_deps_switcher\templates\pyproject_template_workspace.toml_fragment.j2) that, for each `include_deps`, emits `dep = { workspace = true }` (same structure as dev/release .j2 files).
- `**deploy_templates()`**: After writing dev and release fragments, also render the workspace .j2 with the same `include_deps` and write `templating/pyproject_template_workspace.toml_fragment`. That way repos get a consistent workspace fragment from `deploy-templates` when they don’t yet have one; “generate from dev/release” remains the fallback when switching to workspace in repos that have only dev+release.

### 5. Files to touch


| Location                                                                                                                                                                               | Change                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [main.py](c:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\src\uv_deps_switcher\main.py)                                                                                                 | Add `generate_workspace_fragment_from_templates()`; in `switch_repos` when `mode == "workspace"`, ensure workspace fragment exists (generate + write if missing), then get content and call `update_pyproject_sources`; add `"workspace"` to CLI choices and help. |
| [main.py](c:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\src\uv_deps_switcher\main.py)                                                                                                 | Optional: in `deploy_templates()`, add `generate_workspace_template(include_deps)` (render new .j2) and write workspace fragment.                                                                                                                                  |
| [templates/pyproject_template_workspace.toml_fragment.j2](c:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\src\uv_deps_switcher\templates\pyproject_template_workspace.toml_fragment.j2) | New file: `[tool.uv.sources]` plus one line per `include_deps`: `dep = { workspace = true }`.                                                                                                                                                                      |


### 6. Edge cases and notes

- **Key consistency**: Use the same key extraction as elsewhere (`extract_source_key` / `parse_template_sources`). TOML normalizes keys; when building “release line map” for non-workspace keys, use the key as parsed so replacement is correct.
- **Dev-only path deps**: Keys that have `path` in dev but no corresponding entry in release get a line in the workspace fragment as `key = { workspace = true }` (appended after iterating release lines).
- **Order**: Preserve the order of the release template for the final workspace fragment so diffs stay small and behavior is predictable.
- **Poetry-style fragments**: Some repos (e.g. [pyPhoCoreHelpers/templating](D:\pho\repos\Spike3DEnv\pyPhoCoreHelpers\templating)) use `[tool.poetry.group.remote.dependencies]`; `parse_template_sources` only reads `[tool.uv.sources]`. This plan assumes uv-style fragments; converting Poetry fragments is out of scope unless you want to extend the parser later.

## Summary

- Add **workspace** mode that applies a fragment where every “repo” (path in dev) becomes `{ workspace = true }` and other entries are copied from the release fragment.
- **If the workspace fragment is missing**: generate it from the repo’s dev and release fragments (same `templating/` dir), then switch.
- Optionally add a package-level workspace .j2 and have `deploy-templates` write the workspace fragment so new repos get all three templates at once.

