---
name: Subtree pull scripts
overview: Add `pull_all_subworkspaces.ps1` and `pull_all_subworkspaces.sh` under `SCRIPTS/` that run the four subtree pull commands from the README, with no remote modifications.
todos: []
isProject: false
---

# Pull-all-subworkspaces scripts

## Goal

Extract the four subtree-pull commands from [README.md](README.md) (lines 13–16) into two scripts that only fetch and pull into the super-repo. No remotes are added, removed, or pushed to.

## Source commands (from README)


| Prefix                 | Remote                        | Branch                      |
| ---------------------- | ----------------------------- | --------------------------- |
| NeuroPy                | remote-NeuroPy                | feature/safe-advance        |
| pyPhoCoreHelpers       | remote-pyPhoCoreHelpers       | release/pho-diba-2025-paper |
| pyPhoPlaceCellAnalysis | remote-pyPhoPlaceCellAnalysis | develop                     |
| Spike3D                | remote-Spike3D                | master                      |


Two of the pulls use `GIT_LFS_SKIP_SMUDGE=1` (pyPhoCoreHelpers, pyPhoPlaceCellAnalysis).

## Placement

- **[SCRIPTS/pull_all_subworkspaces.ps1](SCRIPTS/pull_all_subworkspaces.ps1)** (new)
- **[SCRIPTS/pull_all_subworkspaces.sh](SCRIPTS/pull_all_subworkspaces.sh)** (new)

Same folder as [SCRIPTS/git_convert_to_subtrees.ps1](SCRIPTS/git_convert_to_subtrees.ps1).

## Script behavior

- **No remote changes**: Scripts run only `git subtree pull` (fetch + merge into the super-repo). No `git remote add/remove/set-url`, no `git push`. Remotes are assumed already configured.
- **LFS**: In PowerShell use `$env:GIT_LFS_SKIP_SMUDGE = "1";` before the two LFS repos’ pulls. In shell use `GIT_LFS_SKIP_SMUDGE=1` exported or inline for those two commands.
- **Failure handling**: Optional: `set -e` in `.sh` and `$ErrorActionPreference = 'Stop'` in `.ps1` so the first failing pull stops the script (user can then fix and re-run).
- **Comments**: Brief header in each script stating it only pulls subtrees and does not modify remotes.

## Implementation details

**PowerShell** (`pull_all_subworkspaces.ps1`):

- Run the four commands in order; for pyPhoCoreHelpers and pyPhoPlaceCellAnalysis set `$env:GIT_LFS_SKIP_SMUDGE = "1"` before their `git subtree pull ... --squash`.

**Shell** (`pull_all_subworkspaces.sh`):

- Shebang `#!/usr/bin/env bash` (or `sh` if you prefer minimal deps).
- For the two LFS repos: `GIT_LFS_SKIP_SMUDGE=1 git subtree pull ... --squash` (or `export GIT_LFS_SKIP_SMUDGE=1` before that block).
- Run from repo root (script can `cd` to the directory containing `.git` if invoked from elsewhere, or document “run from repo root”).

## README

- Optionally add a short note in the “Updating Git Subtrees” section pointing to these scripts (e.g. “Or run `./SCRIPTS/pull_all_subworkspaces.ps1` or `./SCRIPTS/pull_all_subworkspaces.sh` from the repo root.”). Omit if you want the README to stay command-only.

