---
name: Subtree script robustness
overview: Add explicit .gitmodules cleanup, configurable/detected branch, exit-on-failure for git commands, and continue-on-error with summary when converting multiple submodules in [SCRIPTS/git_convert_to_subtrees.ps1](SCRIPTS/git_convert_to_subtrees.ps1).
todos: []
isProject: false
---

# Subtree conversion script robustness

## 1. Explicit .gitmodules cleanup

After step 1 (`git rm --cached $RepoPath`), ensure the submodule is removed from `.gitmodules`:

- If `.gitmodules` exists, read it and remove the block for this submodule: from `[submodule "RepoPath"]` through the next blank line or next `[submodule ...]` (or end of file).
- Use a regex or line-by-line parse so we don’t leave a dangling section. If content changed, write back and run `git add .gitmodules` (or rely on the existing `git add .` in step 4).
- If the file becomes empty or only whitespace, either delete it or leave a single newline; stage the change.

**Location:** Inside `Convert-SubmoduleToSubtree`, immediately after the `git rm --cached $RepoPath` call (before step 2).

## 2. Branch parameter and detection

- Add an optional parameter to the function, e.g. `[string]$Branch = ''`. If provided, use it in `git subtree add ... $remoteName $Branch --squash`.
- If `$Branch` is empty: detect default branch from the remote with `git ls-remote --symref $RemoteUrl HEAD` (run after adding the remote and fetching, or before fetch using $RemoteUrl). Parse the line `ref: refs/heads/<branch>	HEAD` to get `<branch>`; fallback to `main` if parsing fails.
- Pass-through: add an optional `-Branch` to the script’s execution list (e.g. a single default for all, or per-repo if you add a hashtable of repo → branch). For minimal change, use one optional `$defaultBranch` variable at script level; when set, pass it into each `Convert-SubmoduleToSubtree` call; otherwise rely on detection.

**Location:** New parameter on `Convert-SubmoduleToSubtree`; detection logic inside the function before `git subtree add`; caller loop passes optional branch if desired.

## 3. Error handling (exit on failure)

- After every critical `git` command, check `$LASTEXITCODE` and, if non-zero, throw a clear error (e.g. `throw "git <command> failed for $RepoPath"`) so the script doesn’t continue in a bad state.
- Commands to guard: `git rm --cached`, `git add .`, `git commit`, `git remote add`, `git fetch`, `git subtree add`. Optionally guard `git config --remove-section` only when it’s required for correctness (removing the section is best-effort; ignore exit if section doesn’t exist).
- Keep file operations (Remove-Item, .gitmodules edit) in try/catch or with existence checks so failures are reported clearly.

**Location:** After each of the listed git invocations inside `Convert-SubmoduleToSubtree`.

## 4. Continue-on-error and summary for the list

- In the top-level `foreach ($name in $submodules.Keys)`, wrap the call to `Convert-SubmoduleToSubtree` in try/catch. On catch, log the error (e.g. Write-Error or Write-Host to stderr), add the repo name to a list of failures, and continue to the next key.
- After the loop, if any failures were collected, print a short summary: e.g. “Converted X; failed: Repo1, Repo2” and exit with a non-zero code (e.g. `exit 1`). If all succeeded, exit 0.

**Location:** [SCRIPTS/git_convert_to_subtrees.ps1](SCRIPTS/git_convert_to_subtrees.ps1) lines 52–54 (the foreach and single call); add a `$failed = @()` (or list), try/catch, and final summary + exit.

## File to modify

- [SCRIPTS/git_convert_to_subtrees.ps1](SCRIPTS/git_convert_to_subtrees.ps1) only.

## Order of implementation

1. Add .gitmodules cleanup block after step 1.
2. Add `$Branch` parameter and default-branch detection; use in `git subtree add`.
3. Add `$LASTEXITCODE` checks and throw after each critical git command.
4. Wrap the foreach in try/catch, collect failures, and print summary + exit code.

No new files; keep the script single-file and preserve existing style (comments, spacing).