from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.transforms import IdentityTransform

def add_figure_text_box(fig, render_text, x=20, y=20, bbox_args=dict(), text_args=dict()):
    """ Adds a small box containing the potentially multi-line render_text to the matplotlib figure. 
    Usage:
        render_text = active_session_computation_config.str_for_attributes_list_display(key_val_sep_char=':')
        add_figure_text_box(plt.gcf(), render_text=render_text)
    """
    if fig is None:
        fig = plt.gcf()
    # This configures the background box that wraps the text content. these are matplotlib.patch.Patch properties
    # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    bbox_props = {'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5} | bbox_args # the properties for the background bounding box for the text
    # place a text box in upper left in axes coords
    # ax.text(0.05, 0.95, render_text, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)
    # active_properties_box_text = fig.text(20, 20, render_text, color="k", fontsize=12, transform=IdentityTransform(), bbox=props)
    # active_properties_box_text = fig.text(**({'x': 20, 'y': 20, 'text': render_text, 'color': 'k', 'fontsize': 12, 'transform': IdentityTransform(), 'bbox':bbox_props} | text_args))    
    active_properties_box_text = fig.text(x, y, render_text, **({'color': 'k', 'fontsize': 12, 'transform': IdentityTransform(), 'bbox':bbox_props} | text_args))
    
    return active_properties_box_text




# fig = plt.figure()
# render_text = active_session_computation_config.str_for_attributes_list_display(key_val_sep_char=':')
# fig.text(0, 250, render_text, color="k", fontsize=12, transform=IdentityTransform(), wrap=True)

# # rgba1 = build_image_from_text(r"IQ: $\sigma_i=15$", color="blue", fontsize=20, dpi=200)
# # rgba2 = build_image_from_text(r"some other string", color="red", fontsize=20, dpi=200)
# # # One can then draw such text images to a Figure using `.Figure.figimage`.
# # fig.figimage(rgba1, 100, 50)
# # fig.figimage(rgba2, 100, 150)

# # # One can also directly draw texts to a figure with positioning
# # # in pixel coordinates by using `.Figure.text` together with
# # # `.transforms.IdentityTransform`.
# # fig.text(100, 250, r"IQ: $\sigma_i=15$", color="blue", fontsize=20,
# #         transform=IdentityTransform())
# # fig.text(100, 350, r"some other string", color="red", fontsize=20,
# #         transform=IdentityTransform())
# plt.show()
