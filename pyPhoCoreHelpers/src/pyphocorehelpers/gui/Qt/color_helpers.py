from __future__ import annotations # prevents having to specify types for typehinting as strings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ## typehinting only imports here
    from matplotlib.colors import LinearSegmentedColormap


from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from nptyping import NDArray
from collections import namedtuple
from copy import deepcopy
import numpy as np
import pandas as pd
from neuropy.utils.mixins.enum_helpers import StringLiteralComparableEnum
from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes
import pyphoplacecellanalysis.External.pyqtgraph as pg
from qtpy import QtGui # for QColor
from qtpy.QtGui import QColor, QBrush, QPen



def debug_print_color(color: QColor):
    if color.alphaF() == 1.0:
        color_hex_format = QColor.HexRgb
    else:
        color_hex_format = QColor.HexArgb
    print(f'rgbaF: {color.getRgbF()}, HexARgb: {color.name(color_hex_format)}')
    

def build_adjusted_color(color: QColor, hue_shift:float=0.0, saturation_scale:float=1.0, value_scale:float=1.0, alpha_scale: float=1.0, wants_return_as_hex_string:bool=False, wants_hex_string_include_alpha: bool=True):
    """ Builds a copy of the color QColor with optionally modified HSV properties
    Example:
        from pyphocorehelpers.gui.Qt.color_helpers import build_adjusted_color
    
        debug_print_color(curr_color)
        curr_color_copy = build_adjusted_color(curr_color, hue_shift=0.0, saturation_scale=0.35, value_scale=1.0)
        debug_print_color(curr_color_copy)

    """
    if isinstance(color, str):
        color = QtGui.QColor(color) ## convert to QColor if needed
    
    curr_color_copy = color.convertTo(QColor.Hsv) # makes a copy of color
    # curr_color_copy.setHsv(curr_color_copy.hue(),curr_color_copy.saturation(), curr_color_copy.value())
    # np.clip(v, 0.0, 1.0) ensures the values are between 0.0 and 1.0
    curr_color_copy.setHsvF(np.clip((curr_color_copy.hueF() + hue_shift), 0.0, 1.0),
                            np.clip((saturation_scale*curr_color_copy.saturationF()), 0.0, 1.0),
                            np.clip((value_scale * curr_color_copy.valueF()), 0.0, 1.0))
    curr_color_copy.setAlphaF(np.clip((alpha_scale*curr_color_copy.alphaF()), 0.0, 1.0))
    # curr_color_copy.setAlphaF(color.alphaF())
    assert curr_color_copy.isValid(), "Constructed color is invalid!"
    
    if not wants_return_as_hex_string:
        # return QColor
        return curr_color_copy
    else:
        ## convert to a hex string to return
        return ColorFormatConverter.qColor_to_hexstring(curr_color_copy, include_alpha=wants_hex_string_include_alpha)


# @function_attributes(short_name=None, tags=['color', 'HSV', 'conversion'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-01-29 13:53', related_items=[])
def calculate_hsv_shift(colorA: Union[str, QColor], colorB: Union[str, QColor], debug_print=False) -> Dict[str, float]:
    """ Computes the HSV shift/scale factors between two colors
    from pyphocorehelpers.gui.Qt.color_helpers import calculate_hsv_shift
            
    NOTE: outputs are suitable for direct input into `build_adjusted_color(...)`

    Usage:    
    
        from pyphocorehelpers.gui.Qt.color_helpers import calculate_hsv_shift
        
        hsv_diff = calculate_hsv_shift(colorA='#1f02c2' , colorB='#13007f', debug_print=True) # hsvB - hsvA
        hsv_diff # {'hue_shift': -0.00022222222222223476, 'saturation_scale': 1.0104226090442343, 'value_scale': 0.654639175257732, 'alpha_scale': 1.0}
                
    """
    if isinstance(colorA, str):
        colorA = QtGui.QColor(colorA)
    if isinstance(colorB, str):
        colorB = QtGui.QColor(colorB)
        
    if debug_print:
        debug_print_color(colorA)
        debug_print_color(colorB)
    
    hsvA = np.array(colorA.getHsvF()) # (0.6918333333333333, 0.9896849011978333, 0.7607843137254902, 1.0)
    hsvB = np.array(colorB.getHsvF()) # (0.6918333333333333, 0.9896849011978333, 0.7607843137254902, 1.0)
    assert len(hsvA) == 4
    assert len(hsvB) == 4
    if debug_print:
        print(f'hsvA: {hsvA}\nhsvB: {hsvB}')
    # hsv_diff: NDArray = (hsvB - hsvA)
    
    # saturation_diff = max(hsvB[1], hsvB[0])
    
    hsv_diff = np.array([(hsvB[0] - hsvA[0]), np.nan_to_num((hsvB[1] / hsvA[1]), nan=1.0), np.nan_to_num((hsvB[2] / hsvA[2]), nan=1.0), np.nan_to_num((hsvB[3] / hsvA[3]), nan=1.0)])  
    
    assert len(hsv_diff) == 4
    return dict(zip(['hue_shift', 'saturation_scale', 'value_scale', 'alpha_scale'], hsv_diff)) # dict(hue_shift=0.0, saturation_scale=1.0, value_scale=1.0, alpha_scale=1.0)

    


def adjust_saturation(rgb, saturation_factor: float):
    """ adjusts the rgb colors by the saturation_factor by converting to HSV space.
    
    """
    import matplotlib.colors as mcolors
    import colorsys
    # Convert RGB to HSV
    hsv = mcolors.rgb_to_hsv(rgb)

    if np.ndim(hsv) < 3:
        # Multiply the saturation by the saturation factor
        hsv[:, 1] *= saturation_factor
        
        # Clip the saturation value to stay between 0 and 1
        hsv[:, 1] = np.clip(hsv[:, 1], 0, 1)
        
    else: 
        # Multiply the saturation by the saturation factor
        hsv[:, :, 1] *= saturation_factor
        # Clip the saturation value to stay between 0 and 1
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 1)
    
    # Convert back to RGB
    return mcolors.hsv_to_rgb(hsv)




# ==================================================================================================================================================================================================================================================================================== #
# 3D Colormap Helpers - for `use_advanced_3D_cmap` == True mode                                                                                                                                                                                                                                                       #
# ==================================================================================================================================================================================================================================================================================== #

# from pyphocorehelpers.gui.Qt.color_helpers import create_3d_lut_saturation, create_3d_lut_cmaps_interp, apply_3d_colormap, composite_stack
@function_attributes(short_name=None, tags=['use_advanced_3D_cmap'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2026-03-02 13:36', related_items=[])
def create_3d_lut_saturation(n_t_bins, v_bins=256, cmap_name='viridis'):
    """
    Creates a 2D Lookup Table (LUT) mapping (v_idx, t_idx) -> RGBA.
    Saturation and Alpha decrease as t_idx increases.
    """
    # 1. Get base colormap from PyQtGraph (returns 0-255 RGBA)
    cmap = pg.colormap.get(cmap_name)
    base_rgba = cmap.getLookupTable(0.0, 1.0, v_bins, alpha=True) 
    
    # Ensure it has 4 channels (fallback if the colormap only returns RGB)
    if base_rgba.shape[1] == 3:
        base_rgba = np.column_stack([base_rgba, np.full(v_bins, 255, dtype=base_rgba.dtype)])
        
    base_rgb = base_rgba[:, :3].astype(np.float32)
    
    # Calculate luminance to use for desaturating colors
    # (Dot product with standard perceptual weights)
    luminance = np.dot(base_rgb, [0.2989, 0.5870, 0.1140])[:, None] 
    
    # Initialize the 3D LUT: (v_bins, n_t_bins, 4 channels)
    lut = np.zeros((v_bins, n_t_bins, 4), dtype=np.uint8)
    
    for t in range(n_t_bins):
        # Scale factors: t=0 is 100%, t=max is heavily reduced
        t_normalized = t / max(1, n_t_bins - 1)
        sat_factor = 1.0 - 0.8 * t_normalized   # Saturation down to 20%
        alpha_factor = 1.0 - 0.5 * t_normalized # Alpha down to 50%
        
        # Blend base RGB with pure grayscale luminance to desaturate
        rgb_t = base_rgb * sat_factor + luminance * (1.0 - sat_factor)
        lut[:, t, :3] = np.clip(rgb_t, 0, 255).astype(np.uint8)
        
        # Scale alpha
        base_alpha = base_rgba[:, 3].astype(np.float32)
        lut[:, t, 3] = np.clip(base_alpha * alpha_factor, 0, 255).astype(np.uint8)
        
        # CRITICAL: Mask out absolute zero values by forcing Alpha = 0 
        # (Assuming v_idx=0 means 0 probability background)
        lut[0, t, 3] = 0
        
    return lut

@function_attributes(short_name=None, tags=['use_advanced_3D_cmap'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2026-03-02 13:36', related_items=[])
def create_3d_lut_cmaps_interp(n_t_bins, v_bins=256, cmap1_name='Reds', cmap2_name='Greens'):
    """
    Creates a 2D Lookup Table (LUT) mapping (v_idx, t_idx) -> RGBA.
    Interpolates between two colormaps across t_idx.
    Alpha smoothly decreases as t_idx increases for better 3D compositing.
    """
    # 1. Get base colormaps from PyQtGraph
    # pg.colormap.get('viridis','matplotlib')
    if isinstance(cmap1_name, str):
        cmap1 = pg.colormap.get(cmap1_name,'matplotlib')
    else:
        cmap1 = cmap1_name ## assume direct cmap

    if isinstance(cmap2_name, str):
        cmap2 = pg.colormap.get(cmap2_name,'matplotlib')
    else:
        cmap2 = cmap2_name ## assume direct cmap

    rgba1 = cmap1.getLookupTable(0.0, 1.0, v_bins, alpha=True) 
    rgba2 = cmap2.getLookupTable(0.0, 1.0, v_bins, alpha=True)
    
    # Ensure they have 4 channels
    if rgba1.shape[1] == 3:
        rgba1 = np.column_stack([rgba1, np.full(v_bins, 255, dtype=rgba1.dtype)])
    if rgba2.shape[1] == 3:
        rgba2 = np.column_stack([rgba2, np.full(v_bins, 255, dtype=rgba2.dtype)])
        
    rgba1 = rgba1.astype(np.float32)
    rgba2 = rgba2.astype(np.float32)
    
    # Initialize the 3D LUT: (v_bins, n_t_bins, 4 channels)
    lut = np.zeros((v_bins, n_t_bins, 4), dtype=np.uint8)
    
    for t in range(n_t_bins):
        # Scale factor: t=0 is 100% cmap1, t=max is 100% cmap2
        t_normalized = t / max(1, n_t_bins - 1)
        
        # Linearly interpolate between the two colormaps
        rgba_t = rgba1 * (1.0 - t_normalized) + rgba2 * t_normalized
        
        # Optional but recommended for stacking: scale alpha down as t increases
        # so older time bins don't completely occlude newer ones
        alpha_factor = 1.0 - 0.5 * t_normalized # Alpha down to 50%
        rgba_t[:, 3] *= alpha_factor
        
        lut[:, t, :] = np.clip(rgba_t, 0, 255).astype(np.uint8)
        
        # CRITICAL: Mask out absolute zero values by forcing Alpha = 0 
        # (Assuming v_idx=0 means 0 probability background)
        lut[0, t, 3] = 0
        
    return lut

@function_attributes(short_name=None, tags=['use_advanced_3D_cmap'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2026-03-02 13:36', related_items=[])
def apply_3d_colormap(data_3d, lut):
    """
    Extremely efficient mapping of (X, Y, T) data -> (X, Y, T, 4) RGBA volume.
    """
    Nx, Ny, Nt = data_3d.shape
    v_bins = lut.shape[0]
    
    # Scale float posteriors [0.0, 1.0] to integer indices [0, v_bins-1]
    v_idx = np.clip((data_3d * (v_bins - 1)).astype(int), 0, v_bins - 1)
    
    # Create broadcastable t_idx: shape (1, 1, Nt)
    # NumPy will automatically broadcast this against v_idx's shape (Nx, Ny, Nt)
    t_idx = np.arange(Nt).reshape(1, 1, Nt)
    
    # Apply advanced indexing (Returns shape: Nx, Ny, Nt, 4)
    rgba_volume = lut[v_idx, t_idx]
    
    return rgba_volume

@function_attributes(short_name=None, tags=['use_advanced_3D_cmap'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2026-03-02 13:36', related_items=[])
def composite_stack(rgba_volume):
    """
    Flattens the 4D RGBA volume into a 2D RGBA image by alpha-compositing
    from bottom (t=0) to top (t=Nt-1).

    Usage:
        from pyphocorehelpers.gui.Qt.color_helpers import create_3d_lut_saturation, create_3d_lut_cmaps_interp, apply_3d_colormap, composite_stack

    """
    # Convert to float [0, 1] for math
    rgba = rgba_volume.astype(np.float32) / 255.0
    
    # Pre-multiply alpha to simplify standard "Over" compositing
    rgb = rgba[..., :3] * rgba[..., 3:4]
    a = rgba[..., 3:4]
    
    Nx, Ny, Nt, _ = rgba.shape
    out_rgb = np.zeros((Nx, Ny, 3), dtype=np.float32)
    out_a = np.zeros((Nx, Ny, 1), dtype=np.float32)
    
    # Python loop over T is perfectly fine here because standard T is small (e.g. 5-50),
    # while the heavy lifting on the 2D spatial grid is fully vectorized.
    for t in range(Nt):
        src_rgb = rgb[:, :, t, :]
        src_a = a[:, :, t, :]
        
        # Standard Alpha Blending: Out = Src + Dst * (1 - Src_Alpha)
        out_rgb = src_rgb + out_rgb * (1.0 - src_a)
        out_a = src_a + out_a * (1.0 - src_a)
        
    # Un-premultiply alpha to get standard RGB back
    mask = out_a > 0
    final_rgb = np.zeros_like(out_rgb)
    final_rgb[mask[..., 0]] = out_rgb[mask[..., 0]] / out_a[mask[..., 0]]
    
    final_rgba = np.concatenate([final_rgb, out_a], axis=-1)
    return (final_rgba * 255).astype(np.uint8)






@metadata_attributes(short_name=None, tags=['colormap', 'color', 'static'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-08-30 19:55', related_items=[])
class ColormapHelpers:
    """ 
    from pyphocorehelpers.gui.Qt.color_helpers import ColormapHelpers
        
    ColormapHelpers.
    """
    # Create a function to modify the colormap's alpha channel
    @classmethod
    def create_transparent_colormap(cls, cmap_name: Optional[str]=None, color_literal_name: Optional[str]=None, lower_bound_alpha=0.1, should_return_LinearSegmentedColormap:bool=True) -> NDArray:
        """ 
        Usage:
            additional_cmap_names = dict(zip(TrackTemplates.get_decoder_names(), ['red', 'purple', 'green', 'orange'])) # {'long_LR': 'red', 'long_RL': 'purple', 'short_LR': 'green', 'short_RL': 'orange'}

            long_epoch_config = long_short_display_config_manager.long_epoch_config.as_pyqtgraph_kwargs()
            short_epoch_config = long_short_display_config_manager.short_epoch_config.as_pyqtgraph_kwargs()

            color_dict = {'long_LR': long_epoch_config['brush'].color(), 'long_RL': apply_LR_to_RL_adjustment(long_epoch_config['brush'].color()),
                            'short_LR': short_epoch_config['brush'].color(), 'short_RL': apply_LR_to_RL_adjustment(short_epoch_config['brush'].color())}
            additional_cmap_names = {k: ColorFormatConverter.qColor_to_hexstring(v) for k, v in color_dict.items()}

            additional_cmaps = {k: ColormapHelpers.create_transparent_colormap(color_literal_name=v, lower_bound_alpha=0.1) for k, v in additional_cmap_names.items()}
        
        """
        from pyphoplacecellanalysis.External.pyqtgraph.colormap import ColorMap
        from matplotlib.colors import LinearSegmentedColormap
        
        # Get the base colormap
        assert (cmap_name is not None) or (color_literal_name is not None)
        if color_literal_name is not None:
            assert cmap_name is None
            cmap = pg.ColorMap(np.array([0.0, 1.0]), np.array([pg.mkColor(color_literal_name).getRgb()[:3] + (0,), pg.mkColor(color_literal_name).getRgb()[:3] + (255,)], dtype=np.ubyte))
        else:
            assert cmap_name is not None
            cmap = pg.colormap.get(cmap_name, source='matplotlib')

        # Create a lookup table with the desired number of points (default 256)
        if should_return_LinearSegmentedColormap:    
            lut = cmap.getLookupTable(alpha=True, mode=ColorMap.FLOAT)
        else:
            lut = cmap.getLookupTable(alpha=True, mode=ColorMap.BYTE)        
        # `ColorMap.BYTE` (0 to 255), `ColorMap.FLOAT` (0.0 to 1.0) or `ColorMap.QColor`.
        
        # Modify the alpha values
        alpha_channel = lut[:, 3]  # Extract the alpha channel (4th column)
        alpha_channel = np.linspace(lower_bound_alpha, 1, len(alpha_channel))  # Linear alpha gradient from lower_bound_alpha to 1
        if should_return_LinearSegmentedColormap:
            n_colors = np.shape(lut)[0]
            cmap = LinearSegmentedColormap.from_list('CustomMap', lut, N=n_colors)
            cmap.set_bad(color=(0,0,0,0))        # NaNs→fully transparent
            return cmap
        
        else:
            # return NDArray
            lut[:, 3] = (alpha_channel * 255).astype(np.uint8)  # Convert to 0-255 range
            
        
        return lut
        
    @classmethod
    def desaturate_colormap(cls, cmap, desaturation_factor: float):
        """
        Desaturate a colormap by a given factor.

        Parameters:
        - cmap: A Matplotlib colormap instance.
        - desaturation_factor: A float between 0 and 1, with 0 being fully desaturated (greyscale)
        and 1 being fully saturated (original colormap colors).

        Returns:
        - new_cmap: A new Matplotlib colormap instance with desaturated colors.

        Usage:
            # Load the existing 'viridis' colormap
            viridis = plt.cm.get_cmap('viridis')
            # Create a desaturated version of 'viridis'
            desaturation_factors = np.linspace(start=1.0, stop=0.0, num=6)
            desaturated_viridis = [ColormapHelpers.desaturate_colormap(viridis, a_desaturation_factor) for a_desaturation_factor in desaturation_factors]
            for a_cmap in desaturated_viridis:
                display(a_cmap)

                
        """
        import matplotlib.pyplot as plt
        # Get the colormap colors and the number of entries in the colormap
        cmap_colors = cmap(np.arange(cmap.N))
        
        # Convert RGBA to RGB
        cmap_colors_rgb = cmap_colors[:, :3]
        
        # Create an array of the same shape filled with luminance values
        # The luminance of a color is a weighted average of the R, G, and B values
        # These weights are based on how the human eye perceives color intensity
        luminance = np.dot(cmap_colors_rgb, [0.299, 0.587, 0.114]).reshape(-1, 1)
        
        # Create a grayscale version of the colormap
        grayscale_cmap = np.hstack([luminance, luminance, luminance])
        
        # Blend the original colormap with the grayscale version
        blended_cmap = desaturation_factor * cmap_colors_rgb + (1 - desaturation_factor) * grayscale_cmap
        
        # Add the alpha channel back and create a new colormap
        new_cmap_colors = np.hstack([blended_cmap, cmap_colors[:, 3:]])
        new_cmap = plt.matplotlib.colors.ListedColormap(new_cmap_colors)
        
        return new_cmap


    @classmethod
    def make_saturating_red_cmap(cls, time: float, N_colors:int=256, min_alpha: float=0.0, max_alpha: float=0.82, debug_print:bool=False) -> LinearSegmentedColormap:
        """ time is between 0.0 and 1.0 

        Usage: Test Example:
            from pyphocorehelpers.gui.Qt.color_helpers import ColormapHelpers

            n_time_bins = 5
            cmaps = [ColormapHelpers.make_saturating_red_cmap(float(i) / float(n_time_bins - 1)) for i in np.arange(n_time_bins)]
            for cmap in cmaps:
                cmap
                
        Usage:
            # Example usage
            # You would replace this with your actual data and timesteps
            data = np.random.rand(10, 10)  # Sample data
            n_timesteps = 5  # Number of timesteps

            # Plot data with increasing red for each timestep
            fig, axs = plt.subplots(1, n_timesteps, figsize=(15, 3))
            for i in range(n_timesteps):
                time = i / (n_timesteps - 1)  # Normalize time to be between 0 and 1
                # cmap = make_timestep_cmap(time)
                cmap = make_red_cmap(time)
                axs[i].imshow(data, cmap=cmap)
                axs[i].set_title(f'Timestep {i+1}')
            plt.show()

        """
        from matplotlib.colors import LinearSegmentedColormap

        colors = np.array([(0, 0, 0), (1, 0, 0)]) # np.shape(colors): (2, 3)
        if debug_print:
            print(f'np.shape(colors): {np.shape(colors)}')
        # Apply a saturation change
        saturation_factor = float(time) # 0.5  # Increase saturation by 1.5 times
        adjusted_colors = adjust_saturation(colors, saturation_factor)
        if debug_print:
            print(f'np.shape(adjusted_colors): {np.shape(adjusted_colors)}')
        adjusted_colors = adjusted_colors.tolist()
        ## Set the alpha of the first color to 0.0 and of the final color to 0.82
        adjusted_colors = [[*v, max_alpha] for v in adjusted_colors]
        adjusted_colors[0][-1] = min_alpha

        # n_bins = [2]  # Discretizes the interpolation into bins
        return LinearSegmentedColormap.from_list('CustomMap', adjusted_colors, N=N_colors)


    # Convert to LinearSegmentedColormap
    @classmethod
    def colormap_to_linear_segmented(cls, cmap, n_samples=256) -> LinearSegmentedColormap:
        """
        Converts a Colormap to a LinearSegmentedColormap.

        Args:
            cmap (Colormap): The original colormap to convert.
            n_samples (int): Number of samples to take from the original colormap.

        Returns:
            LinearSegmentedColormap: The converted colormap.
        """
        from matplotlib.colors import LinearSegmentedColormap
        from pyphoplacecellanalysis.External.pyqtgraph.colormap import ColorMap
        if isinstance(cmap, (LinearSegmentedColormap,)):
            return deepcopy(cmap) # already the correct type
        else:
            ## needs convert                          
            colors = cmap(np.linspace(0, 1, n_samples))  # Sample the original colormap
            return LinearSegmentedColormap.from_list(f"{cmap.name}_linear", colors)

    @classmethod
    def mpl_to_pg_colormap(cls, mpl_cmap_name: Union[str, Any], resolution=256) -> pg.ColorMap:
        """
        Converts a Matplotlib colormap to a PyQtGraph ColorMap.
        
        Args:
            mpl_cmap_name (str): Name of the Matplotlib colormap.
            resolution (int): Number of discrete color steps (default is 256).
        
        Returns:
            pg.ColorMap: The equivalent PyQtGraph ColorMap.
        """
        import matplotlib.pyplot as plt
        mpl_cmap = plt.get_cmap(mpl_cmap_name)
        positions = np.linspace(0, 1, resolution)
        colors = [mpl_cmap(i) for i in positions]
        colors_rgb = [tuple(int(c * 255) for c in color[:3]) for color in colors]
        return pg.ColorMap(positions, colors_rgb)
                
            

    @classmethod
    def create_colormap_transparent_below_value(cls, mycmap: Union[str, Any], low_value_cuttoff:float=0.2, below_low_value_cuttoff_alpha_value: float=0.0, resampled_num_colors:int=7):
        """ Modifies the provided colormap by settings the opacity/alpha of all values below `low_value_cuttoff` (where values always go [0.0, 1.0]) to the value `below_low_value_cuttoff_alpha_value`
        Usage:
        
            from pyphocorehelpers.gui.Qt.color_helpers import ColormapHelpers
        
            additional_cmap_names = dict(zip(TrackTemplates.get_decoder_names(), ['red', 'purple', 'green', 'orange'])) # {'long_LR': 'red', 'long_RL': 'purple', 'short_LR': 'green', 'short_RL': 'orange'}

            long_epoch_config = long_short_display_config_manager.long_epoch_config.as_pyqtgraph_kwargs()
            short_epoch_config = long_short_display_config_manager.short_epoch_config.as_pyqtgraph_kwargs()

            color_dict = {'long_LR': long_epoch_config['brush'].color(), 'long_RL': apply_LR_to_RL_adjustment(long_epoch_config['brush'].color()),
                            'short_LR': short_epoch_config['brush'].color(), 'short_RL': apply_LR_to_RL_adjustment(short_epoch_config['brush'].color())}
            additional_cmap_names = {k: ColorFormatConverter.qColor_to_hexstring(v) for k, v in color_dict.items()}

            additional_cmaps = {k: ColormapHelpers.create_transparent_colormap(color_literal_name=v, lower_bound_alpha=0.1) for k, v in additional_cmap_names.items()}
        
        """
        from matplotlib.colors import LinearSegmentedColormap
        from pyphoplacecellanalysis.External.pyqtgraph.colormap import ColorMap
        
        if isinstance(mycmap, str):
            mycmap = pg.colormap.get(mycmap, source='matplotlib')

        # original_n_colors: int = mycmap.N
        # print(f'original_n_colors: {original_n_colors}')

        # Get colors by sampling the colormap
        # resampled_num_colors: int = 7  # Number of colors to extract
        if resampled_num_colors is None:
            resampled_num_colors: int = original_n_colors  # Number of colors to extract

        ## convert to LinearSegmented if needed:
        mycmap = cls.colormap_to_linear_segmented(cmap=mycmap, n_samples=resampled_num_colors)        
        assert isinstance(mycmap, (LinearSegmentedColormap, )), f"type(mycmap): {type(mycmap)}" 
        _resampled_cmap = mycmap.resampled(resampled_num_colors)


        sampled_color_reference_arr = np.array([(float(i) / float(resampled_num_colors - 1)) for i in range(resampled_num_colors)]) ## array ranging between 0.0 and 1.0
        sampled_color_reference_idxs = np.arange(len(sampled_color_reference_arr))
        sampled_colors = np.array([list(_resampled_cmap(i / (resampled_num_colors - 1))) for i in range(resampled_num_colors)])
        # sampled_colors.shape # (num_colors, 4)
        
        is_value_below_cutoff = (sampled_color_reference_arr < low_value_cuttoff)
        
        # sampled_color_reference_arr[is_value_below_cutoff] ## values
        below_cuttoff_indicies = sampled_color_reference_idxs[is_value_below_cutoff]
        
        # sampled_colors[below_cuttoff_indicies][-1] = 0.0 # set alpha

        # sampled_colors[is_value_below_cutoff][-1] = below_low_value_cuttoff_alpha_value # set alpha

        for idx in below_cuttoff_indicies:
            sampled_colors[idx][-1] = below_low_value_cuttoff_alpha_value # set alpha  

        # sampled_colors[0][-1] = 0.0 # set alpha
        # sampled_colors

        # Rebuild the colormap
        reconstructed_cmap = LinearSegmentedColormap.from_list(f"reconstructed_{_resampled_cmap.name}", sampled_colors)

        return reconstructed_cmap
                

@metadata_attributes(short_name=None, tags=['color', 'dataseries', 'series', 'helper'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2023-06-21 13:50', related_items=['UnitColoringMode'])
class ColorFormatConverter:
     
    @classmethod
    def _hexArgb_to_hexRGBA(cls, hex_Argb_str:str) -> str:
        """ converts a hexArgb string such as one output by `pen.color().name(QtGui.QColor.HexArgb)` to a regular hex_RGBA string like would be used for matplotlib.
        
        '#0b0049ff'
        
        QColor.HexArgb: '#AARRGGBB' A “#” character followed by four two-digit hexadecimal numbers (i.e. #AARRGGBB).
        Output Format (HexRGBA): '#RRGGBBAA'
        
        Usage:
            from pyphocorehelpers.gui.Qt.color_helpers import ColorFormatConverter
            from pyphocorehelpers.gui.Qt.color_helpers import hexArgb_to_hexRGBA
            pen=pg.mkPen('#0b0049')
            hex_Argb_str:str = pen.color().name(QtGui.QColor.HexArgb) # '#ff0b0049'
            hex_RGBA_str = hexArgb_to_hexRGBA(hex_Argb_str)
            hex_RGBA_str # '#0b0049ff'

        """
        hex_rgb_str_part = hex_Argb_str[3:] # get the rgb characters
        hex_alpha_str_part: str = hex_Argb_str[1:3] # get the "alpha" components
        hex_RGBA_str: str = f"#{hex_rgb_str_part}{hex_alpha_str_part}"
        return hex_RGBA_str

    @classmethod
    def qColor_to_hexstring(cls, qcolor: QtGui.QColor, include_alpha:bool=True, use_HexArgb_instead_of_HexRGBA:bool=False) -> str:
        """ converts a QColor to a hex string 
        
        include_alpha: if True, returns a hex string containing the alpha values
        use_HexArgb_instead_of_HexRGBA:bool; default False, don't use typically.
            If False results in a string like '#80ff000
        
        
        Notes on getting hex colors:
            getting the name of a QColor with .name(QtGui.QColor.HexRgb) results in a string like '#ff0000'
            getting the name of a QColor with .name(QtGui.QColor.HexArgb) results in a string like '#80ff0000'

        Usage:
            from pyphocorehelpers.gui.Qt.color_helpers import ColorFormatConverter
            ColorFormatConverter.qColor_to_hexstring(aQColor)
        """
        if not include_alpha:
            return qcolor.name(QtGui.QColor.HexRgb)
        else:
            hex_Argb_str = qcolor.name(QtGui.QColor.HexArgb)
            if use_HexArgb_instead_of_HexRGBA:
                return hex_Argb_str
            else:
                return cls._hexArgb_to_hexRGBA(hex_Argb_str)


    @classmethod
    def is_valid_hexstring(cls, a_label: str) -> bool:
        if not isinstance(a_label, str):
            return False

        s = a_label
        if s and s[0] == '#':
            s = s[1:]

        n = len(s)
        if n not in (3, 4, 6, 8):
            return False

        for c in s:
            if not (
                '0' <= c <= '9' or
                'a' <= c <= 'f' or
                'A' <= c <= 'F'
            ):
                return False

        return True


    # ==================================================================================================================== #
    # Color NDArray Conversions                                                                                             #
    # ==================================================================================================================== #
    @classmethod
    def auto_detect_color_NDArray_is_255_array_format(cls, colors_ndarray: np.ndarray) -> bool:
        """ tries to auto-detect the format of the color NDArray in terms of whether it contains 0.0-1.0 or 0.0-255.0 values. 
        returns True if it is 255_array_format, and False otherwise
        """
        return (not np.all(colors_ndarray <= 1.0)) # all are less than 1.0 implies that it NOT a 255_format_array



    @classmethod
    def Colors_NDArray_Convert_to_255_array(cls, colors_ndarray: np.ndarray) -> np.ndarray:
        """ takes an [4, nCell] np.array of (0.0 - 255.0) values for the color and converts it to a 0.0-1.0 array of the same shape.
        Reciprocal: Colors_NDArray_Convert_to_zero_to_one_array
        """
        converted_colors_ndarray = deepcopy(colors_ndarray)
        converted_colors_ndarray[0:2, :] *= 255 # [1.0, 0.0, 0.0, 1.0]
        return converted_colors_ndarray
    
    @classmethod
    def Colors_NDArray_Convert_to_zero_to_one_array(cls, colors_ndarray: np.ndarray) -> np.ndarray:
        """ takes an [4, nCell] np.array of 0.0-1.0 values for the color and converts it to a (0.0 - 255.0) array of the same shape.
        Reciprocal: Colors_NDArray_Convert_to_255_array
        """
        converted_colors_ndarray = deepcopy(colors_ndarray).astype(float)
        colors_shape = np.shape(converted_colors_ndarray)
        n_colors: int = colors_shape[0]
        assert n_colors in [3, 4], f"n_colors must be either 3 (RGB) or 4 (RGBA) but instead it is {n_colors}. Is the array transposed? colors_shape: {colors_shape}"
        if n_colors == 3:
            color_idx_range = np.arange(3) # 0:2, RGB
        elif n_colors == 4:
            color_idx_range = np.arange(4) # 0:3, RGBA
        else:
            raise NotImplementedError(f'n_colors: {n_colors}')
        
        print(f'color_idx_range: {color_idx_range}')
        converted_colors_ndarray[color_idx_range, :] /= 255
        # converted_colors_ndarray[0:2, :] /= 255 # UFuncTypeError: Cannot cast ufunc 'divide' output from dtype('float64') to dtype('uint8') with casting rule 'same_kind'
        return converted_colors_ndarray

    @classmethod
    def qColorsList_to_NDarray(cls, qcolors_list, is_255_array:bool) -> np.ndarray:
        """ takes a list[QColor] and returns a [4, nCell] np.array with the color for each in the list 
        
        is_255_array: bool - if False, all RGB color values are (0.0 - 1.0), else they are (0.0 - 255.0)
        I was having issues with this list being in the range 0.0-1.0 instead of 0-255.
        
        Note: Matplotlib requires zero_to_one_array format
        
        Extracted on 2024-08-30 from `pyphoplacecellanalysis.General.Mixins.DataSeriesColorHelpers.DataSeriesColorHelpers`

        """

        # allocate new neuron_colors array:
        n_cells = len(qcolors_list)
        neuron_colors = np.zeros((4, n_cells))
        for i, curr_qcolor in enumerate(qcolors_list):
            curr_color = curr_qcolor.getRgbF() # (1.0, 0.0, 0.0, 0.5019607843137255)
            neuron_colors[:, i] = curr_color[:]
        if is_255_array:
            neuron_colors = cls.Colors_NDArray_Convert_to_255_array(neuron_colors) 
        return neuron_colors
    

    @classmethod
    def colors_NDarray_to_qColorsList(cls, colors_ndarray: np.ndarray, is_255_array:Optional[bool]=None) -> list:
        """ Takes a [4, nCell] np.array and returns a list[QColor] with the color for each cell in the array
        
        is_255_array: bool - if False, all RGB color values are in range (0.0 - 1.0), else they are in range (0.0 - 255.0)
        
        Note: Matplotlib requires zero_to_one_array format
        
        Extracted on 2024-08-30 from `pyphoplacecellanalysis.General.Mixins.DataSeriesColorHelpers.DataSeriesColorHelpers`
        """
        if is_255_array is None:
            is_255_array = cls.auto_detect_color_NDArray_is_255_array_format(colors_ndarray)

        if is_255_array:
            colors_ndarray = cls.Colors_NDArray_Convert_to_zero_to_one_array(colors_ndarray)

        n_cells = colors_ndarray.shape[1]
        qcolors_list = []
        for i in range(n_cells):
            curr_color = QColor.fromRgbF(*colors_ndarray[:, i])
            qcolors_list.append(curr_color)
            
        return qcolors_list


    @classmethod
    def convert_pen_brush_to_matplot_kwargs(cls, pen, brush) -> Dict:
        """ converts a pyqtgraph (pen: QPen, brush: QBrush) combination into matplotlib kwargs dict 
        Usage:
            from pyphocorehelpers.gui.Qt.color_helpers import convert_pen_brush_to_matplot_kwargs

            matplotlib_rect_kwargs = convert_pen_brush_to_matplot_kwargs(pen, brush)
            matplotlib_rect_kwargs

        """
        return dict(linewidth=pen.widthF(), edgecolor=cls._hexArgb_to_hexRGBA(pen.color().name(QtGui.QColor.HexArgb)), facecolor=cls._hexArgb_to_hexRGBA(brush.color().name(QtGui.QColor.HexArgb)))


    # ==================================================================================================================================================================================================================================================================================== #
    # Compatibility functions with pyqtgraph                                                                                                                                                                                                                                               #
    # ==================================================================================================================================================================================================================================================================================== #
    @classmethod
    def colorTuple(cls, c):
        """Return a tuple (R,G,B,A) from a QColor
        Drop-in compatible replacewith with `pg.colorTuple(a_color)`
        """
        return c.getRgb()

    @classmethod
    def colorStr(cls, c):
        """Generate a hex string code from a QColor
        Drop-in compatible replacewith with `pg.colorStr(a_color)`
        Usage:
        
            ColorFormatConverter.colorStr(a_color)
        
        """
        return ('%02x'*4) % cls.colorTuple(c)


# ==================================================================================================================== #
# RectangleRenderTupleHelpers                                                                                          #
# ==================================================================================================================== #
QColorTuple = namedtuple('QColorTuple', ['hexColor', 'alpha'])
QPenTuple = namedtuple('QPenTuple', ['color', 'width'])
QBrushTuple = namedtuple('QBrushTuple', ['color'])


QPenFlatTuple = namedtuple('QPenFlatTuple', ['hexColor', 'alpha', 'width'])
QBrushFlatTuple = namedtuple('QBrushFlatTuple', ['hexColor', 'alpha'])


@metadata_attributes(short_name=None, tags=['class', 'helper', 'pyqtgraph', 'QPen', 'Qt', 'QBrush', 'Helpful', 'RectangleRenderTupleHelpers'], uses=['ColorFormatConverter'], used_by=['QColorColumnsAccessor'], creation_date='2026-02-02 11:50', related_items=[])
class ColorDataframeColumnHelpers:
    """ class for use in copying, serializing, etc the list of tuples used by IntervalRectsItem

    Refactored and generalized from `pyphoplacecellanalysis.GUI.PyQtPlot.Widgets.helpers.RectangleRenderTupleHelpers` on 2026-02-02
    Refactored out of `pyphoplacecellanalysis.GUI.PyQtPlot.Widgets.GraphicsObjects.IntervalRectsItem.IntervalRectsItem` on 2022-12-05 

    Usage:


        from pyphocorehelpers.gui.Qt.color_helpers import ColorDataframeColumnHelpers, ColorFormatConverter, QColorColumnsAccessor
        
    Known Usages:
        Used in `IntervalRectsItem` and `CustomIntervalRectsItem` to copy themselves

        # Copy Constructors: _________________________________________________________________________________________________ #
        def __copy__(self):
            independent_data_copy = ColorDataframeColumnHelpers.copy_data(self.data)
            return CustomIntervalRectsItem(independent_data_copy)
        
        def __deepcopy__(self, memo):
            independent_data_copy = ColorDataframeColumnHelpers.copy_data(self.data)
            return CustomIntervalRectsItem(independent_data_copy)
            # return CustomIntervalRectsItem(copy.deepcopy(self.data, memo))


    """
    @classmethod
    def QColor_to_simple_columns_dict(cls, value):
        """Resolves into basic datatypes:
        color: a HexRgb string (without opacity)
        alpha: a float value indicating the opacity
        """
        return {'hexColor': value.name(QtGui.QColor.HexRgb),'alpha':value.alphaF()}
    
    @classmethod
    def QColor_to_tuple(cls, value):
        return QColorTuple(hexColor=value.name(QtGui.QColor.HexRgb), alpha=value.alphaF())


    # _color_process_fn = lambda a_color: pg.colorStr(a_color) # a_pen.color()
    # _color_process_fn = lambda a_color: ColorDataframeColumnHelpers.QColor_to_simple_columns_dict(a_color)
    # _color_process_fn = lambda a_color: ColorFormatConverter.colorStr(a_color)
    _color_process_fn = lambda a_color: ColorFormatConverter.qColor_to_hexstring(a_color, include_alpha=True, use_HexArgb_instead_of_HexRGBA=False)


    @classmethod
    def QPen_to_dict(cls, a_pen):
        return {'color': cls._color_process_fn(a_pen.color()), 'width':a_pen.widthF()}
        # return {**cls.QColor_to_simple_columns_dict(a_pen.color()),'width':a_pen.widthF()}

    @classmethod
    def QBrush_to_dict(cls, a_brush):
        return {'color': cls._color_process_fn(a_brush.color())} # ,'gradient':a_brush.gradient()
        # return {**cls.QColor_to_simple_columns_dict(a_brush.color())} # ,'gradient':a_brush.gradient()

    @classmethod
    def QPen_to_tuple(cls, a_pen):
        return QPenTuple(color=cls._color_process_fn(a_pen.color()), width=a_pen.widthF())
        # return QPenTuple(**cls.QColor_to_simple_columns_dict(a_pen.color()), width=a_pen.widthF())

    @classmethod
    def QBrush_to_tuple(cls, a_brush):
        return QBrushTuple(color=cls._color_process_fn(a_brush.color()))
        # return QBrushTuple(**cls.QColor_to_simple_columns_dict(a_brush.color()))

    
    @classmethod
    def get_serialized_data(cls, tuples_data):
        """ converts the list of (float, float, float, float, QPen, QBrush) tuples or IntervalRectsItemData objects into a serialized format for serialization. 
        
        Handles both:
        - Tuples: (start_t, series_vertical_offset, duration_t, series_height, pen, brush) [+ optional label]
        - IntervalRectsItemData objects: with optional label field
        
        Returns serialized format: (start_t, series_vertical_offset, duration_t, series_height, pen_dict, brush_dict, label, is_interval_data)
        """            
        # """ converts the list of (float, float, float, float, QPen, QBrush) tuples into a list of (float, float, float, float, pen_color_hex:str, brush_color_hex:str) for serialization. """            
        # return [(start_t, series_vertical_offset, duration_t, series_height, cls.QPen_to_dict(pen), cls.QBrush_to_dict(brush)) for (start_t, series_vertical_offset, duration_t, series_height, pen, brush) in tuples_data]

        if not tuples_data:
            return []
        
        # Check if first item is IntervalRectsItemData (lazy check to avoid circular dependency)
        first_item = tuples_data[0]
        is_interval_data = hasattr(first_item, '__attrs_attrs__') and hasattr(first_item, 'start_t')
        
        result = []
        for item in tuples_data:
            if is_interval_data:
                # Handle IntervalRectsItemData object
                start_t = item.start_t
                series_vertical_offset = item.series_vertical_offset
                duration_t = item.duration_t
                series_height = item.series_height
                pen = item.pen
                brush = item.brush
                label = getattr(item, 'label', None)  # Optional label field
            else:
                # Handle tuple - unpack first 6 required fields
                start_t, series_vertical_offset, duration_t, series_height, pen, brush = item[:6]
                label = item[6] if len(item) > 6 else None  # Optional 7th field (label)
            
            # Serialize pen and brush to dicts
            serialized_item = (start_t, series_vertical_offset, duration_t, series_height, cls.QPen_to_dict(pen), cls.QBrush_to_dict(brush), label, is_interval_data)
            result.append(serialized_item)
        return result
    

    @classmethod
    def get_deserialized_data(cls, seralized_tuples_data):
        """ converts the serialized data back to the original format (tuples or IntervalRectsItemData objects)
        
        Inverse operation of .get_serialized_data(...).
        
        Handles both old format (6-7 elements) and new format (8 elements with type info).
        
        Usage:
            seralized_tuples_data = ColorDataframeColumnHelpers.get_serialized_data(tuples_data)
            tuples_data = ColorDataframeColumnHelpers.get_deserialized_data(seralized_tuples_data)
        """        
        # """ converts the list of (float, float, float, float, pen_color_hex:str, brush_color_hex:str) tuples back to the original (float, float, float, float, QPen, QBrush) list
        # Inverse operation of .get_serialized_data(...).        
        # Usage:
        #     seralized_tuples_data = ColorDataframeColumnHelpers.get_serialized_data(tuples_data)
        #     tuples_data = ColorDataframeColumnHelpers.get_deserialized_data(seralized_tuples_data)
        # """        
        # return [(start_t, series_vertical_offset, duration_t, series_height, pg.mkPen(pen_color_hex), pg.mkBrush(**brush_color_hex)) for (start_t, series_vertical_offset, duration_t, series_height, pen_color_hex, brush_color_hex) in seralized_tuples_data]

        if not seralized_tuples_data:
            return []
        
        # Check format: new format has 8 elements (includes is_interval_data flag)
        first_item = seralized_tuples_data[0]
        if len(first_item) == 8:
            # New format: includes is_interval_data flag
            use_objects = first_item[7]
        else:
            # Old format: assume tuples for backward compatibility
            use_objects = False
        
        # Lazy import to avoid circular dependency
        if use_objects:
            try:
                from pyphoplacecellanalysis.GUI.PyQtPlot.Widgets.GraphicsObjects.IntervalRectsItem import IntervalRectsItemData
            except ImportError:
                use_objects = False
        
        result = []
        for item in seralized_tuples_data:
            if len(item) == 8:
                # New format with type info
                start_t, series_vertical_offset, duration_t, series_height, pen_dict, brush_dict, label, is_interval_data = item
            elif len(item) == 7:
                # Old format: 7 elements (with label)
                start_t, series_vertical_offset, duration_t, series_height, pen_dict, brush_dict, label = item
            else:
                # Old format: 6 elements (no label)
                start_t, series_vertical_offset, duration_t, series_height, pen_dict, brush_dict = item
                label = None
            
            # Reconstruct pen and brush from dicts
            # pen_dict: {'color': str, 'width': float}
            # brush_dict: {'color': str}
            pen = pg.mkPen(pen_dict['color'], width=pen_dict.get('width', 1))
            brush = pg.mkBrush(brush_dict['color'])
            
            if use_objects:
                # Return IntervalRectsItemData objects
                if label is not None:
                    result.append(IntervalRectsItemData(start_t, series_vertical_offset, duration_t, series_height, pen, brush, label))
                else:
                    result.append(IntervalRectsItemData(start_t, series_vertical_offset, duration_t, series_height, pen, brush))
            else:
                # Return tuples (backward compatibility)
                if label is not None:
                    result.append((start_t, series_vertical_offset, duration_t, series_height, pen, brush, label))
                else:
                    result.append((start_t, series_vertical_offset, duration_t, series_height, pen, brush))
        return result



    @classmethod
    def copy_data(cls, tuples_data):
        seralized_tuples_data = cls.get_serialized_data(tuples_data).copy()
        return cls.get_deserialized_data(seralized_tuples_data)



# ==================================================================================================================================================================================================================================================================================== #
# QColor Pandas Dataframe Accessor for manipulating color columns                                                                                                                                                                                                                      #
# ==================================================================================================================================================================================================================================================================================== #

@pd.api.extensions.register_dataframe_accessor("qcolor")
class QColorColumnsAccessor:
    """ A Pandas pd.DataFrame representation of [start, stop, label] epoch intervals 
    
    Usage:
    
        from pyphocorehelpers.gui.Qt.color_helpers import ColorDataframeColumnHelpers, ColorFormatConverter, QColorColumnsAccessor
        
    """
    def __init__(self, pandas_obj):   
        pandas_obj = self._validate(pandas_obj)
        self._df = pandas_obj
        # initial_labels = deepcopy(list(self._df.columns))
        # extant_hex_color_labels = [k for k in initial_labels if k.starts]        
        # Optional: If the 'label' column of the dataframe is empty, should populate it with the index (after sorting) as a string.
        # self._obj['label'] = self._obj.index
        # self._df["label"] = self._df["label"].astype("str")


    @classmethod
    def _validate(cls, obj):
        """ just require it to be a dataframe """       
        assert isinstance(obj, pd.DataFrame)
        return obj # important! Must return the modified obj to be assigned (since its columns were altered by renaming


    @property
    def df(self) -> pd.DataFrame:
        """The df property."""
        return self._df
    @df.setter
    def df(self, value: pd.DataFrame):
        value = self._validate(value)
        self._df = value
        

    def find_valid_hex_columns(self) -> List[str]:
        """Return column names that are valid hex color labels (RGB/RGBA, with or without '#')."""
        is_valid = ColorFormatConverter.is_valid_hexstring
        valid_cols = []

        for col in self.df.columns:
            series = self.df[col]
            if series.dtype == object and series.map(is_valid).all():
                valid_cols.append(col)

        return valid_cols
    

    def convert_QColor_columns_to_hexcolor_columns(self, specific_QColor_column_names: Optional[List[str]]=None) -> Dict[str, str]:
        """Return column names that are valid hex color labels (RGB/RGBA, with or without '#')."""
        is_valid_QColor_column = lambda x: ((x is not None) and isinstance(x, (QColor, QColorTuple)))
                
        if specific_QColor_column_names is None:
            ## find columns with QColor values
            specific_QColor_column_names = []
            for col in self.df.columns:
                series = self.df[col]
                if series.dtype == object and series.map(is_valid_QColor_column).all():
                    specific_QColor_column_names.append(col)

        else:
            for col in specific_QColor_column_names:
                assert col in self.df.columns, f"col: '{col}' not found in self.df.columns: {list(self.df.columns)}"
                series = self.df[col]
                assert series.dtype == object, f"col: '{col}' series.dtype != object -- series.dtype: {series.dtype}"
                assert series.map(is_valid_QColor_column).all(), f"col: '{col}' contained invalid values, series: {series}"
            
        # self.df = self.df
        
        added_col_names = []
        added_col_names_map = {}
        for col in specific_QColor_column_names:
            new_col_name: str = f'{col}_hex'
            self.df[new_col_name] = self.df[col].map(lambda x: ColorFormatConverter.qColor_to_hexstring(x, include_alpha=True, use_HexArgb_instead_of_HexRGBA=False))
            # self.df[new_col_name] = self.df[col].map(lambda x: "#" + ColorDataframeColumnHelpers.QPen_to_dict(x)['color']).str.upper()
            added_col_names.append(new_col_name)
            added_col_names_map[col] = new_col_name
            
        return added_col_names_map
    


    def split_QPen_columns(self, specific_column_names: Optional[List[str]]=None) -> Dict[str, List[str]]:
        """Splits columns containing QPen values into two separate [f'{a_col}_color_hex', f'{a_col}_width] columns.

        Returns a dict mapping each original column name to the list of added column names [color_hex_col, width_col].
        """
        is_valid_QPen_column = lambda x: (x is not None) and isinstance(x, (QPen, QPenTuple))

        if specific_column_names is None:
            specific_column_names = []
            for col in self.df.columns:
                series = self.df[col]
                if series.dtype == object and series.map(is_valid_QPen_column).all():
                    specific_column_names.append(col)
        else:
            for col in specific_column_names:
                assert col in self.df.columns, f"col: '{col}' not found in self.df.columns: {list(self.df.columns)}"
                series = self.df[col]
                assert series.dtype == object, f"col: '{col}' series.dtype != object -- series.dtype: {series.dtype}"
                assert series.map(is_valid_QPen_column).all(), f"col: '{col}' contained invalid values, series: {series}"

        added_col_names_map = {}
        for col in specific_column_names:
            def pen_to_dict(pen):
                if isinstance(pen, QPenTuple):
                    return {'color': pen.color, 'width': pen.width}
                return ColorDataframeColumnHelpers.QPen_to_dict(pen)

            color_col = f'{col}_color_hex'
            width_col = f'{col}_width'
            self.df[color_col] = self.df[col].map(lambda x: pen_to_dict(x)['color'])
            self.df[width_col] = self.df[col].map(lambda x: pen_to_dict(x)['width'])
            added_col_names_map[col] = [color_col, width_col]

        return added_col_names_map



    def split_QBrush_columns(self, specific_column_names: Optional[List[str]]=None) -> Dict[str, List[str]]:
        """Splits columns containing QBrush values into a separate f'{a_col}_color_hex' column.

        Returns a dict mapping each original column name to the list of added column names [color_hex_col].
        """
        is_valid_QBrush_column = lambda x: (x is not None) and isinstance(x, (QBrush, QBrushTuple))

        if specific_column_names is None:
            specific_column_names = []
            for col in self.df.columns:
                series = self.df[col]
                if series.dtype == object and series.map(is_valid_QBrush_column).all():
                    specific_column_names.append(col)
        else:
            for col in specific_column_names:
                assert col in self.df.columns, f"col: '{col}' not found in self.df.columns: {list(self.df.columns)}"
                series = self.df[col]
                assert series.dtype == object, f"col: '{col}' series.dtype != object -- series.dtype: {series.dtype}"
                assert series.map(is_valid_QBrush_column).all(), f"col: '{col}' contained invalid values, series: {series}"

        added_col_names_map = {}
        for col in specific_column_names:
            def brush_to_dict(brush):
                if isinstance(brush, QBrushTuple):
                    return {'color': brush.color}
                return ColorDataframeColumnHelpers.QBrush_to_dict(brush)

            color_col = f'{col}_color_hex'
            self.df[color_col] = self.df[col].map(lambda x: brush_to_dict(x)['color'])
            added_col_names_map[col] = [color_col]

        return added_col_names_map


    def _detect_split_QPen_columns(self) -> Dict[str, List[str]]:
        """Detect split QPen columns by naming: *_color_hex + *_width pairs. Returns base_col -> [color_col, width_col]."""
        mapping: Dict[str, List[str]] = {}
        for col in self.df.columns:
            if col.endswith('_color_hex'):
                base = col[:-10]  # remove '_color_hex'
                width_col = f'{base}_width'
                if width_col in self.df.columns:
                    mapping[base] = [col, width_col]
        return mapping


    def _detect_split_QBrush_columns(self) -> Dict[str, List[str]]:
        """Detect split QBrush columns by naming: *_color_hex with no matching *_width (brush has only color). Returns base_col -> [color_col]."""
        mapping: Dict[str, List[str]] = {}
        for col in self.df.columns:
            if col.endswith('_color_hex'):
                base = col[:-10]  # remove '_color_hex'
                width_col = f'{base}_width'
                if width_col not in self.df.columns:
                    mapping[base] = [col]
        return mapping


    def merge_QPen_columns(self, split_mapping: Optional[Dict[str, List[str]]] = None, drop_split_columns: bool = False) -> Dict[str, str]:
        """Rebuild QPen columns from split color_hex and width columns.

        If split_mapping is None, detects pairs of columns named *_color_hex and *_width.
        Returns dict mapping each base column name to itself (for API consistency).
        """
        if split_mapping is None:
            split_mapping = self._detect_split_QPen_columns()
        for base_col, (color_col, width_col) in split_mapping.items():
            self.df[base_col] = [
                pg.mkPen(color, width=width)
                for color, width in zip(self.df[color_col], self.df[width_col])
            ]
            if drop_split_columns:
                self.df.drop(columns=[color_col, width_col], inplace=True)
        return {base: base for base in split_mapping}


    def merge_QBrush_columns(self, split_mapping: Optional[Dict[str, List[str]]] = None, drop_split_columns: bool = False) -> Dict[str, str]:
        """Rebuild QBrush columns from split color_hex column.

        If split_mapping is None, detects columns named *_color_hex that have no matching *_width (brush-only).
        Returns dict mapping each base column name to itself (for API consistency).
        """
        if split_mapping is None:
            split_mapping = self._detect_split_QBrush_columns()
        for base_col, (color_col,) in split_mapping.items():
            self.df[base_col] = self.df[color_col].map(lambda c: pg.mkBrush(c))
            if drop_split_columns:
                self.df.drop(columns=[color_col], inplace=True)
        return {base: base for base in split_mapping}

