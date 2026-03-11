# Pull all subtree subworkspaces. Only fetches and merges into this repo; does not add, remove, or push to any remotes.
# Run from repo root. Remotes (remote-NeuroPy, remote-pyPhoCoreHelpers, etc.) must already be configured.
$ErrorActionPreference = 'Stop'

git subtree pull --prefix=NeuroPy remote-NeuroPy feature/safe-advance --squash
$env:GIT_LFS_SKIP_SMUDGE = "1"; git subtree pull --prefix=pyPhoCoreHelpers remote-pyPhoCoreHelpers release/pho-diba-2025-paper --squash
$env:GIT_LFS_SKIP_SMUDGE = "1"; git subtree pull --prefix=pyPhoPlaceCellAnalysis remote-pyPhoPlaceCellAnalysis develop --squash
git subtree pull --prefix=Spike3D remote-Spike3D master --squash
