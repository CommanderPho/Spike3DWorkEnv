---
name: Gitignore backup paths
overview: Update uv-deps-switcher's .gitignore and add documentation so that pyproject.toml backups created by the tool are ignored; optionally add the same pattern to Spike3DEnv's .gitignore.
todos: []
isProject: false
---

# Gitignore for uv-deps-switcher pyproject.toml backups

## Actual backup location (from code)

Backups are written in **each target repo** (e.g. Spike3DEnv), not in uv-deps-switcher itself. Path in code:

- **Directory**: `templating/uv_deps_switcher/backups/`
- **File**: `pyproject.toml.bak`

See [main.py](C:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\src\uv_deps_switcher\main.py) lines 345–348. The folder name is **templating** (not `templates/`).

## Scope


| Location                                                                                    | Purpose                                                                             |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **uv-deps-switcher** [.gitignore](C:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher.gitignore) | Ignore backups if the tool is ever run inside this repo or templating exists there. |
| **Spike3DEnv** [.gitignore](D:\pho\repos\Spike3DEnv.gitignore)                              | Ignore backups created when switching deps in that repo.                            |
| **README** (optional)                                                                       | Document the pattern so other consuming repos can add it.                           |


## Implementation

### 1. uv-deps-switcher `.gitignore`

Append to [.gitignore](C:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher.gitignore) (after the UV section, ~line 41):

```gitignore
# uv-deps-switcher backups (when run in this repo or templating present)
templating/uv_deps_switcher/backups/
```

### 2. Spike3DEnv `.gitignore`

Append to [Spike3DEnv/.gitignore](D:\pho\repos\Spike3DEnv.gitignore):

```gitignore
# uv-deps-switcher pyproject.toml backups
templating/uv_deps_switcher/backups/
```

Using the directory pattern ignores the whole `backups/` folder and any `*.bak` inside it without needing a separate `*.bak` rule.

### 3. README (optional)

In [README.md](C:\Users\pho\repos\ACTIVE_DEV\uv-deps-switcher\README.md), add a short note in the “Project layout” or “Usage” section that repos using the tool should ignore backup files, for example:

- **Suggestion**: In the section that describes the `templating/` directory (e.g. around line 47), add a bullet: “Add `templating/uv_deps_switcher/backups/` to your repo’s `.gitignore` so pyproject.toml backups are not committed.”

## Summary

- **uv-deps-switcher**: One new block in `.gitignore` for `templating/uv_deps_switcher/backups/`.
- **Spike3DEnv**: One new block in `.gitignore` for the same path.
- **Optional**: One sentence in README so other repos can copy the pattern.

No code changes in main.py; backup path stays as-is.