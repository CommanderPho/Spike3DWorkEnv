---
name: Generalize GitHub username resolution
overview: Expand the GitHub username fallback chain from 2 sources (config file, git remote origin) to 4 sources by adding `git config github.user` and environment variable lookup, and centralize the logic into a single `resolve_github_username()` function.
todos:
  - id: add-config-helpers
    content: Add get_github_username_from_git_config() and get_github_username_from_env() to config.py
    status: completed
  - id: add-resolve-fn
    content: Add resolve_github_username(project_path, config_override) to main.py implementing the 4-step chain
    status: completed
  - id: update-call-site
    content: Replace inline ternary on main.py:122 with resolve_github_username(), update imports
    status: completed
  - id: update-readme
    content: Update README.md to document the expanded 4-step username lookup chain
    status: completed
isProject: false
---

# Generalize GitHub Username Resolution

## Current state

Two sources, inline ternary at `[main.py:122](C:/Users/pho/repos/ACTIVE_DEV/uv-deps-switcher/src/uv_deps_switcher/main.py)`:

```python
effective_username = default_github_username if default_github_username and default_github_username.strip() else get_github_username_from_origin(project_path)
```

Called from `switch_repos()` which first calls `get_default_github_username()` from `[config.py](C:/Users/pho/repos/ACTIVE_DEV/uv-deps-switcher/src/uv_deps_switcher/config.py)`.

## Proposed resolution chain (highest → lowest priority)

1. Config file `default_github_username` (explicit user override)
2. Active repo's `git remote get-url origin` (already implemented in `get_github_username_from_origin()`)
3. `git config --global github.user` (GitHub CLI / common convention)
4. Env var: `GITHUB_USERNAME`, then `GH_USER`, then `GITHUB_USER`

## Changes

### `[config.py](C:/Users/pho/repos/ACTIVE_DEV/uv-deps-switcher/src/uv_deps_switcher/config.py)`

Add two new helper functions:

- `get_github_username_from_git_config()` — runs `git config --global github.user` via subprocess, returns the value or `None`
- `get_github_username_from_env()` — checks `os.getenv()` for `GITHUB_USERNAME`, `GH_USER`, `GITHUB_USER` in order

Export both from the module.

### `[main.py](C:/Users/pho/repos/ACTIVE_DEV/uv-deps-switcher/src/uv_deps_switcher/main.py)`

- Add `resolve_github_username(project_path, config_override=None)` function that implements the 4-step chain using the two new helpers from `config.py` plus the existing `get_github_username_from_origin()`
- Replace the inline ternary on line 122 in `check_and_clone_missing_deps()` with a call to `resolve_github_username(project_path, default_github_username)`
- Update `switch_repos()` import line (already imports `get_default_github_username`)

### `[README.md](C:/Users/pho/repos/ACTIVE_DEV/uv-deps-switcher/README.md)`

Update the "Auto-Clone Missing Dependencies" and config documentation sections to describe the 4-step lookup chain.