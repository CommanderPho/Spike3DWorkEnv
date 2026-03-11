---
name: Fix broken imports in pho_jupyter_preview_widget
overview: Fix all broken imports in the pho_jupyter_preview_widget folder that use the old package name `pho_jupyter_preview_widget` instead of `pyphocorehelpers.pho_jupyter_preview_widget`. This includes both actual code imports and docstring examples.
todos: []
---

# Fix Broken Imports in pho_jupyter_preview_widget

## Overview

The `pho_jupyter_preview_widget` folder was integrated from a separate package but still contains imports using the old package name `pho_jupyter_preview_widget` instead of `pyphocorehelpers.pho_jupyter_preview_widget`. This plan fixes all broken imports.

## Files to Fix

### 1. [ipython_helpers.py](H:\TEMP\Spike3DEnv_ExploreUpgrade\Spike3DWorkEnv\pyPhoCoreHelpers\src\pyphocorehelpers\pho_jupyter_preview_widget\ipython_helpers.py)

**Line 68** - Fix actual import in `config_ndarray_preview` method:

- Change: `from pho_jupyter_preview_widget.display_helpers import array_repr_with_graphical_preview`
- To: `from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_repr_with_graphical_preview`

**Line 87** - Fix actual import in `ndarray_preview` method:

- Change: `from pho_jupyter_preview_widget.display_helpers import array_repr_with_graphical_preview`
- To: `from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_repr_with_graphical_preview`

**Line 49** - Fix docstring example:

- Change: `from pho_jupyter_preview_widget.ipython_helpers import PreviewWidgetMagics`
- To: `from pyphocorehelpers.pho_jupyter_preview_widget.ipython_helpers import PreviewWidgetMagics`

### 2. [display_helpers.py](H:\TEMP\Spike3DEnv_ExploreUpgrade\Spike3DWorkEnv\pyPhoCoreHelpers\src\pyphocorehelpers\pho_jupyter_preview_widget\display_helpers.py)

**Line 328** - Fix docstring example (has double path):

- Change: `from pho_jupyter_preview_widget.pho_jupyter_preview_widget.display_helpers import array_preview_with_heatmap_repr_html`
- To: `from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_preview_with_heatmap_repr_html`

**Line 493** - Fix docstring example:

- Change: `from pho_jupyter_preview_widget.display_helpers import array_preview_with_graphical_shape_repr_html`
- To: `from pyphocorehelpers.pho_jupyter_preview_widget.display_helpers import array_preview_with_graphical_shape_repr_html`

### 3. [array_shape_display/array_shape_display.py](H:\TEMP\Spike3DEnv_ExploreUpgrade\Spike3DWorkEnv\pyPhoCoreHelpers\src\pyphocorehelpers\pho_jupyter_preview_widget\array_shape_display\array_shape_display.py)

**Lines 76-77** - Fix example code imports (in commented/example section):

- Change: `from pho_jupyter_preview_widget.array_shape_display import array_repr_html` and `from pho_jupyter_preview_widget.array_shape_display.array_shape_display import array_repr_html`
- To: `from pyphocorehelpers.pho_jupyter_preview_widget.array_shape_display import array_repr_html` and `from pyphocorehelpers.pho_jupyter_preview_widget.array_shape_display.array_shape_display import array_repr_html`

## Implementation Notes

- All imports should use the full path: `pyphocorehelpers.pho_jupyter_preview_widget`
- Fix both actual code imports (critical) and docstring examples (for consistency)
- The existing correct imports on lines 502 and 512 in `display_helpers.py` serve as reference for the correct format