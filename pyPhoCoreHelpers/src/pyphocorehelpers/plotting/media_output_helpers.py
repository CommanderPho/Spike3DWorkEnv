from __future__ import annotations # prevents having to specify types for typehinting as strings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ## typehinting only imports here
    from pyphoplacecellanalysis.Pho2D.data_exporting import HeatmapExportKind

import os
import io
from typing import Dict, List, Tuple, Optional, Callable, Union, Any
import nptyping as ND
from nptyping import NDArray
import numpy as np
import pandas as pd
from pathlib import Path
# import cv2
from copy import deepcopy
from glob import glob

import matplotlib.pyplot as plt # for export_array_as_image
from PIL import Image, ImageOps, ImageFilter # for export_array_as_image
from PIL import ImageDraw, ImageFont

from plotly.graph_objects import Figure as PlotlyFigure # required for `fig_to_clipboard`
from matplotlib.figure import FigureBase
# from pyphoplacecellanalysis.SpecificResults.PendingNotebookCode import copy_image_to_clipboard # required for `fig_to_clipboard`

from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes
from pyphocorehelpers.programming_helpers import copy_image_to_clipboard
from pyphocorehelpers.image_helpers import ImageHelpers
from pyphocorehelpers.assertion_helpers import Assert

# from pyphoplacecellanalysis.Pho2D.data_exporting import HeatmapExportKind

from enum import Enum, auto


class ImageStackOrientation(Enum):
    """ The orientation upon which to stack a set of images
    
    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import ImageStackOrientation

        stack_orientations: List[ImageStackOrientation] = [ImageStackOrientation.VERTICAL]
        for an_orientation in stack_orientations:
            _single_epoch_combined_img = an_orientation.stack_images(_single_epoch_row, padding=combined_img_padding, separator_color=combined_img_separator_color)    
            _single_epoch_single_series_single_export_type_rows_list.append(_single_epoch_combined_img)
            ## Save the image:
            _img_path = _output_combined_dir.joinpath(f'merged_{an_orientation.name}_{known_epoch_type_name}[{i}].png').resolve()
            _single_epoch_combined_img.save(_img_path)
            _output_combined_image_save_dirs.append(_img_path)
    """
    VERTICAL = auto()
    HORIZONTAL = auto()
    GRID = auto()
    
    @property
    def is_vertical(self) -> bool:
        return (self.name == ImageStackOrientation.VERTICAL.name)
    
    @property
    def is_horizontal(self) -> bool:
        return (self.name == ImageStackOrientation.HORIZONTAL.name)
    
    @property
    def is_grid(self) -> bool:
        return (self.name == ImageStackOrientation.GRID.name)

    @property
    def shortname(self) -> str:
        """ Abbreviation like 'V' or 'H' """
        return self.name.upper()[0] ## Only the first letter
        # return self.name.lower()

    def __str__(self):
        return self.name

    @classmethod
    def list_values(cls):
        """Returns a list of all enum values"""
        return list(cls)

    @classmethod
    def list_names(cls):
        """Returns a list of all enum names"""
        return [e.name for e in cls]
    
    def stack_images(self, *args, **kwargs):
        """ shortcut to perform image stacking
        Usage:
        
            from pyphocorehelpers.plotting.media_output_helpers import ImageStackOrientation
            
        """
        if self.name == ImageStackOrientation.VERTICAL.name:
            return vertical_image_stack(*args, **kwargs)
        elif self.name == ImageStackOrientation.HORIZONTAL.name:
            return horizontal_image_stack(*args, **kwargs)
        elif self.name == ImageStackOrientation.GRID.name:
            return image_grid(*args, **kwargs)
        else:
            raise NotImplementedError(f'self: {self}')



def add_border(image: Image.Image, border_size: int = 5, border_color: tuple = (0, 0, 0)) -> Image.Image:
    return ImageOps.expand(image, border=border_size, fill=border_color)

def add_shadow(image: Image.Image, offset: int = 5, background_color: tuple = (0, 0, 0, 0), shadow_color: tuple = (0, 0, 0, 255)) -> Image.Image:
    total_width = image.width + offset
    total_height = image.height + offset

    shadow = Image.new('RGBA', (total_width, total_height), background_color)
    shadow.paste(image, (offset, offset))

    shadow_layer = Image.new('RGBA', (total_width, total_height), shadow_color)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=offset))

    shadow = Image.alpha_composite(shadow_layer, shadow)

    return shadow


def img_data_to_greyscale(img_data: NDArray, min_val: Optional[float]=None, max_val: Optional[float]=None, should_invert: bool=False) -> NDArray[np.uint8]:
    """ rescales the img_data array to 0-255 
    
    if `should_invert == True`, higher values are darker (with max_val == 1.0)

    Usage 1:
        from pyphocorehelpers.plotting.media_output_helpers import img_data_to_greyscale
        
        norm_array = img_data_to_greyscale(img_data)

    Usage 2:
        from pyphocorehelpers.plotting.media_output_helpers import img_data_to_greyscale

        norm_array = img_data_to_greyscale(img_data, min_val = kwargs.pop('vmin', None), max_val = kwargs.pop('vmax', None), should_invert=True)

    """
    # norm_array = (img_data - np.min(img_data)) / np.ptp(img_data) ## Default

    # Normalize your array to 0-1 using nan-aware functions
    
    if min_val is None:
        min_val = np.nanmin(img_data)
    if max_val is None:
        max_val = np.nanmax(img_data)


    if np.all(np.isnan(img_data)):
        ## Image contains only np.nan values, we cannot normalize it.
        ## okay to just use the NaNs directly I guess
        norm_array = img_data
    elif (min_val == 0) and (max_val == 0):
        assert np.nansum(img_data) == 0.0, f"this should only occur when the image is all zeros, but the image: \nimg_data: {img_data}"
        # assert np.allclose(img_data, 0.0, equal_nan=True), f"this should only occur when the image is all zeros, but the image: \nimg_data: {img_data}" ## doesn't work for images with all zeros except they contain np.nan somewhere (making the np.allclose(..., 0.0) comparison fail
        ## okay to just use the zeros directly
        norm_array = img_data
    else:
        assert (min_val < max_val), f"min_val: {min_val}, max_val: {max_val}, img_data: {img_data}"
        ptp_val = max_val - min_val
        norm_array = (img_data - min_val) / ptp_val

    # Scale to 0-255 and convert to uint8
    if should_invert:
        # Invert the values: higher values become darker (0), lower values become lighter (255)
        return (255 - (norm_array * 255)).astype(np.uint8)
    else:
        # Original behavior: higher values become lighter (255), lower values become darker (0)
        return (norm_array * 255).astype(np.uint8)


@metadata_attributes(short_name=None, tags=['image','post-hoc','export', 'posterior'], input_requires=[], output_provides=[], uses=[], used_by=['ImagePostRenderFunctionSets'], creation_date='2025-04-01 00:00', related_items=[])
class ImageOperationsAndEffects:
    
    @classmethod
    def create_fn_builder(cls, a_fn, **static_kwargs):
        """  Creates a function builder that captures static parameters and allows dynamic parameters to be added later.
        
        
        a_fn = ImageOperationsAndEffects.create_fn_builder(ImageOperationsAndEffects.add_solid_border, border_color = (0, 0, 0, 255))
        
        """
        def _create_new_img_operation_function(*dynamic_args, **dynamic_kwargs):
            """Create a function that adds a specific label to an image."""
            final_kwargs = (deepcopy(static_kwargs) | dynamic_kwargs) ## override any static kwargs with the dynamic ones
            return lambda an_img: a_fn(an_img, *dynamic_args, **final_kwargs)
        
        return _create_new_img_operation_function


    # @classmethod
    # def add_simple_bottom_label(cls, image: Image.Image, label_text: str, padding: int = None, font_size: int = None,  
    #                     text_color: tuple = (0, 0, 0), background_color: tuple = (255, 255, 255, 255), 
    #                     with_text_outline: bool = False, relative_font_size: float = 0.10, 
    #                     relative_padding: float = 0.025) -> Image.Image:
    #     """Adds a horizontally centered label underneath the bottom of an image.
        
    #     Parameters:
    #     -----------
    #     image : Image.Image
    #         The PIL Image to add a label to
    #     label_text : str
    #         The text to display as the label
    #     padding : int, optional
    #         Vertical padding between image and label. If None, calculated from relative_padding.
    #     font_size : int, optional
    #         Font size for the label text. If None, calculated from relative_font_size.
    #     text_color : tuple, optional
    #         RGB color for the text, by default (0, 0, 0) (black)
    #     background_color : tuple, optional
    #         RGBA color for the label background, by default (255, 255, 255, 255) (white)
    #     with_border : bool, optional
    #         Whether to add a border around the text, by default True
    #     relative_font_size : float, optional
    #         Font size as a proportion of image height, by default 0.03 (3% of image height)
    #     relative_padding : float, optional
    #         Padding as a proportion of image height, by default 0.02 (2% of image height)
            
    #     Returns:
    #     --------
    #     Image.Image
    #         A new image with the label added below the original image
            
    #     Usage:
    #     ------
    #     from pyphocorehelpers.plotting.media_output_helpers import add_bottom_label
        
    #     # Create an image with a label that scales with image size
    #     labeled_image = add_bottom_label(original_image, "Time (seconds)", relative_font_size=0.04)
    #     labeled_image
    #     """
    #     # Calculate font size and padding based on image height if not provided
    #     img_height = image.height
        
    #     if font_size is None:
    #         font_size = max(int(img_height * relative_font_size), 20)  # Minimum font size of 8
        
    #     if padding is None:
    #         padding = max(int(img_height * relative_padding), 10)  # Minimum padding of 5
        
    #     # Try to load a nicer font if available, otherwise use default
    #     try:
    #         # Try to use a common font that should be available on most systems
    #         # get a font
    #         font = ImageHelpers.get_font('FreeMono.ttf', size=font_size)
    #         # font = ImageFont.truetype("Arial", font_size)
    #     except IOError:
    #         # Fall back to default font with specified size
    #         try:
    #             # For newer Pillow versions that support size in load_default
    #             font = ImageFont.load_default(size=font_size)
    #         except TypeError:
    #             # For older Pillow versions that don't support size parameter
    #             default_font = ImageFont.load_default()
    #             # Try to find a bitmap font of appropriate size as alternative
    #             try:
    #                 font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    #             except IOError:
    #                 # If all else fails, use the default font
    #                 font = default_font
    #                 print(f"Warning: Could not load font with specified size {font_size}. Text may appear smaller than expected.")


    #     # Create a temporary drawing context to measure text dimensions
    #     temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    #     temp_draw = ImageDraw.Draw(temp_img)
        
    #     # Use getbbox() for newer Pillow versions, fallback to textsize()
    #     try:
    #         # For newer Pillow versions
    #         bbox = temp_draw.textbbox((0, 0), label_text, font=font)
    #         text_width = bbox[2] - bbox[0]
    #         text_height = bbox[3] - bbox[1]
    #     except AttributeError:
    #         # For older Pillow versions
    #         text_width, text_height = temp_draw.textsize(label_text, font=font)
        
    #     # Create a new image with space for the label
    #     new_width = image.width
    #     new_height = image.height + padding + text_height + padding
        
    #     # Create the new image with the background color
    #     if image.mode == 'RGBA':
    #         new_image = Image.new('RGBA', (new_width, new_height), background_color)
    #     else:
    #         # Convert background_color to RGB if the image is not RGBA
    #         new_image = Image.new(image.mode, (new_width, new_height), background_color[:3])
        
    #     # Paste the original image at the top
    #     new_image.paste(image, (0, 0))
        
    #     # Create a drawing context for the new image
    #     draw = ImageDraw.Draw(new_image)
        
    #     # Calculate the position to center the text horizontally
    #     text_x = (new_width - text_width) // 2
    #     text_y = image.height + padding
        
    #     # Draw the text with or without border
    #     if with_text_outline:
    #         # Calculate border thickness based on font size
    #         border_thickness = max(1, int(font_size * 0.05))  # 5% of font size, minimum 1px
            
    #         def draw_text_with_border(draw, x, y, text, font, fill, thickness=1):
    #             # Draw shadow/border (using black color)
    #             shadow_color = (0, 0, 0)
    #             for dx in range(-thickness, thickness + 1):
    #                 for dy in range(-thickness, thickness + 1):
    #                     if dx != 0 or dy != 0:  # Skip the center position
    #                         draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    #             # Draw text itself
    #             draw.text((x, y), text, font=font, fill=fill)
                
    #         draw_text_with_border(draw, text_x, text_y, label_text, font, fill=text_color, thickness=border_thickness)
    #     else:
    #         # Draw text without border
    #         draw.text((text_x, text_y), label_text, font=font, fill=text_color)
        
    #     return new_image



    @classmethod
    def add_boxed_adjacent_label(cls, image: Image.Image, label_text: str, image_edge: str = 'top', # ['top', 'left', 'right', 'bottom']
                                 padding: int = None, font_size: int = None,
                                text_color: tuple = (255, 255, 255), background_color: tuple = (66, 66, 66, 255),
                                text_outline_shadow_color=None, relative_font_size: float = 0.06,
                                relative_padding: float = 0.025, fixed_label_region_size: Optional[Tuple[Optional[int], Optional[int]]] = None,
                                font='ndastroneer.ttf', 
                                debug_print=False, **text_kwargs) -> Image.Image:
        """Adds a box containing an appropriately oriented text label (vertical for L/R edge, horizontal for Top/Bottom edge)
        and concatenates it to that edge of the image.
        
        Usage:
            from pyphocorehelpers.plotting.media_output_helpers import vertical_image_stack, horizontal_image_stack, image_grid, ImageOperationsAndEffects
            
            _out_row_stack = ImageOperationsAndEffects.add_boxed_adjacent_label(_out_row_stack, 'global', image_edge='top', font_size=48, text_color="#000000",
                                            background_color=(255, 255, 255, 0),
                                            )
                                            
        """
        assert image_edge in ('top', 'bottom', 'left', 'right'), f"Invalid image_edge: {image_edge}, valid options: ['top', 'left', 'right', 'bottom']"
        original_width, original_height = image.size
        if fixed_label_region_size is None:
            fixed_label_region_size = [None, None]

        # Font size / padding
        ref_dim = original_height if image_edge in ('top', 'bottom') else original_width
        if font_size is None:
            font_size = max(int(ref_dim * relative_font_size), 8)
        if padding is None:
            padding = max(int(ref_dim * relative_padding), 0)

        # Load font
        try:
            font_obj = ImageHelpers.get_font(font, size=font_size, allow_caching=True)
        except IOError:
            try:
                font_obj = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except IOError:
                font_obj = ImageFont.load_default()

        # Measure text
        tmp_img = Image.new('RGBA', (1, 1))
        tmp_draw = ImageDraw.Draw(tmp_img)
        text_w, text_h = tmp_draw.textsize(label_text, font=font_obj, **text_kwargs)

        # Determine label box size
        fw, fh = fixed_label_region_size if fixed_label_region_size else (None, None)
        if image_edge in ('top', 'bottom'):
            label_box_w = fw if fw is not None else original_width
            label_box_h = fh if fh is not None else text_h + 2 * padding
        else:
            label_box_w = fw if fw is not None else text_h + 2 * padding
            label_box_h = fh if fh is not None else original_height

        label_img = Image.new('RGBA', (label_box_w, label_box_h), background_color)
        draw_label = ImageDraw.Draw(label_img)

        # Draw text (orientation aware)
        if image_edge in ('top', 'bottom'):
            tx, ty = (label_box_w - text_w) // 2, (label_box_h - text_h) // 2
            if text_outline_shadow_color:
                border_thickness = max(1, int(font_size * 0.05))
                for dx in range(-border_thickness, border_thickness + 1):
                    for dy in range(-border_thickness, border_thickness + 1):
                        if dx or dy:
                            draw_label.text((tx + dx, ty + dy), label_text, fill=text_outline_shadow_color, font=font_obj, **text_kwargs)
            draw_label.text((tx, ty), label_text, fill=text_color, font=font_obj, **text_kwargs)
        else:
            vert_img = Image.new('RGBA', (text_w + 2 * padding, text_h + 2 * padding), (0, 0, 0, 0))
            vert_draw = ImageDraw.Draw(vert_img)
            if text_outline_shadow_color:
                border_thickness = max(1, int(font_size * 0.05))
                for dx in range(-border_thickness, border_thickness + 1):
                    for dy in range(-border_thickness, border_thickness + 1):
                        if dx or dy:
                            vert_draw.text((padding + dx, padding + dy), label_text, fill=text_outline_shadow_color, font=font_obj, **text_kwargs)
            vert_draw.text((padding, padding), label_text, fill=text_color, font=font_obj, **text_kwargs)
            if image_edge == 'left':
                vert_img = vert_img.rotate(90, expand=True)
            else:
                vert_img = vert_img.rotate(270, expand=True)
            y_off = (label_box_h - vert_img.height) // 2
            x_off = (label_box_w - vert_img.width) // 2
            label_img.paste(vert_img, (x_off, y_off), vert_img)

        # Concatenate
        if image_edge == 'top':
            new_img = Image.new('RGBA', (max(original_width, label_box_w), label_box_h + original_height), (0, 0, 0, 0))
            new_img.paste(label_img, (0, 0))
            new_img.paste(image, (0, label_box_h))
        elif image_edge == 'bottom':
            new_img = Image.new('RGBA', (max(original_width, label_box_w), original_height + label_box_h), (0, 0, 0, 0))
            new_img.paste(image, (0, 0))
            new_img.paste(label_img, (0, original_height))
        elif image_edge == 'left':
            new_img = Image.new('RGBA', (label_box_w + original_width, max(original_height, label_box_h)), (0, 0, 0, 0))
            new_img.paste(label_img, (0, 0))
            new_img.paste(image, (label_box_w, 0))
            
        elif image_edge == 'right':
            new_img = Image.new('RGBA', (original_width + label_box_w, max(original_height, label_box_h)), (0, 0, 0, 0))
            new_img.paste(image, (0, 0))
            new_img.paste(label_img, (original_width, 0))            
        else:
            raise NotImplementedError(f"unknown image_edge value: '{image_edge}'. Valid values are in: ['top', 'left', 'right', 'bottom'] ")

        if debug_print:
            print(f"add_boxed_adjacent_label: edge={image_edge}, box=({label_box_w}x{label_box_h}), font_size={font_size}, padding={padding}")

        return new_img

 

    @classmethod
    def add_bottom_label(cls, image: Image.Image, label_text: str, padding: int = None, font_size: int = None,  
                        text_color: tuple = (255, 255, 255), background_color: tuple = (66, 66, 66, 255), 
                        text_outline_shadow_color=None,
                        relative_font_size: float = 0.06,
                        relative_padding: float = 0.025, fixed_label_region_height: Optional[int] = 520,
                        # font='OpenSansCondensed-LightItalic.ttf',
                        font='ndastroneer.ttf',
                        debug_print=False,
                        ) -> Image.Image:
        """Adds a vertically oriented label at the bottom of an image.

        This is used when building combined posterior images (one for each decoder) to add a band at the bottom containing a label with the epoch start timestamp.
        
        """

        # Calculate font size and padding based on image height if not provided
        original_img_height: int = deepcopy(image.height)
        original_img_width: int = deepcopy(image.width) 
            
        if font_size is None:
            font_size = max(int(original_img_height * relative_font_size), 20)  # Minimum font size of 8
            if debug_print:
                print(f'computing font size with relative_font_size: {relative_font_size}: font_size: {font_size} |', end='\t')
        if padding is None:
            padding = max(int(original_img_height * relative_padding), 0)  # Minimum padding of 0
        
        # Try to load a nicer font if available, otherwise use default
        try:
            font = ImageHelpers.get_font(font, size=font_size, allow_caching=True) # 'FreeMono.ttf'
        except IOError:
            # Fall back to default font with specified size
            try:
                font = ImageFont.load_default(size=font_size)
            except TypeError:
                default_font = ImageFont.load_default()
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                except IOError:
                    font = default_font
                    print(f"Warning: Could not load font with specified size {font_size}. Text may appear smaller than expected.")


        # label_kwargs = dict(font=font, align='center', anchor="mm") ## WORKS!, seems to be aligned better for small images, worse for large ones
        # label_kwargs = dict(font=font, align='center', anchor="ms") ## works okay.. #TODO 2025-05-27 15:39: - [ ] Seems to cut-off labels (all of them) for some reason?
        label_kwargs = dict(font=font, align='center', anchor="mt") ## NOW working, but has too much space on the bottom (because I add padding somewhere)
        
        # Create a temporary drawing context to measure text dimensions
        _temp_empty_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        _temp_empty_draw = ImageDraw.Draw(_temp_empty_img)
        
        required_text_width, required_text_height = _temp_empty_draw.textsize(label_text, font=font, spacing=0)
        
        required_text_height = required_text_height # + padding
        required_text_width = required_text_width # + padding


        # For vertical text, we need to swap width and height
        rotated_text_width: int = deepcopy(required_text_height)  # After 90 degree rotation
        rotated_text_height: int = deepcopy(required_text_width)  # After 90 degree rotation
        
        if debug_print:
            print(f'rotated_text_width: {rotated_text_width}, rotated_text_height: {rotated_text_height}', end='\t')
            
        if fixed_label_region_height is not None:
            if ((padding + rotated_text_height) > fixed_label_region_height):
                raise ValueError(f'Needed spacing for the label exceeds the specfied fixed_label_region_height: {fixed_label_region_height}, required space (padding + rotated_text_height): {(padding + rotated_text_height)}, padding: {padding}, rotated_text_height: {rotated_text_height}.')
            active_total_label_region_height: int = fixed_label_region_height ## override with the `fixed_label_region_height`
        else:
            active_total_label_region_height: int = (padding + rotated_text_height)

        # Create a new image with space for the label
        new_width: int = deepcopy(original_img_width)
        new_height: int = int(original_img_height + active_total_label_region_height)

            
        # ==================================================================================================================================================================================================================================================================================== #
        # Create the `new_larger_image` with the text label at the bottom                                                                                                                                                                                                                      #
        # ==================================================================================================================================================================================================================================================================================== #
        # Create the new image with the background color
        if image.mode == 'RGBA':
            new_larger_image = Image.new('RGBA', (new_width, new_height), background_color)
        else:
            new_larger_image = Image.new(image.mode, (new_width, new_height), background_color[:3])
        
        if debug_print:
            print(f'new_larger_image.size(w: {new_width}, h: {new_height}', end='\t')
            

        # Paste the original image at the top
        new_larger_image.paste(image, (0, 0))
        

        # ==================================================================================================================================================================================================================================================================================== #
        # Create the temporary `_temp_label_image` which is to be rotated                                                                                                                                                                                                                      #
        # ==================================================================================================================================================================================================================================================================================== #
        # Create a transparent background for the text
        # _debug_red_color = (255, 0, 0, 90)
        _clear_color = (0, 0, 0, 0)
        _active_label_bg_color = _clear_color
        _temp_label_image = Image.new('RGBA', (required_text_width, required_text_height), _active_label_bg_color)
        _temp_draw_label = ImageDraw.Draw(_temp_label_image)
        
        _internal_temp_box_text_x: int = (required_text_width // 2)
        _internal_temp_box_text_y: int = 0 # (font_size // 2)        
        
        # print(f'text_width: {text_width}, text_height: {text_height}, _internal_temp_box_text_x: {_internal_temp_box_text_x}, _internal_temp_box_text_y: {_internal_temp_box_text_y}')

        # Draw the text
        if (text_outline_shadow_color is not None):
            # Calculate border thickness based on font size
            border_thickness = max(1, int(font_size * 0.05))  # 5% of font size, minimum 1px
            
            # Draw text with outline
            for dx in range(-border_thickness, border_thickness + 1):
                for dy in range(-border_thickness, border_thickness + 1):
                    if dx != 0 or dy != 0:  # Skip the center position
                        _temp_draw_label.text((dx, dy), label_text, fill=text_outline_shadow_color, **label_kwargs)
            
            # Draw the main text
            # draw_label_temp.text((0, 0), label_text, fill=text_color, **label_kwargs)
            _temp_draw_label.text((_internal_temp_box_text_x, _internal_temp_box_text_y), label_text, fill=text_color, **label_kwargs)
        else:
            # Draw text without an outline
            _temp_draw_label.text((_internal_temp_box_text_x, _internal_temp_box_text_y), label_text, fill=text_color, **label_kwargs) # , direction=''
        
        
        # Rotate the text 270 degrees (so it reads from bottom to top)
        _temp_label_image = _temp_label_image.rotate(270, expand=1)

        # Get the dimensions of the rotated text image
        # rotated_width, rotated_height = _temp_label_image.size

        # Calculate position to center the text horizontally
        # For 270 degree rotation, we need to center based on the height of the original text
        # because after rotation, the height becomes the width
        # text_x = (new_width - rotated_width) // 2 ## WORKS, centers the result: 
        text_x = 0 ## WORKS, centers the result: 
        text_y = original_img_height + padding  # Position at the bottom of the original image plus padding

        # Paste the rotated text at the bottom center of the image
        new_larger_image.paste(_temp_label_image, (text_x, text_y), _temp_label_image)

        if debug_print:
            print(f'done.', end='\n') ## terminate the line
            
        return new_larger_image


    @classmethod
    def add_overlayed_text(cls, image: Image.Image, label_text: str, 
                                 padding: int = None, font_size: int = None,
                                 text_color: tuple = (255, 255, 255), 
                                 background_color: tuple = (0, 0, 0, 0),
                                 text_outline_shadow_color: Optional[tuple] = None,
                                 relative_font_size: float = 0.04,
                                 relative_padding: float = 0.02,
                                 font: str = 'ndastroneer.ttf',
                                 corner: str = 'top-left',
                                 inverse_scale_factor: Optional[Tuple]=None,
                                 debug_print: bool = False, **text_kwargs) -> Image.Image:
        """Adds a text label as an overlay in the specified corner of an image with a transparent background.
        
        This function creates a text overlay that sits on top of the original image without changing
        its dimensions. The text has a semi-transparent background for better readability.
        
        Parameters:
        -----------
        image : Image.Image
            The PIL Image to add the overlay label to
        label_text : str
            The text to display as the overlay
        padding : int, optional
            Padding around the text in pixels. If None, calculated based on relative_padding
        font_size : int, optional
            Font size in pixels. If None, calculated based on relative_font_size
        text_color : tuple, optional
            RGB or RGBA color for the text, by default (255, 255, 255) (white)
        background_color : tuple, optional
            RGBA color for the background rectangle, by default (0, 0, 0, 128) (semi-transparent black)
        text_outline_shadow_color : tuple, optional
            RGB or RGBA color for text outline/shadow. If None, no outline is drawn
        relative_font_size : float, optional
            Font size as a fraction of image height, by default 0.04 (4% of image height)
        relative_padding : float, optional
            Padding as a fraction of image height, by default 0.02 (2% of image height)
        font : str, optional
            Font file name to use, by default 'ndastroneer.ttf'
        corner : str, optional
            Corner to place the overlay: 'top-left', 'top-right', 'bottom-left', 'bottom-right', 
            by default 'top-left'
        debug_print : bool, optional
            Whether to print debug information, by default False
            
        Returns:
        --------
        Image.Image
            A new image with the text overlay added (same dimensions as original)
            
        Usage:
        ------
        from pyphocorehelpers.plotting.media_output_helpers import ImageOperationsAndEffects
        
        # Add a simple overlay
        labeled_image = ImageOperationsAndEffects.add_top_left_overlay_label(
            image, "Session 1", text_color=(255, 255, 0)
        )
        
        # Add overlay with custom styling
            ## Add overlay text to `an_active_img`
            an_active_img = ImageOperationsAndEffects.add_overlayed_text(an_active_img, a_decoder_name, font_size=48, text_color="#FF00EACA", stroke_width=1, stroke_fill="#000000")
        """
        
        # Validate corner parameter
        valid_corners = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        if corner not in valid_corners:
            raise ValueError(f"corner must be one of {valid_corners}, got '{corner}'")
        
        # Ensure image is in RGBA mode for transparency support
        if image.mode != 'RGBA':
            working_image = image.convert('RGBA')
        else:
            working_image = image.copy()
        
        # Calculate font size and padding based on image height if not provided
        original_img_height: int = working_image.height
        original_img_width: int = working_image.width
            
        if font_size is None:
            font_size = max(int(original_img_height * relative_font_size), 12)  # Minimum font size of 12
            if debug_print:
                print(f'Computing font size with relative_font_size: {relative_font_size}: font_size: {font_size}')
                
        if padding is None:
            padding = max(int(original_img_height * relative_padding), 4)  # Minimum padding of 4px
        
        # Try to load the specified font, fall back to default if not available
        try:
            font_obj = ImageHelpers.get_font(font, size=font_size, allow_caching=True)
        except (IOError, OSError):
            # Fall back to default font with specified size
            try:
                font_obj = ImageFont.load_default(size=font_size)
            except TypeError:
                default_font = ImageFont.load_default()
                try:
                    font_obj = ImageFont.truetype("DejaVuSans.ttf", font_size)
                except (IOError, OSError):
                    font_obj = default_font
                    if debug_print:
                        print(f"Warning: Could not load font '{font}' with size {font_size}. Using default font.")
        
        # Create a temporary drawing context to measure text dimensions
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Get text dimensions (handle both old and new PIL versions)
        try:
            # Newer PIL versions
            bbox = temp_draw.textbbox((0, 0), label_text, font=font_obj)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Older PIL versions
            text_width, text_height = temp_draw.textsize(label_text, font=font_obj)
        
        # Calculate background rectangle dimensions
        bg_width = text_width + (padding * 2)
        bg_height = text_height + (padding * 2)
        
        # Create background rectangle image
        bg_image = Image.new('RGBA', (bg_width, bg_height), background_color)
        
        # Create text image with transparent background
        text_image = Image.new('RGBA', (bg_width, bg_height), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_image)
        
        # Calculate text position (centered in the background)
        text_x = padding
        text_y = padding
        
        # Draw text with outline if specified
        if text_outline_shadow_color is not None:
            # Calculate border thickness based on font size
            border_thickness = max(1, int(font_size * 0.08))  # 8% of font size, minimum 1px
            
            # Draw text outline/shadow
            for dx in range(-border_thickness, border_thickness + 1):
                for dy in range(-border_thickness, border_thickness + 1):
                    if dx != 0 or dy != 0:  # Skip the center position
                        text_draw.text((text_x + dx, text_y + dy), label_text, fill=text_outline_shadow_color, font=font_obj, **text_kwargs)
        
        # Draw the main text
        text_draw.text((text_x, text_y), label_text, fill=text_color, font=font_obj, **text_kwargs)
        
        # ## inverse transform the text image so that when the parent image gets stretched, the text doesn't look stretched. #TODO 2025-08-13 14:35: - [ ] Currently does not work
        # if inverse_scale_factor is not None:
        #     assert len(inverse_scale_factor) == 2, f"inverse_scale_factor should be a tuple (width_scale_factor, height_scale_factor) but is instead inverse_scale_factor: {inverse_scale_factor}"
        #     rescale_size = ((bg_width * int(inverse_scale_factor[0])), (bg_height * int(inverse_scale_factor[1])))
        #     text_image = text_image.resize(size=rescale_size) ## scale image down by 1/4 in width but leave the original height
            
        # Composite text onto background
        overlay_image = Image.alpha_composite(bg_image, text_image)
        
        # Calculate position based on corner
        if corner == 'top-left':
            pos_x = 0
            pos_y = 0
        elif corner == 'top-right':
            pos_x = original_img_width - bg_width
            pos_y = 0
        elif corner == 'bottom-left':
            pos_x = 0
            pos_y = original_img_height - bg_height
        elif corner == 'bottom-right':
            pos_x = original_img_width - bg_width
            pos_y = original_img_height - bg_height
        
        # Ensure position is within image bounds
        pos_x = max(0, min(pos_x, original_img_width - bg_width))
        pos_y = max(0, min(pos_y, original_img_height - bg_height))
        
        # Create final image by compositing the overlay onto the working image
        result_image = working_image.copy()
        # result_image.paste(overlay_image, (pos_x, pos_y), overlay_image)
        # result_image = Image.alpha_composite(working_image.copy(), overlay_image) # Composite text onto background
        position = (pos_x, pos_y)
        result_image.alpha_composite(overlay_image, dest=position)
    

        if debug_print:
            print(f'Added overlay label "{label_text}" at {corner} (x={pos_x}, y={pos_y})')
            print(f'Text dimensions: {text_width}x{text_height}, Background: {bg_width}x{bg_height}')
            
        return result_image


    def add_half_width_rectangle(image: Image.Image, side: str = 'left', 
                                color: tuple = (200, 200, 255, 255), background_color: tuple = (255, 255, 255, 255),
                                height_fraction: float = 0.1) -> Image.Image:
        """Adds a rectangle that fills half the width of the image.
        
        Parameters:
        -----------
        image : Image.Image
            The PIL Image to add the rectangle to
        side : str, optional
            Which side to place the rectangle, either 'left' or 'right', by default 'left'
        color : tuple, optional
            RGBA color for the rectangle, by default (200, 200, 255, 255) (light blue)
        vertical_position : str, optional
            Where to place the rectangle vertically, either 'top', 'middle', 'bottom', or 'full',
            by default 'bottom'
        height_fraction : float, optional
            What fraction of the image height the rectangle should occupy (when not 'full'),
            by default 0.1 (10% of image height)
            
        Returns:
        --------
        Image.Image
            A new image with the rectangle added
            
        Usage:
        ------
        from pyphocorehelpers.plotting.media_output_helpers import add_half_width_rectangle
        
        # Add a blue rectangle to the left half of the bottom of the image
        modified_image = add_half_width_rectangle(
            original_image, 
            side='left',
            color=(100, 100, 255, 200),  # Semi-transparent blue
            vertical_position='bottom',
            height_fraction=0.15  # 15% of image height
        )
        
        # Add a red rectangle covering the entire right half
        modified_image = add_half_width_rectangle(
            original_image, 
            side='right',
            color=(255, 100, 100, 255),  # Red
            vertical_position='full'
        )
        """
        # Validate parameters
        if side not in ['left', 'right']:
            raise ValueError("side must be either 'left' or 'right'")
        
        # Create a new image with space for the rectangle
        new_width = image.width

        # Get image dimensions
        width, height = image.size
        half_width = width // 2
        rect_height = int(height * height_fraction)
        new_height = image.height + rect_height
        
        # Create the new image with the background color
        if image.mode == 'RGBA':
            new_image = Image.new('RGBA', (new_width, new_height), background_color)
        else:
            # Convert background_color to RGB if the image is not RGBA
            new_image = Image.new(image.mode, (new_width, new_height), background_color[:3])
        
        # Paste the original image at the top
        new_image.paste(image, (0, 0))
        
        # Create a drawing context
        draw = ImageDraw.Draw(new_image)
        
        # Calculate rectangle coordinates
        half_width = new_width // 2
        rect_top = image.height
        rect_bottom = new_height
        
        # Draw the rectangle on the specified half
        if side == 'left':
            draw.rectangle([(0, rect_top), (half_width, rect_bottom)], fill=color)
        else:  # right
            draw.rectangle([(half_width, rect_top), (new_width, rect_bottom)], fill=color)
        
        return new_image


    def add_solid_border(image: Image.Image, border_width: int = 5,  border_color: tuple = (0, 0, 0, 255)) -> Image.Image:
        """Adds a solid border around an image by extending it on all sides.
        
        Parameters:
        -----------
        image : Image.Image
            The PIL Image to add a border to
        border_width : int, optional
            Width of the border in pixels, by default 5
        border_color : tuple, optional
            RGBA color for the border, by default (0, 0, 0, 255) (solid black)
            
        Returns:
        --------
        Image.Image
            A new image with the border added around the original image
            
        Usage:
        ------
        from pyphocorehelpers.plotting.media_output_helpers import add_solid_border
        
        # Add a 10-pixel red border around the image
        bordered_image = add_solid_border(
            original_image, 
            border_width=10,
            border_color=(255, 0, 0, 255)  # Red
        )
        
        # Add a default 5-pixel black border
        bordered_image = add_solid_border(original_image)
        """
        # Get original image dimensions
        original_width, original_height = image.size
        
        # Calculate new dimensions
        new_width = original_width + (2 * border_width)
        new_height = original_height + (2 * border_width)
        
        # Create a new image with the border color
        if image.mode == 'RGBA':
            new_image = Image.new('RGBA', (new_width, new_height), border_color)
        else:
            # Convert border_color to RGB if the image is not RGBA
            new_image = Image.new(image.mode, (new_width, new_height), border_color[:3])
        
        # Paste the original image in the center
        new_image.paste(image, (border_width, border_width))
        
        return new_image



@metadata_attributes(short_name=None, tags=['function'], input_requires=[], output_provides=[], uses=['ImageOperationsAndEffects'], used_by=[], creation_date='2025-05-30 04:49', related_items=['ImageOperationsAndEffects'])
class ImagePostRenderFunctionSets:
    """ Provides SETS of operations to be performed on IMAGES, specifically for a particular export type (greyscale heatmaps for individual 1D decoders like 'long_LR' vs. RAW_RGBA (pseudo2D)

    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import ImagePostRenderFunctionSets, ImageOperationsAndEffects

        'raw_rgba': HeatmapExportConfig.init_for_export_kind(export_kind=HeatmapExportKind.RAW_RGBA, 
                                                            raw_RGBA_only_parameters = dict(spikes_df=deepcopy(get_proper_global_spikes_df(owning_pipeline_reference)), xbin=deepcopy(a_decoder.xbin), lower_bound_alpha=0.1, drop_below_threshold=1e-3, t_bin_size=time_bin_size, use_four_decoders_version=False), desired_height=desired_height, 
                                                            post_render_image_functions_builder_fn=ImagePostRenderFunctionSets._build_mergedColorDecoders_image_export_functions_dict),

    """
    # prepare_for_publication: bool = False
    prepare_for_publication: bool = True

    @function_attributes(short_name=None, tags=['publication', 'light-mode', 'export'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-09-03 08:31', related_items=[])
    @classmethod
    def _get_export_color_scheme_kwargs(cls, is_prepare_for_publication: bool=True):
        """ Added 2025-09-03 to make Figure 4 Example Posterior exports better
        """
        fixed_label_region_height: Optional[int] = 520
        # font_size = 144
        # font_size = 96
        # font_size = 72
        font_size = 48

        _common_kwargs = dict(fixed_label_region_height=fixed_label_region_height, font_size=font_size)
        
        if not is_prepare_for_publication:
            return _common_kwargs | dict(text_color=(255, 255, 255), background_color=(66, 66, 66)) # light color fg on dark bg
        else:
            ## publication mode
            return _common_kwargs | dict(text_color=(0, 0, 0), background_color=(236,236,236)) # dark color fg on light bg
        


    @classmethod
    def _build_no_op_image_export_functions_dict(cls, a_decoder_decoded_epochs_result: DecodedFilterEpochsResult) -> List[Dict[str, Callable]]:
        """ empty/no-op 
        post_render_image_functions_dict_list: List[Dict[str, Callable]] = _build_image_export_functions_dict(a_decoder_decoded_epochs_result=a_decoder_decoded_epochs_result)

        """
        num_filter_epochs: int = a_decoder_decoded_epochs_result.num_filter_epochs
        # Build post-image-generation callback functions _____________________________________________________________________________________________________________________________________________________________________________________________________________________________________ #
        post_render_image_functions_dict_list: List = [dict() for i in np.arange(num_filter_epochs)] ## empty dict
        return post_render_image_functions_dict_list


    @classmethod
    def _build_mergedColorDecoders_image_export_functions_dict(cls, a_decoder_decoded_epochs_result: DecodedFilterEpochsResult) -> List[Dict[str, Callable]]:
        """ 
        post_render_image_functions_dict_list: List[Dict[str, Callable]] = _build_image_export_functions_dict(a_decoder_decoded_epochs_result=a_decoder_decoded_epochs_result)

        """
        from neuropy.core.epoch import ensure_dataframe
        from pyphocorehelpers.assertion_helpers import Assert

        num_filter_epochs: int = a_decoder_decoded_epochs_result.num_filter_epochs
        active_filter_epochs: pd.DataFrame = ensure_dataframe(a_decoder_decoded_epochs_result.active_filter_epochs)

        Assert.require_columns(active_filter_epochs, required_columns=['maze_id'])
        is_epoch_pre_post_delta = active_filter_epochs['maze_id'].to_numpy()

        # Build post-image-generation callback functions _____________________________________________________________________________________________________________________________________________________________________________________________________________________________________ #

        _label_kwargs = cls._get_export_color_scheme_kwargs(is_prepare_for_publication=cls.prepare_for_publication)

        create_label_function = ImageOperationsAndEffects.create_fn_builder(ImageOperationsAndEffects.add_bottom_label, **_label_kwargs) #  text_color=(255, 255, 255), background_color=(66, 66, 66), font_size=font_size, fixed_label_region_height=fixed_label_region_height
        # create_half_width_rectangle_function = ImageOperationsAndEffects.create_fn_builder(ImageOperationsAndEffects.add_half_width_rectangle, height_fraction = 0.1)    
        create_solid_border_function = ImageOperationsAndEffects.create_fn_builder(ImageOperationsAndEffects.add_solid_border) # border_color = (0, 0, 0, 255)

        post_render_image_functions_dict_list: List = []

        for i in np.arange(num_filter_epochs):
            active_captured_single_epoch_result: SingleEpochDecodedResult = a_decoder_decoded_epochs_result.get_result_for_epoch(active_epoch_idx=i)

            # Prepare a multi-line, sideways label _______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________ #
            complete_epoch_identifier_str = ''

            ## mode to use
            curr_epoch_info_dict = active_captured_single_epoch_result.epoch_info_tuple._asdict()
            active_epoch_id: int = curr_epoch_info_dict.get('label', None)
            if active_epoch_id is not None:
                active_epoch_id = int(active_epoch_id)
                # complete_epoch_identifier_str = f"{complete_epoch_identifier_str}lbl[{active_epoch_id:03d}]" # 2025-06-03 - 'p_x_given_n[067]'
                complete_epoch_identifier_str = f"{complete_epoch_identifier_str}L{active_epoch_id:03d}"
            else:
                print(f'falling back to plain epoch IDXs because label was not found!')
                active_epoch_data_IDX: int = active_captured_single_epoch_result.epoch_data_index
                if active_epoch_data_IDX is not None:
                    complete_epoch_identifier_str = f'{complete_epoch_identifier_str}IDX{active_epoch_data_IDX:03d}'

            ## OUTPUTS: complete_epoch_identifier_str
            is_post_delta: bool = (is_epoch_pre_post_delta[i] > 0)

            ## get pre/post delta label:
            earliest_t = active_captured_single_epoch_result.time_bin_edges[0]
            # earliest_t_ms = earliest_t * 1e-3
            earliest_t_str: str = "{:08.4f}".format(earliest_t)
            # earliest_t_str: str = f"{earliest_t:.4f}"

            # Create an image with a label
            # labeled_image = add_bottom_label(original_image, "Time (seconds)", font_size=14)
            # curr_x_axis_label_str: str = f'{earliest_t}'
            # if not is_post_delta:
            #      curr_x_axis_label_str = f'{curr_x_axis_label_str} (pre-delta)'
            # else:
            #     curr_x_axis_label_str = f'{curr_x_axis_label_str} (post-delta)'

            curr_x_axis_label_str: str = f''
            if not is_post_delta:
                #  curr_x_axis_label_str = f'PRE'
                    side = 'left'
                    epoch_rect_color = '#4169E1'

            else:
                # curr_x_axis_label_str = f'POST'
                side = 'right'
                epoch_rect_color = '#DC143C'

            # curr_x_axis_label_str = f"{curr_x_axis_label_str}[{i}]"
            # curr_x_axis_label_str = f"{curr_x_axis_label_str}\n{earliest_t_str}"


            if len(complete_epoch_identifier_str) > 0:
                curr_x_axis_label_str = f"{complete_epoch_identifier_str}: {earliest_t_str}" ## add separator if needed for time
            else:
                curr_x_axis_label_str = f"{earliest_t_str}" # // 2025-06-03 09:10 working

            # curr_post_render_image_functions_dict = {'add_bottom_label': (lambda an_img: add_bottom_label(an_img, curr_x_axis_label_str, font_size=8))}
            curr_post_render_image_functions_dict = {
                # 'add_bottom_label': create_label_function(curr_x_axis_label_str, font_size=font_size, text_color=(255, 255, 255), background_color=(66, 66, 66), text_outline_shadow_color=None, fixed_label_region_height=fixed_label_region_height, debug_print=False),
                'add_bottom_label': create_label_function(curr_x_axis_label_str, **(_label_kwargs | dict(text_color=epoch_rect_color)), text_outline_shadow_color=None, debug_print=False), # , fixed_label_region_height=fixed_label_region_height, font_size=font_size
                # 'create_solid_border_function': create_solid_border_function(border_width = 10, border_color = epoch_rect_color),
                # 'create_half_width_rectangle_function': create_half_width_rectangle_function(side, epoch_rect_color), ## create rect to indicate pre/post delta
                # 'create_half_width_rectangle_function': create_half_width_rectangle_function(side, epoch_rect_color),
            }
            post_render_image_functions_dict_list.append(curr_post_render_image_functions_dict)                        
        # END for i in np.arange(num_filter_epochs)


        return post_render_image_functions_dict_list



    
def get_array_as_image(img_data: NDArray[ND.Shape["IM_HEIGHT, IM_WIDTH, 4"], np.floating], desired_width: Optional[int] = None, desired_height: Optional[int] = None, export_kind: Optional[HeatmapExportKind] = None,
                        colormap='viridis', skip_img_normalization:bool=False, export_grayscale:bool=False,
                        include_value_labels: bool = False, allow_override_aspect_ratio:bool=False, flip_vertical_axis: bool = False, debug_print=False, **kwargs) -> Image.Image:
    """ Like `save_array_as_image` except it skips the saving to disk. Converts a numpy array to file as a colormapped image
    
    # Usage:
    
        from pyphocorehelpers.plotting.media_output_helpers import get_array_as_image
    
        image = get_array_as_image(img_data, desired_height=100, desired_width=None, skip_img_normalization=True)
        image
        
    # Usage 2:
    
        img_data = np.transpose(img_data, axes=(1, 0, 2)) # Convert to (H, W, 4)
        kwargs = {}
        desired_height = 400
        desired_width = None
        skip_img_normalization = True
        _out_img = get_array_as_image(img_data, desired_height=desired_height, desired_width=desired_width, skip_img_normalization=skip_img_normalization, export_kind=HeatmapExportKind.RAW_RGBA, **kwargs)
        _out_img

                
    """
    from pyphoplacecellanalysis.Pho2D.data_exporting import HeatmapExportKind

    if export_kind is None:
        if export_grayscale:
            export_kind = HeatmapExportKind.GREYSCALE
        else:
            export_kind = HeatmapExportKind.COLORMAPPED
    else:
        if debug_print:
            print(f'export_kind: {export_kind} explicitly provided, so ignoring export_grayscale: {export_grayscale}')



    if np.ndim(img_data) < 2:
        img_data = np.atleast_2d(img_data).T # (50, ) -> (50, 1)



    # Assuming `your_array` is your numpy array
    if export_kind.value == HeatmapExportKind.GREYSCALE.value:
    # if export_grayscale:
        # Convert to grayscale (normalize if needed)
        assert (colormap is None) or (colormap == 'viridis'), f"colormap should not be specified when export_grayscale=True" # (default 'viridis' is safely ignored)
        
        if skip_img_normalization:
            print(f'WARN: when `export_grayscale == True`, `skip_img_normalization == True` makes no sense and will be ignored.')
            
        alpha = (~np.isnan(img_data)).astype(np.uint8) * 255
        norm_array = img_data_to_greyscale(img_data, min_val = kwargs.pop('vmin', None), max_val = kwargs.pop('vmax', None), should_invert=True)
        # Scale to 0-255 and convert to uint8
        # image = Image.fromarray(norm_array, mode='L') # .shape: (59, 4, 67)
        
        ### have to build `mode='LA'` (mode='LA' → Grayscale + Alpha) image out of norm_array to represent transparency
        norm_array = np.nan_to_num(norm_array, nan=0).astype(np.uint8)
        image = Image.fromarray(np.dstack((norm_array, alpha)), mode='LA')


        # ## Fill np.nan with a color instead -  have to build RGBA image out of norm_array to represent transparency
        # nan_fill_color = (155, 0, 0, 155)  # Red, fully opaque
        # nan_mask = np.isnan(norm_array)
        # norm_array = np.nan_to_num(norm_array, nan=0).astype(np.uint8)
        # rgba = np.dstack((norm_array, norm_array, norm_array, np.full_like(norm_array, 255)))
        # rgba[nan_mask] = nan_fill_color  # replace NaNs with chosen RGBA color
        # image = Image.fromarray(rgba, mode='RGBA')



    elif export_kind.value == HeatmapExportKind.COLORMAPPED.value:
        ## Color export mode!
        assert (colormap is not None)
        # Get the specified colormap
        colormap = plt.get_cmap(colormap)
        
        alpha = (~np.isnan(img_data)).astype(np.uint8) * 255

        if skip_img_normalization:
            norm_array = img_data
        else:
            # Normalize your array to 0-1 using nan-aware functions
            min_val = kwargs.pop('vmin', None)
            if min_val is None:
                min_val = np.nanmin(img_data)
                
            max_val = kwargs.pop('vmax', None)
            if max_val is None:
                max_val = np.nanmax(img_data)

            assert (min_val < max_val), f"min_val: {min_val}, min_val: {min_val}, img_data: {img_data}"
            ptp_val = max_val - min_val
            norm_array = (img_data - min_val) / ptp_val

        # Apply colormap
        image_array = colormap(norm_array)

        # Convert to PIL image and remove alpha channel
        # image = Image.fromarray((image_array[:, :, :3] * 255).astype(np.uint8)) # TypeError: Cannot handle this data type: (1, 1, 3, 4), |u1  || 2025-06-04 Failing for 1D input arrts which end up as (1D, 4): IndexError: too many indices for array: array is 2-dimensional, but 3 were indexed
        
        ## Fill np.nan with a color instead -  have to build RGBA image out of norm_array to represent transparency
        # nan_fill_color = (155, 0, 0, 155)  # Red, fully opaque
        # nan_mask = np.isnan(norm_array)
        # norm_array = np.nan_to_num(norm_array, nan=0).astype(np.uint8)
        # rgba = np.dstack(((image_array[:, :, :3] * 255).astype(np.uint8), np.full_like(norm_array, 255)))
        # rgba[nan_mask] = nan_fill_color  # replace NaNs with chosen RGBA color
        rgba = np.dstack(((image_array[:, :, :3] * 255).astype(np.uint8), alpha))
        image = Image.fromarray(rgba, mode='RGBA')


    elif export_kind.value == HeatmapExportKind.RAW_RGBA.value:
        ## Raw ready to use RGBA image is passed in:
        # Convert to PIL image and remove alpha channel
        image = Image.fromarray((img_data * 255).astype(np.uint8)) # TypeError: Cannot handle this data type: (1, 1, 3, 4), |u1
        assert skip_img_normalization == True, f"it does not make sense to re-normalize the RGBA image"
        norm_array = img_data
        

    else:
        raise NotImplementedError(f"export_kind: {export_kind}")    
    
    ## OUTPUT: image: Image

    # Optionally flip the image vertically
    if flip_vertical_axis:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        
    if ((desired_width is None) and (desired_height is None)):
        desired_width = 1024 # set a default arbitrarily

    if desired_width is not None:
        # Specify width
        assert ((desired_height is None) or allow_override_aspect_ratio), f"please don't provide both width and height, the other will be calculated automatically. If you meant to force this set `allow_override_aspect_ratio=True` to override."
        if (desired_height is None):
            # Calculate height to preserve aspect ratio
            desired_height = int(desired_width * norm_array.shape[0] / norm_array.shape[1])
        
    elif (desired_height is not None):
        # Specify height:
        assert ((desired_width is None) or allow_override_aspect_ratio), f"please don't provide both width and height, the other will be calculated automatically. If you meant to force this set `allow_override_aspect_ratio=True` to override."
        if (desired_width is None):
            # Calculate width to preserve aspect ratio
            desired_width = int(desired_height * norm_array.shape[1] / norm_array.shape[0])
    else:
        raise ValueError("you must specify width or height of the output image")

    # Resize image
    # image = image.resize((new_width, new_height), Image.LANCZOS)
    image = image.resize((int(desired_width), int(desired_height)), Image.NEAREST)

    if include_value_labels:
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        def draw_text_with_border(draw, x, y, text, font, fill):
            # Draw shadow/border (using black color)
            shadow_color = (0, 0, 0)
            draw.text((x - 1, y - 1), text, font=font, fill=shadow_color)
            draw.text((x + 1, y - 1), text, font=font, fill=shadow_color)
            draw.text((x - 1, y + 1), text, font=font, fill=shadow_color)
            draw.text((x + 1, y + 1), text, font=font, fill=shadow_color)
            # Draw text itself
            draw.text((x, y), text, font=font, fill=fill)

        # Iterate over pixels and annotate with their values
        for y in range(norm_array.shape[0]):
            for x in range(norm_array.shape[1]):
                value = norm_array[y, x]
                text = f'{value:.2f}'
                # text = "{:07.2f}".format(value) # f'{value:.2f}'
                text_x = x * desired_width // norm_array.shape[1]
                text_y = y * desired_height // norm_array.shape[0]

                # Draw the text with border
                draw_text_with_border(draw, text_x, text_y, text, font, fill=(255, 255, 255))

                # Rotate the text by 45 degrees (angle)
                text_image = Image.new('RGBA', (image.size[0], image.size[1]), (255, 255, 255, 0))
                text_draw = ImageDraw.Draw(text_image)
                draw_text_with_border(text_draw, text_x, text_y, text, font, fill=(255, 255, 255))
                # text_image = text_image.rotate(45, expand=1)
                image.paste(text_image, (0, 0), text_image)


    # ==================================================================================================================================================================================================================================================================================== #
    # Call the post-render functions, which do things like: Add bottom time label, adding colored border, etc                                                                                                                                                                                                                                                                #
    # ==================================================================================================================================================================================================================================================================================== #    
    post_render_image_functions = kwargs.pop('post_render_image_functions', {})
    for a_render_fn_name, a_render_fn in post_render_image_functions.items():
        if debug_print:
            print(f'\tperforming: {a_render_fn_name}')
        image = a_render_fn(image)

    return image


def save_array_as_image(img_data, desired_width: Optional[int] = 1024, desired_height: Optional[int] = None, export_kind: Optional[HeatmapExportKind] = None, out_path='output/numpy_array_as_image.png', colormap:str='viridis', skip_img_normalization:bool=False, export_grayscale:bool=False, include_value_labels: bool = False, allow_override_aspect_ratio:bool=False, flip_vertical_axis: bool = False, **kwargs) -> Tuple[Image.Image, Path]:
    """ Exports a numpy array to file as a colormapped image
    
    # Usage:
    
        from pyphocorehelpers.plotting.media_output_helpers import save_array_as_image
    
        image, out_path = save_array_as_image(img_data, desired_height=100, desired_width=None, skip_img_normalization=True)
        image
        
        
                
    """
    image: Image.Image = get_array_as_image(img_data=img_data, desired_width=desired_width, desired_height=desired_height, export_kind=export_kind, colormap=colormap, skip_img_normalization=skip_img_normalization, export_grayscale=export_grayscale, include_value_labels=include_value_labels, allow_override_aspect_ratio=allow_override_aspect_ratio, flip_vertical_axis=flip_vertical_axis, **kwargs)
    out_path = Path(out_path).resolve()
    # Save image to file
    image.save(out_path)

    return image, out_path


def get_array_as_image_stack(imgs: List[Image.Image], offset=10, single_image_alpha_level:float=0.5,
                            #   border_size: Optional[int] = 5, shadow_offset: Optional[int] = 10,
                              should_add_border: bool = False, border_size: int = 5, border_color: Tuple[int, int, int] = (0, 0, 0),
                              should_add_shadow: bool = False, shadow_offset: int = 10, shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
                              ) -> Image.Image:
   
    """ Handles 3D images
    Given a list of equally sized figures, how do I overlay them in a neat looking stack and produce an output graphic from that?
    I want them offset slightly from each other to make a visually appealing stack

    single_image_alpha_level = 0.5 - adjust this value to set the desired transparency level (0.0 to 1.0)
    offset = 10  # your desired offset

    2024-01-12 - works well

    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import get_array_as_image_stack, save_array_as_image_stack

        # Let's assume you have a list of images
        images = ['image1.png', 'image2.png', 'image3.png']  # replace this with actual paths to your images
        output_img, output_path = get_array_as_image_stack(out_figs_paths, offset=55, single_image_alpha_level=0.85)

    """
    # Make a general alpha adjustment to the images
    if (single_image_alpha_level is None) or (single_image_alpha_level == 1.0):
        # Open the images
        pass

    else:
        print(f'WARNING: transparency mode is very slow! This took ~50sec for ~30 images')
        # only do this if transparency of layers is needed, as this is very slow (~50sec)
        imgs = [img.convert("RGBA") for img in imgs] # convert to RGBA explicitly, seems to be very slow.
        for i in range(len(imgs)):
            for x in range(imgs[i].width):
                for y in range(imgs[i].height):
                    r, g, b, a = imgs[i].getpixel((x, y))
                    imgs[i].putpixel((x, y), (r, g, b, int(a * single_image_alpha_level)))

    # Assume all images are the same size
    width, height = imgs[0].size

    # Create a new image with size larger than original ones, considering offsets
    output_width = width + abs(offset) * (len(imgs) - 1)
    output_height = height + abs(offset) * (len(imgs) - 1)

    output_img = Image.new('RGBA', (output_width, output_height))

    should_add_border = (should_add_border and (border_size is not None) and (border_size > 0))
    should_add_shadow = (should_add_shadow and (shadow_offset is not None) and (shadow_offset > 0))
    # Overlay images with offset
    #    for i, img in enumerate(imgs):
    #       output_img.paste(img, (i * offset, i * offset), img)

    if should_add_border:
        width += 2 * border_size
        height += 2 * border_size

    if should_add_shadow:
        width += shadow_offset
        height += shadow_offset

    output_width = width + abs(offset) * (len(imgs) - 1)
    output_height = height + abs(offset) * (len(imgs) - 1)

    output_img = Image.new('RGBA', (output_width, output_height))

    for i, img in enumerate(imgs):
        if add_border:
            img = add_border(img, border_size=border_size, border_color=border_color)
        if add_shadow:
            img = add_shadow(img, offset=shadow_offset, shadow_color=shadow_color)
        output_img.paste(img, (i * offset, i * offset), img)

    return output_img


def compute_total_padding(padding: Union[str, float], num_images: int, dimension_size: float) -> float:
    """ 
    dimension_size: only used if padding is passed as a percent

    Usage:     
        output_width = np.sum(widths)
        output_total_padding_width: float = compute_total_padding(padding=padding, num_images=len(imgs), dimension_size=output_width)
    """
    if isinstance(padding, str) and padding.endswith('%'):
        # if it's a string like '1%', it specifies the desired width in terms of the total image width
        padding_percent = padding.strip('%')
        padding_percent = float(padding_percent)
        assert (padding <= 100.0) and (padding >= 0.0), f"padding: {padding} is invalid! Should be a percentage of the total image width like '1%'."
        padding = (padding_percent * dimension_size) / float(num_images - 1) # padding in px

    return (padding * (num_images - 1))



def vertical_image_stack(imgs: List[Image.Image], padding=10, v_overlap: int=0, separator_color=None) -> Image.Image:
    """ Builds a stack of images into a vertically concatenated image.
    offset = 10  # your desired offset

    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import vertical_image_stack, horizontal_image_stack

        # Open the images
        _raster_imgs = [Image.open(i) for i in _out_rasters_save_paths]
        _out_vstack = vertical_image_stack(_raster_imgs, padding=5)
        _out_vstack
        
    """
    # Ensure all images are in RGBA mode
    imgs = [img.convert('RGBA') if img.mode != 'RGBA' else img for img in imgs]
    
    widths = np.array([img.size[0] for img in imgs])
    heights = np.array([img.size[1] for img in imgs])

    # Create a new image with size larger than original ones, considering offsets
    # output_height = (np.sum(heights) + (padding * (len(imgs) - 1))) - v_overlap
    output_height = np.sum(heights) - v_overlap
    output_total_padding_height: float = compute_total_padding(padding=padding, num_images=len(imgs), dimension_size=output_height)

    output_height = output_height + output_total_padding_height
    output_width = np.max(widths)
    # print(f'output_width: {output_width}, output_height: {output_height}')
    output_img = Image.new('RGBA', (output_width, output_height))
    cum_height = 0
    for i, img in enumerate(imgs):
        curr_img_width, curr_img_height = img.size
        output_img.paste(img, (0, cum_height), img)
        # cum_height += (curr_img_height+padding) - v_overlap
        cum_height += curr_img_height - v_overlap ## add the current image height
        if (separator_color is not None) and (padding > 0):
            ## fill the between-image area with a separator_color
            _tmp_separator_img = Image.new('RGBA', (output_width, padding), separator_color)
            output_img.paste(_tmp_separator_img, (0, cum_height))
                    
        cum_height += padding

    return output_img


def horizontal_image_stack(imgs: List[Image.Image], padding=10, separator_color=None) -> Image.Image:
    """ Builds a stack of images into a horizontally concatenated image.
    offset = 10  # your desired offset

    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import vertical_image_stack, horizontal_image_stack

        # Open the images
        _raster_imgs = [Image.open(i) for i in _out_rasters_save_paths]
        # _out_vstack = vertical_image_stack(_raster_imgs, padding=5)
        # _out_vstack
        _out_hstack = horizontal_image_stack(_raster_imgs, padding=5)
        _out_hstack

    """
    # Ensure all images are in RGBA mode
    imgs = [img.convert('RGBA') if img.mode != 'RGBA' else img for img in imgs]
    
    ## get the sizes of each image
    widths = np.array([img.size[0] for img in imgs])
    heights = np.array([img.size[1] for img in imgs])

    # Create a new image with size larger than original ones, considering offsets
    output_width = np.sum(widths)
    output_total_padding_width: float = compute_total_padding(padding=padding, num_images=len(imgs), dimension_size=output_width)
    output_width = output_width + output_total_padding_width
    output_height = np.max(heights)
    
    # print(f'output_width: {output_width}, output_height: {output_height}')
    output_img = Image.new('RGBA', (output_width, output_height))
    cum_width = 0
    for i, img in enumerate(imgs):
        curr_img_width, curr_img_height = img.size
        output_img.paste(img, (cum_width, 0), img)
        # cum_height += curr_img_height
        cum_width += curr_img_width ## add the current image width
        if (separator_color is not None) and (padding > 0):
            ## fill the between-image area with a separator_color
            _tmp_separator_img = Image.new('RGBA', (padding, output_height), separator_color)
            output_img.paste(_tmp_separator_img, (cum_width, 0))
    
        cum_width += padding

    return output_img


def image_grid(imgs: List[List[Image.Image]], v_padding=None, h_padding=None, padding:Optional[float]=None, separator_color=None, v_overlap=0) -> Image.Image:
    """ Builds a stack of images into a horizontally concatenated image.
    offset = 10  # your desired offset

    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import vertical_image_stack, horizontal_image_stack, image_grid

        # Open the images
        _raster_imgs = [Image.open(i) for i in _out_rasters_save_paths]
        # _out_vstack = vertical_image_stack(_raster_imgs, padding=5)
        # _out_vstack
        _out_hstack = horizontal_image_stack(_raster_imgs, padding=5)
        _out_hstack

    """
    if padding is not None:
        ## same padding for both
        v_padding = padding
        h_padding = padding
    else:
        ## default to 5 pixels
        v_padding = 5
        h_padding = 5
    return vertical_image_stack(imgs=[horizontal_image_stack(imgs=a_row, padding=h_padding, separator_color=separator_color) for a_row in imgs], padding=v_padding, v_overlap=v_overlap, separator_color=separator_color)



# @function_attributes(short_name=None, tags=['image', 'stack', 'batch', 'file', 'stack'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-01-12 00:00', related_items=[])
def save_array_as_image_stack(images: List[Path], offset=10, single_image_alpha_level:float=0.5):
    """ 
    Given a list of equally sized figures, how do I overlay them in a neat looking stack and produce an output graphic from that?
    I want them offset slightly from each other to make a visually appealing stack


    single_image_alpha_level = 0.5 - adjust this value to set the desired transparency level (0.0 to 1.0)
    offset = 10  # your desired offset

    2024-01-12 - works well

    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import save_array_as_image_stack

        # Let's assume you have a list of images
        images = ['image1.png', 'image2.png', 'image3.png']  # replace this with actual paths to your images
        output_img, output_path = render_image_stack(out_figs_paths, offset=55, single_image_alpha_level=0.85)

    """
    # Open the images
    imgs = [Image.open(i) for i in images]

    output_img = get_array_as_image_stack(imgs, offset=offset, single_image_alpha_level=single_image_alpha_level)

    output_path: Path = Path('output/stacked_images.png').resolve()
    output_img.save(output_path)
    return output_img, output_path




#TODO 2023-09-27 19:54: - [ ] saving
@function_attributes(short_name=None, tags=['cv2'], input_requires=[], output_provides=[], uses=['cv2'], used_by=['PosteriorExporting.save_posterior_to_video'], creation_date='2024-09-06 11:34', related_items=[])
def save_array_as_video(array, video_filename='output/videos/long_short_rel_entr_curves_frames.mp4', fps=30.0, isColor=False, colormap=None, skip_img_normalization=False, debug_print=False, progress_print=True):
    """
    Save a 3D numpy array as a grayscale video.

    NOTE: .avi is MUCH faster than .mp4, by like 100x or more!
    
    Parameters:
    - array: numpy array of shape (timesteps, height, width)
    - output_filename: name of the output video file
    - fps: frames per second for the output video


    Usage:

        from pyphocorehelpers.plotting.media_output_helpers import save_array_as_video
        
        video_out_path = save_array_as_video(array=active_relative_entropy_results['snapshot_occupancy_weighted_tuning_maps'], video_filename='output/videos/snapshot_occupancy_weighted_tuning_maps.avi', isColor=False)
        print(f'video_out_path: {video_out_path}')
        reveal_in_system_file_manager(video_out_path)
    """
    import cv2
    if colormap is None:
        colormap = cv2.COLORMAP_VIRIDIS
    if skip_img_normalization:
        array = array
    else:
        # Normalize your array to 0-1
        array = (array - np.nanmin(array, axis=(1,2,), keepdims=True)) / np.ptp(array, axis=(1,2,), keepdims=True)
    
    gray_frames = cv2.normalize(array, None, 255, 0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U) # same size as array
    if debug_print:
        print(f'array.shape: {array.shape}')
        print(f'gray_frames.shape: {gray_frames.shape}')
    assert array.shape == gray_frames.shape, f"gray_frames should be the same size as the input array, just scaled to greyscale int8!"
    
    # Extract width and height from the array:
    n_frames = np.shape(array)[0]
    height = np.shape(array)[1]
    width = np.shape(array)[2]

    ## Check the path exists first:
    video_filepath: Path = Path(video_filename).resolve()
    video_parent_path = video_filepath.parent
    # assert video_parent_path
    if (not video_parent_path.exists()):
        print(f'target output directory (video_parent_path: "{video_parent_path}") does not exist. Creating it.')
        video_parent_path.mkdir(exist_ok=True)

    # initialize video writer
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    out = cv2.VideoWriter(str(video_filename), fourcc, fps, (width, height))

    # new frame after each addition of water
    progress_print_every_n_frames: int = 15 # print progress only once every 15 frames so it doesn't spam the output log
    for i in np.arange(n_frames):
        if progress_print and (i % 15 == 0):
            print(f'saving frame {i}/{n_frames}')
        gray = np.squeeze(gray_frames[i,:,:]) # single frame
        gray_3c = cv2.merge([gray, gray, gray])
        if isColor and (colormap is not None):
            # NEW: apply colormap if provided and isColor is True
            color_array = cv2.applyColorMap(gray_3c, colormap)
            out.write(color_array)
        else:
            out.write(gray_3c)

    # close out the video writer
    out.release()
    if progress_print:
        print(f'done! video saved to {video_filename}')
    return Path(video_filename).resolve()


@function_attributes(short_name=None, tags=['cv2'], input_requires=[], output_provides=[], uses=['cv2'], used_by=[], creation_date='2024-09-06 11:33', related_items=[])
def colormap_and_save_as_video(array, video_filename='output.avi', fps=30.0, colormap=None):
    import cv2
    if colormap is None:
        colormap = cv2.COLORMAP_VIRIDIS
    # array = ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8)
    # color_array = cv2.applyColorMap(array, colormap)
    return save_array_as_video(array, video_filename=video_filename, fps=fps, isColor=True, colormap=colormap)
    
""" 

# def normalize_and_save_as_video(array, output_filename='output.mp4', fps=30.0):
#     array = ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8)
#     return save_array_as_video(array, output_filename, fps)


# def colormap_and_save_as_video(array, output_filename='output.mp4', fps=30.0, colormap=cv2.COLORMAP_JET):
#     array = ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8)
#     color_array = cv2.applyColorMap(array, colormap)
#     return save_array_as_video(color_array, output_filename, fps, isColor=True)
    

# Example usage
# array = np.random.randint(0, 256, (4123, 90, 117), dtype=np.uint8)

# Save the `long_short_rel_entr_curves_frames` array out to the file:
# video_out_path = save_array_as_video(active_relative_entropy_results_xr_dict['long_short_rel_entr_curves_frames'].to_numpy(), output_filename='output/videos/long_short_rel_entr_curves_frames.mp4')


# array = active_relative_entropy_results_xr_dict['long_short_rel_entr_curves_frames'].to_numpy()
# video_out_path = normalize_and_save_as_video(array=array, output_filename='output/videos/long_short_rel_entr_curves_frames.mp4')

"""



@function_attributes(short_name=None, tags=['cv2'], input_requires=[], output_provides=[], uses=['cv2'], used_by=[], creation_date='2024-09-06 11:33', related_items=[])
def create_video_from_images(image_folder: str, output_video_file: str, seconds_per_frame: float, frame_size: tuple = None, codec: str = 'mp4v') -> Path:
    """ 
    Loads sequence of images from a folder and joins them into a video where each frame is a fixed duration (`seconds_per_frame`)
    
    # Usage:
        from pyphocorehelpers.plotting.media_output_helpers import create_video_from_images
        from pyphoplacecellanalysis.GUI.Napari.napari_helpers import napari_export_image_sequence
        ## Save images from napari to disk:
        desired_save_parent_path = Path('2024-08-08 - TransitionMatrix/PosteriorPredictions').resolve()
        imageseries_output_directory = napari_export_image_sequence(viewer=viewer, imageseries_output_directory=desired_save_parent_path, slider_axis_IDX=0)
        ## Build video from saved images:
        video_out_file = desired_save_parent_path.joinpath('output_video.mp4')
        create_video_from_images(image_folder=imageseries_output_directory, output_video_file=video_out_file, seconds_per_frame=0.2)

    """
    import cv2

    if not isinstance(image_folder, Path):
        image_folder = Path(image_folder).resolve()
    if not isinstance(output_video_file, Path):
        output_video_file = Path(output_video_file).resolve()
            

    images = sorted(glob(os.path.join(image_folder, '*.png')))  # Adjust the extension if necessary
    if not images:
        raise ValueError("No images found in the specified folder.")
    
    first_image = cv2.imread(images[0])
    height, width, _ = first_image.shape
    frame_size = frame_size or (width, height)

    fourcc = cv2.VideoWriter_fourcc(*codec)
    fps = 1 / seconds_per_frame
    video_writer = cv2.VideoWriter(output_video_file.resolve().as_posix(), fourcc, fps, frame_size)
    
    for image_file in images:
        img = cv2.imread(image_file)
        if img.shape[1] != frame_size[0] or img.shape[0] != frame_size[1]:
            img = cv2.resize(img, frame_size)
        video_writer.write(img)
    
    video_writer.release()
    return output_video_file


def create_gif_from_images(image_folder: str, output_video_file: str, seconds_per_frame: float) -> Path:
    """ 
    Loads sequence of images from a folder and joins them into an animated GIF where each frame is a fixed duration (`seconds_per_frame`)
    
    # Usage:
        from pyphocorehelpers.plotting.media_output_helpers import create_gif_from_images
        from pyphoplacecellanalysis.GUI.Napari.napari_helpers import napari_export_image_sequence
        ## Save images from napari to disk:
        desired_save_parent_path = Path('2024-08-08 - TransitionMatrix/PosteriorPredictions').resolve()
        imageseries_output_directory = napari_export_image_sequence(viewer=viewer, imageseries_output_directory=desired_save_parent_path, slider_axis_IDX=0)
        ## Build animated .gif from saved images:
        gif_out_file = desired_save_parent_path.joinpath('output_video.gif')
        create_gif_from_images(image_folder=imageseries_output_directory, output_video_file=gif_out_file, seconds_per_frame=0.2)

    """
    from PIL import Image # create_gif_from_images
    
    if not isinstance(image_folder, Path):
        image_folder = Path(image_folder).resolve()
    if not isinstance(output_video_file, Path):
        output_video_file = Path(output_video_file).resolve()
        
    images = sorted(glob(os.path.join(image_folder, '*.png')))  # Adjust the extension if necessary
    if not images:
        raise ValueError("No images found in the specified folder.")
    
    frames = [Image.open(image) for image in images]
    duration = int(seconds_per_frame * 1000)  # Convert seconds to milliseconds
    
    frames[0].save(output_video_file, format='GIF', append_images=frames[1:], save_all=True, duration=duration, loop=0)
    return output_video_file





# plotly.graph_objs._figure.Figure

# @function_attributes(short_name=None, tags=['clipboard', 'image', 'figure', 'export', 'matplotlib', 'plotly'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-03-05 13:59', related_items=[])
def fig_to_clipboard(a_fig: Union[PlotlyFigure, FigureBase], format="png", **kwargs):
    """ Any common figure type (matplotlib, Plotly, etc) to clipboard as image  _______________________________________________________________________________________________  
    
    from pyphocorehelpers.plotting.media_output_helpers import fig_to_clipboard
    
    fig_to_clipboard(fig)

    """
    from pyphocorehelpers.programming_helpers import copy_image_to_clipboard
    
    _fig_save_fn = None
    if isinstance(a_fig, FigureBase):
        # Matplotlib Figure:
        _fig_save_fn = a_fig.savefig
        if format == 'png':
            kwargs.setdefault('bbox_inches', 'tight') # crops off the empty white margins

    elif isinstance(a_fig, PlotlyFigure):
        # Plotly Figure:
        _fig_save_fn = a_fig.write_image
    else:
        raise NotImplementedError(f"type(a_fig): {type(a_fig)}, a_fig: {a_fig}")
    ## Perform the image generation to clipboard:
    with io.BytesIO() as buf:
        _fig_save_fn(buf, format=format, **kwargs)
        buf.seek(0)
        img = Image.open(buf)
        # Send the image to the clipboard
        copy_image_to_clipboard(img)
        # Close the buffer and figure to free resources
        buf.close()
            

def figure_to_pil_image(a_fig: Union[PlotlyFigure, FigureBase], format="png", **kwargs) -> Optional[Image.Image]:
    """ Convert a Matplotlib Figure to a PIL Image.

    Parameters:
        fig (matplotlib.figure.Figure): The Matplotlib figure to convert.

    Returns:
        PIL.Image.Image: The resulting PIL Image.
        
    Usage:
        from pyphocorehelpers.plotting.media_output_helpers import figure_to_pil_image
    
        fig_img = figure_to_pil_image(a_fig=fig)
    """
    _fig_save_fn = None
    img = None
    if isinstance(a_fig, FigureBase):
        # Matplotlib Figure:
        _fig_save_fn = a_fig.savefig
        if format == 'png':
            kwargs.setdefault('bbox_inches', 'tight') # crops off the empty white margins

    elif isinstance(a_fig, PlotlyFigure):
        # Plotly Figure:
        _fig_save_fn = a_fig.write_image
    else:
        raise NotImplementedError(f"type(a_fig): {type(a_fig)}, a_fig: {a_fig}")
    
    ## Perform the image generation to clipboard:
    with io.BytesIO() as buf:
        _fig_save_fn(buf, format=format, **kwargs)
        buf.seek(0)
        img = Image.open(buf)
        # Optionally, convert the image to RGB (if not already in that mode)
        if img.mode != 'RGB':
            img = img.convert('RGB')    
        # Close the buffer and figure to free resources
        buf.close()
    
    return img






@function_attributes(short_name=None, tags=['colormap', 'grayscale', 'image'], input_requires=[], output_provides=[], uses=[], used_by=['blend_images'], creation_date='2024-08-21 00:00', related_items=[])
def apply_colormap(image: np.ndarray, color: tuple) -> np.ndarray:
    colored_image = np.zeros((*image.shape, 3), dtype=np.float32)
    for i in range(3):
        colored_image[..., i] = image * color[i]
    return colored_image

@function_attributes(short_name=None, tags=['image'], input_requires=[], output_provides=[], uses=['apply_colormap'], used_by=[], creation_date='2024-08-21 00:00', related_items=[])
def blend_images(images: list, cmap=None) -> np.ndarray:
    """ Tries to pre-combine images to produce an output image of the same size

    # 'coolwarm'
    images = [a_seq_mat.todense().T for i, a_seq_mat in enumerate(sequence_frames_sparse)]
    blended_image = blend_images(images)
    # blended_image = blend_images(images, cmap='coolwarm')
    blended_image

    # blended_image = Image.fromarray(blended_image, mode="RGB")
    # # blended_image = get_array_as_image(blended_image, desired_height=100, desired_width=None, skip_img_normalization=True)
    # blended_image

    """
    from matplotlib.colors import Normalize
    
    if cmap is None:
        # Non-colormap mode:
        # Ensure images are in the same shape
        combined_image = np.zeros_like(images[0], dtype=np.float32)

        for img in images:
            combined_image += img.astype(np.float32)

    else:
        # colormap mode
        # Define a colormap (blue to red)
        cmap = plt.get_cmap(cmap)
        norm = Normalize(vmin=0, vmax=(len(images) - 1))

        combined_image = np.zeros((*images[0].shape, 3), dtype=np.float32)

        for i, img in enumerate(images):
            color = cmap(norm(i))[:3]  # Get RGB color from colormap
            colored_image = apply_colormap(img, color)
            combined_image += colored_image

    combined_image = np.clip(combined_image, 0, 255)  # Ensure pixel values are within valid range
    return combined_image.astype(np.uint8)



from pathlib import Path


try:
    from pypdf import PdfReader, PdfWriter, Transformation ## for PDFHelpers
    _PDFHELPERS_AVAILABLE = True

    @metadata_attributes(short_name=None, tags=['PDF', 'export', 'filesystem', 'concatenate', 'combine'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-06-19 11:48', related_items=[])
    class PDFHelpers:
        """ Helpers for Concatenating single-figure PDFs and other things
        
        from pyphocorehelpers.plotting.media_output_helpers import PDFHelpers
        
        """

        @classmethod
        def concatenate_pdfs_horizontally(cls, pdf_paths: List[Union[str, Path]], output_path: Union[str, Path], padding: float = 0):
            """
            Horizontally concatenate multiple single-page PDFs.

            Parameters:
            -----------
            pdf_paths : List[Union[str, Path]]
                List of paths to PDF files to concatenate horizontally
            output_path : Union[str, Path]
                Path for the output concatenated PDF
            padding : float, optional
                Spacing between PDFs in points, by default 0

            Returns:
            --------
            Path
                Path to the created concatenated PDF

            Usage:
            ------
            from pyphocorehelpers.plotting.media_output_helpers import PDFHelpers

            # Concatenate multiple PDFs horizontally
            pdf_files = [pdf1_path, pdf2_path, pdf3_path]
            output_file = PDFHelpers.concatenate_pdfs_horizontally(
                pdf_paths=pdf_files,
                output_path="combined_output.pdf",
                padding=10
            )

            # Concatenate just two PDFs (backwards compatible)
            output_file = PDFHelpers.concatenate_pdfs_horizontally(
                pdf_paths=[left_pdf_path, right_pdf_path],
                output_path="combined_output.pdf"
            )
            """
            if not pdf_paths:
                raise ValueError("pdf_paths cannot be empty")

            if len(pdf_paths) == 1:
                # If only one PDF, just copy it
                import shutil
                shutil.copy2(pdf_paths[0], output_path)
                return Path(output_path)

            # Convert paths to Path objects
            pdf_paths = [Path(p) for p in pdf_paths]
            output_path = Path(output_path)

            # Read all PDFs and get their pages
            readers = [PdfReader(pdf_path) for pdf_path in pdf_paths]
            pages = [reader.pages[0] for reader in readers]  # Assume single-page PDFs

            # Get dimensions of all pages
            widths = [float(page.mediabox.width) for page in pages]
            heights = [float(page.mediabox.height) for page in pages]

            # Calculate new page dimensions
            total_padding = padding * (len(pages) - 1) if len(pages) > 1 else 0
            new_width = sum(widths) + total_padding
            new_height = max(heights)

            # Create new PDF with combined page
            writer = PdfWriter()
            new_page = writer.add_blank_page(width=new_width, height=new_height)

            # Add pages horizontally with padding
            current_x_offset = 0
            for i, (page, width) in enumerate(zip(pages, widths)):
                if current_x_offset > 0:
                    # Create transformation to translate the page
                    transformation = Transformation().translate(tx=current_x_offset, ty=0)
                    new_page.merge_transformed_page(page, transformation)
                else:
                    # First page at origin
                    new_page.merge_page(page)

                # Update offset for next page
                current_x_offset += width + padding

            # Save the result
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            print(f'Successfully concatenated {len(pdf_paths)} PDFs to: "{output_path}"')
            return output_path


        @classmethod
        def concatenate_pdfs_vertically(cls, pdf_paths: List[Union[str, Path]], output_path: Union[str, Path], padding: float = 0):
            """
            Vertically concatenate multiple single-page PDFs.

            Parameters:
            -----------
            pdf_paths : List[Union[str, Path]]
                List of paths to PDF files to concatenate vertically
            output_path : Union[str, Path]
                Path for the output concatenated PDF
            padding : float, optional
                Spacing between PDFs in points, by default 0

            Returns:
            --------
            Path
                Path to the created concatenated PDF
            """
            if not pdf_paths:
                raise ValueError("pdf_paths cannot be empty")

            if len(pdf_paths) == 1:
                import shutil
                shutil.copy2(pdf_paths[0], output_path)
                return Path(output_path)

            # Convert paths to Path objects
            pdf_paths = [Path(p) for p in pdf_paths]
            output_path = Path(output_path)

            # Read all PDFs and get their pages
            readers = [PdfReader(pdf_path) for pdf_path in pdf_paths]
            pages = [reader.pages[0] for reader in readers]

            # Get dimensions of all pages
            widths = [float(page.mediabox.width) for page in pages]
            heights = [float(page.mediabox.height) for page in pages]

            # Calculate new page dimensions
            total_padding = padding * (len(pages) - 1) if len(pages) > 1 else 0
            new_width = max(widths)
            new_height = sum(heights) + total_padding

            # Create new PDF with combined page
            writer = PdfWriter()
            new_page = writer.add_blank_page(width=new_width, height=new_height)

            # Add pages vertically with padding (from top to bottom)
            current_y_offset = new_height  # Start from top
            for i, (page, height) in enumerate(zip(pages, heights)):
                current_y_offset -= height  # Move down by page height

                if current_y_offset != (new_height - height):  # Not the first page
                    # Create transformation to translate the page
                    transformation = Transformation().translate(tx=0, ty=current_y_offset)
                    new_page.merge_transformed_page(page, transformation)
                else:
                    # First page
                    transformation = Transformation().translate(tx=0, ty=current_y_offset)
                    new_page.merge_transformed_page(page, transformation)

                # Update offset for next page (subtract padding)
                current_y_offset -= padding

            # Save the result
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            print(f'Successfully concatenated {len(pdf_paths)} PDFs vertically to: "{output_path}"')
            return output_path

        @function_attributes(short_name=None, tags=['pdf','scale', 'resize'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-07-03 16:58', related_items=[])
        @classmethod
        def scale_pdf(cls, input_path: str, output_path: str, scale_factor: float = 0.5):
            """ Scale all aspects of a vector PDF uniformly by `scale_factor`.
            
            Parameters:
                input_path (str): Path to input PDF file.
                output_path (str): Path to save scaled output PDF.
                scale_factor (float): Scaling factor (e.g., 0.5 for 50% size).
                
                
            Usage:
            
                from pyphocorehelpers.plotting.media_output_helpers import PDFHelpers

                # Scale input.pdf down to 50% size, scaling around the center
                PDFHelpers.scale_pdf(input_path=_fig2_final_combined_output_path, output_path=_fig2_final_combined_output_path.with_stem(f"scaled_output"), scale_factor=0.5, center=False)

            """
            from pypdf import PdfReader, PdfWriter, Transformation ## for PDFHelpers
            from pypdf.generic import RectangleObject
            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                # Original size
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)
                transform = Transformation().scale(scale_factor)

                # Apply transformation
                page.add_transformation(transform)

                # Compute new bounding box
                new_w = w * scale_factor
                new_h = h * scale_factor

                # Create new rectangle
                new_box = RectangleObject([0, 0, new_w, new_h])

                # Update MediaBox and CropBox
                page.mediabox = new_box
                page.cropbox = new_box

                writer.add_page(page)

            # Write output
            with open(output_path, "wb") as f_out:
                writer.write(f_out)
                

except ImportError:
    _PDFHELPERS_AVAILABLE = False




# ==================================================================================================================================================================================================================================================================================== #
# SVGHelpers                                                                                                                                                                                                                                                                           #
# ==================================================================================================================================================================================================================================================================================== #
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from typing import List, Union, Tuple
from pathlib import Path

@metadata_attributes(short_name=None, tags=['SVG', 'export', 'filesystem', 'concatenate', 'combine', 'vector'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-07-22 00:00', related_items=['concatenate_pdfs_horizontally'])
class SVGHelpers:
    """ Helpers for concatenating and manipulating SVG files while preserving vector graphics

    from pyphocorehelpers.plotting.media_output_helpers import SVGHelpers

    """

    @classmethod 
    def _parse_svg_dimensions(cls, svg_path: Union[str, Path]) -> Tuple[float, float]:
        """
        Extract width and height from an SVG file.

        Returns:
        --------
        Tuple[float, float]
            (width, height) in pixels
        """
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()

            width = root.get('width', '100')
            height = root.get('height', '100')

            # Parse viewBox if width/height are not specified or are percentages
            viewbox = root.get('viewBox')
            if viewbox:
                try:
                    vb_values = [float(x) for x in viewbox.split()]
                    if len(vb_values) >= 4:
                        vb_width, vb_height = vb_values[2], vb_values[3]

                        # If width/height are percentages or missing, use viewBox
                        if '%' in str(width) or 'em' in str(width) or width == '100':
                            width = vb_width
                        if '%' in str(height) or 'em' in str(height) or height == '100':
                            height = vb_height
                except ValueError:
                    pass  # fallback to default parsing

            # Convert to float, removing units
            def parse_dimension(dim):
                if isinstance(dim, (int, float)):
                    return float(dim)
                dim_str = str(dim).lower()
                # Remove common units and convert to pixels (rough conversion)
                dim_str = re.sub(r'[a-z%]+$', '', dim_str)
                try:
                    return float(dim_str)
                except ValueError:
                    return 100.0  # fallback

            return parse_dimension(width), parse_dimension(height)
        except Exception as e:
            print(f"Error parsing SVG dimensions from {svg_path}: {e}")
            return 100.0, 100.0  # fallback dimensions

    @classmethod
    def concatenate_svgs_horizontally(cls, svg_paths: List[Union[str, Path]], output_path: Union[str, Path], 
                                    padding: float = 0, background_color: str = None) -> Path:
        """
        Horizontally concatenate multiple SVG files while preserving vector graphics.

        Parameters:
        -----------
        svg_paths : List[Union[str, Path]]
            List of paths to SVG files to concatenate horizontally
        output_path : Union[str, Path]
            Path for the output concatenated SVG
        padding : float, optional
            Spacing between SVGs in pixels, by default 0
        background_color : str, optional
            Background color for the combined SVG (e.g., 'white', '#ffffff'), by default None

        Returns:
        --------
        Path
            Path to the created concatenated SVG
        """
        if not svg_paths:
            raise ValueError("svg_paths cannot be empty")

        if len(svg_paths) == 1:
            # If only one SVG, just copy it
            import shutil
            shutil.copy2(svg_paths[0], output_path)
            return Path(output_path)

        # Convert paths to Path objects
        svg_paths = [Path(p) for p in svg_paths]
        output_path = Path(output_path)

        # Parse all SVGs and get their dimensions
        svg_contents = []
        svg_dimensions = []

        for svg_path in svg_paths:
            try:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                svg_contents.append(content)
                width, height = cls._parse_svg_dimensions(svg_path)
                svg_dimensions.append((width, height))
            except Exception as e:
                print(f"Error reading SVG {svg_path}: {e}")
                continue

        if not svg_contents:
            raise ValueError("No valid SVG files could be read")

        # Calculate combined dimensions
        widths = [dim[0] for dim in svg_dimensions]
        heights = [dim[1] for dim in svg_dimensions]

        total_padding = padding * (len(svg_contents) - 1) if len(svg_contents) > 1 else 0
        combined_width = sum(widths) + total_padding
        combined_height = max(heights)

        # Create the combined SVG as string
        svg_parts = []
        svg_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{combined_width}" height="{combined_height}" viewBox="0 0 {combined_width} {combined_height}">')

        # Add background rectangle if specified
        if background_color:
            svg_parts.append(f'  <rect width="100%" height="100%" fill="{background_color}"/>')

        # Add each SVG content horizontally
        current_x_offset = 0

        for i, (content, (width, height)) in enumerate(zip(svg_contents, svg_dimensions)):
            # Extract content between <svg> tags, excluding the SVG element itself
            inner_content = cls._extract_svg_inner_content(content)

            if inner_content.strip():
                # Wrap in a group with translation
                if current_x_offset > 0:
                    svg_parts.append(f'  <g transform="translate({current_x_offset}, 0)">')
                else:
                    svg_parts.append('  <g>')

                # Add the inner content with proper indentation
                for line in inner_content.split('\n'):
                    if line.strip():
                        svg_parts.append(f'    {line.strip()}')

                svg_parts.append('  </g>')

            # Update offset for next SVG
            current_x_offset += width + padding

        svg_parts.append('</svg>')

        # Write the combined SVG
        combined_content = '\n'.join(svg_parts)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)

        print(f'Successfully concatenated {len(svg_contents)} SVGs horizontally to: "{output_path}"')
        return output_path

    @classmethod
    def concatenate_svgs_vertically(cls, svg_paths: List[Union[str, Path]], output_path: Union[str, Path], 
                                  padding: float = 0, background_color: str = None) -> Path:
        """
        Vertically concatenate multiple SVG files while preserving vector graphics.
        """
        if not svg_paths:
            raise ValueError("svg_paths cannot be empty")

        if len(svg_paths) == 1:
            import shutil
            shutil.copy2(svg_paths[0], output_path)
            return Path(output_path)

        # Convert paths to Path objects  
        svg_paths = [Path(p) for p in svg_paths]
        output_path = Path(output_path)

        # Parse all SVGs and get their dimensions
        svg_contents = []
        svg_dimensions = []

        for svg_path in svg_paths:
            try:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                svg_contents.append(content)
                width, height = cls._parse_svg_dimensions(svg_path)
                svg_dimensions.append((width, height))
            except Exception as e:
                print(f"Error reading SVG {svg_path}: {e}")
                continue

        if not svg_contents:
            raise ValueError("No valid SVG files could be read")

        # Calculate combined dimensions
        widths = [dim[0] for dim in svg_dimensions]
        heights = [dim[1] for dim in svg_dimensions]

        total_padding = padding * (len(svg_contents) - 1) if len(svg_contents) > 1 else 0
        combined_width = max(widths)
        combined_height = sum(heights) + total_padding

        # Create the combined SVG as string
        svg_parts = []
        svg_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{combined_width}" height="{combined_height}" viewBox="0 0 {combined_width} {combined_height}">')

        # Add background if specified
        if background_color:
            svg_parts.append(f'  <rect width="100%" height="100%" fill="{background_color}"/>')

        # Add each SVG content vertically
        current_y_offset = 0

        for i, (content, (width, height)) in enumerate(zip(svg_contents, svg_dimensions)):
            # Extract content between <svg> tags
            inner_content = cls._extract_svg_inner_content(content)

            if inner_content.strip():
                # Wrap in a group with translation
                if current_y_offset > 0:
                    svg_parts.append(f'  <g transform="translate(0, {current_y_offset})">')
                else:
                    svg_parts.append('  <g>')

                # Add the inner content with proper indentation
                for line in inner_content.split('\n'):
                    if line.strip():
                        svg_parts.append(f'    {line.strip()}')

                svg_parts.append('  </g>')

            # Update offset for next SVG
            current_y_offset += height + padding

        svg_parts.append('</svg>')

        # Write the combined SVG
        combined_content = '\n'.join(svg_parts)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(combined_content)

        print(f'Successfully concatenated {len(svg_contents)} SVGs vertically to: "{output_path}"')
        return output_path

    @classmethod
    def _extract_svg_inner_content(cls, svg_content: str) -> str:
        """
        Extract the inner content of an SVG file (everything between the root <svg> tags).

        Parameters:
        -----------
        svg_content : str
            The full SVG file content as a string

        Returns:
        --------
        str
            The inner content without the root <svg> element
        """
        import re

        # Remove XML declaration and doctype if present
        content = re.sub(r'<\?xml[^>]*\?>', '', svg_content)
        content = re.sub(r'<!DOCTYPE[^>]*>', '', content)

        # Find the opening and closing svg tags
        # Match opening <svg> tag (may span multiple lines and have attributes)
        svg_start_match = re.search(r'<svg[^>]*>', content, re.DOTALL | re.IGNORECASE)
        if not svg_start_match:
            return ""

        # Find the matching closing </svg> tag
        svg_end_match = re.search(r'</svg\s*>', content, re.IGNORECASE)
        if not svg_end_match:
            return ""

        # Extract content between the tags
        start_pos = svg_start_match.end()
        end_pos = svg_end_match.start()

        inner_content = content[start_pos:end_pos].strip()

        # Remove any nested <svg> root elements that might cause conflicts
        # but keep their content
        inner_content = re.sub(r'<svg[^>]*>', '', inner_content, flags=re.IGNORECASE)
        inner_content = re.sub(r'</svg\s*>', '', inner_content, flags=re.IGNORECASE)

        return inner_content
