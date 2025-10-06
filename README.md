# Spike3DWorkEnv
A super-folder that just contains all Spike3D repos as submodules (subfolders)

```bash

git submodule update --init --recursive

```


## SeaGOAT code search
https://kantord.github.io/SeaGOAT/latest/usage/

```ps1
seagoat-server start C:\Users\pho\repos\Spike3DWorkEnv

```

## Gita - management of multiple git repos simultaneously!
### Install via:
```ps1
uv tool install gita
```

```ps1
cd "H:\TEMP\Spike3DEnv_ExploreUpgrade\Spike3DWorkEnv" ## Windows

cd "/scratch/kdiba_root/kdiba99/halechr/repos/Spike3D_PaperEnv" ## Greatlakes Unix

gita add NeuroPy NeuroPy/
gita add pyPhoCoreHelpers pyPhoCoreHelpers/
gita add pyPhoPlaceCellAnalysis pyPhoPlaceCellAnalysis/
gita add Spike3D Spike3D/

gita group add NeuroPy pyPhoCoreHelpers pyPhoPlaceCellAnalysis -n main-libs-group
gita git pull

```


## Switching Branches:
```ps1

## switch to common stable branch
gita super main-libs-group checkout release/pho-diba-2025-paper
gita shell uv lock
gita shell Spike3D uv sync --all-extras

## switch to dev branchs:
gita super NeuroPy checkout feature/safe-advance
gita super pyPhoCoreHelpers pyPhoPlaceCellAnalysis checkout develop
gita super Spike3D checkout master
gita shell uv lock

gita shell Spike3D uv sync --all-extras

```









### OVERFLOW TODO: custom commands
```
$XDG_CONFIG_HOME/gita/cmds.json
GITA_PROJECT_HOME

C:\Users\pho\.config\gita


PS H:\TEMP\Spike3DEnv_ExploreUpgrade\Spike3DWorkEnv> gita ll    
NeuroPy                feature/safe-advance [] fixed issue with updating bins when we happen to ahve the same number (71 minutes ago)
Spike3D                master     []      bump (5 hours ago)
pyPhoCoreHelpers       develop    []      bump (2 days ago)
pyPhoPlaceCellAnalysis develop    []      force update bins as workaround (71 minutes ago)


gita context main-libs-group

gita pull main-libs-group

gita context auto
gita git pull
gita super checkout release/pho-diba-2025-paper

```

```
git rm --cached PyQtInspect-Open
git rm --cached flexitext
git rm --cached matlab-to-neuropy-exporter
git rm --cached maxlikespy
git rm --cached napari-spike3d
git rm --cached portion
git rm --cached proplot
git rm --cached pylustrator
git rm --cached pho_jupyter_preview_widget
git rm --cached TrajSeg
git rm --cached silx
git rm --cached vedo
```