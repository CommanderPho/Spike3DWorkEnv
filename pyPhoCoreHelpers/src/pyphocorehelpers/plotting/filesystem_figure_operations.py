# Take the individual cell's pf export figures and composite them into a single stack
from typing import Tuple, Dict, List, Optional
from pathlib import Path
from PIL import Image
from pyphocorehelpers.function_helpers import function_attributes


@function_attributes(short_name=None, tags=['image', 'stack', 'batch', 'file', 'stack'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-01-12 00:00', related_items=[])
def render_image_stack(images: List[Path], offset=10, single_image_alpha_level:float=0.5):
   """ 
    Given a list of equally sized figures, how do I overlay them in a neat looking stack and produce an output graphic from that?
    I want them offset slightly from each other to make a visually appealing stack


    single_image_alpha_level = 0.5 - adjust this value to set the desired transparency level (0.0 to 1.0)
    offset = 10  # your desired offset

    2024-01-12 - works well

    Usage:
        from pyphocorehelpers.plotting.filesystem_figure_operations import render_image_stack

        # Let's assume you have a list of images
        images = ['image1.png', 'image2.png', 'image3.png']  # replace this with actual paths to your images
        output_img, output_path = render_image_stack(out_figs_paths, offset=55, single_image_alpha_level=0.85)

   """

   # Open the images
   imgs = [Image.open(i) for i in images]

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
   output_width = width + offset * (len(imgs) - 1)
   output_height = height + offset * (len(imgs) - 1)

   output_img = Image.new('RGBA', (output_width, output_height))

   # Overlay images with offset
   for i, img in enumerate(imgs):
      output_img.paste(img, (i * offset, i * offset), img)

   output_path: Path = Path('output/stacked_images.png').resolve()
   output_img.save(output_path)
   return output_img, output_path

