# Spike3DWorkEnv
A super-folder that just contains all Spike3D repos as submodules (subfolders)

```bash

git submodule update --init --recursive

```


## Updating Git Subtrees:
```bash
git subtree pull --prefix=NeuroPy remote-NeuroPy feature/safe-advance --squash
$env:GIT_LFS_SKIP_SMUDGE = "1"; git subtree pull --prefix=pyPhoCoreHelpers remote-pyPhoCoreHelpers release/pho-diba-2025-paper --squash
$env:GIT_LFS_SKIP_SMUDGE = "1"; git subtree pull --prefix=pyPhoPlaceCellAnalysis remote-pyPhoPlaceCellAnalysis develop --squash
git subtree pull --prefix=Spike3D remote-Spike3D master --squash
```