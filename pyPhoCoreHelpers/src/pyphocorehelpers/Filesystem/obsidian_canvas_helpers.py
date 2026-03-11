from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from typing_extensions import TypeAlias
from nptyping import NDArray
from pathlib import Path
import shutil
import numpy as np

from pyjsoncanvas import (
    Canvas,
    TextNode,
    FileNode,
    LinkNode,
    GroupNode,
    GroupNodeBackgroundStyle,
    Edge,
    Color,
)

import shutil ## for copying images
from pyphocorehelpers.image_helpers import ImageHelpers


def sort_nodes_by_position_and_id(nodes_list):
    # Sort by x, y, x1, y1, id in that order
    return sorted(nodes_list, key=lambda node: (node.x, node.y, node.x1, node.y1, node.id))



def create_group_nested_node_hierarchy(loaded_canvas: Canvas):
    """
    Usage:
        loaded_canvas: Canvas = ObsidianCanvasHelper.load(canvas_url=existing_canvas_path)
        group_organized_node_hierarchy = create_group_nested_node_hierarchy(loaded_canvas

    """
    loaded_canvas_nodes: List[GenericNode] = deepcopy(loaded_canvas.nodes)
    loaded_canvas_nodes_df: pd.DataFrame = pd.DataFrame(loaded_canvas_nodes)
    loaded_canvas_nodes_df

    ## Add right-edge columns:
    loaded_text_nodes_df['x1'] = loaded_text_nodes_df['x'] + loaded_text_nodes_df['width']
    loaded_text_nodes_df['y1'] = loaded_text_nodes_df['y'] + loaded_text_nodes_df['height']

    # Sort by columns: 'x' (ascending), 'y' (ascending), 'id' (ascending)
    loaded_text_nodes_df = loaded_text_nodes_df.sort_values(['x', 'y', 'id'])
    loaded_text_nodes_df


    loaded_group_nodes: Set[GroupNode] = set([v for v in loaded_canvas_nodes if (v.type.value == NodeType.GROUP.value)])


    loaded_text_nodes = [v for v in loaded_canvas_nodes if (v.type.value == NodeType.TEXT.value)]
    loaded_text_nodes

    # Loaded variable 'loaded_text_nodes' from kernel state

    loaded_text_nodes_df: pd.DataFrame = pd.DataFrame(loaded_text_nodes)
    ## Add right-edge columns:
    loaded_text_nodes_df['x1'] = loaded_text_nodes_df['x'] + loaded_text_nodes_df['width']
    loaded_text_nodes_df['y1'] = loaded_text_nodes_df['y'] + loaded_text_nodes_df['height']

    # Sort by columns: 'x' (ascending), 'y' (ascending), 'id' (ascending)
    loaded_text_nodes_df = loaded_text_nodes_df.sort_values(['x', 'y', 'id'])
    loaded_text_nodes_df



    group_organized_node_hierarchy: Dict = {}


    a_group_node: GroupNode = loaded_group_nodes[0]

    a_group_node.find_children(loaded_group_nodes[1:])
    return group_organized_node_hierarchy


# @metadata_attributes(short_name=None, tags=['canvas', 'obsidian'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2025-05-21 15:17', related_items=[])
class ObsidianCanvasHelper:
    """ Helps with Obsidian Canvases

    Usage:    
        from pyphocorehelpers.Filesystem.obsidian_canvas_helpers import ObsidianCanvasHelper
        
        canvas_url = Path(r"D:/PhoGlobalObsidian2022/🌐🧠 Working Memory/Pho-Kamran Paper 2024/2025-05-15 - Pho Sorted Events.canvas")
        write_modified_canvas_path: Path = canvas_url.with_name(f'_programmatic_test.canvas')
        loaded_canvas = ObsidianCanvasHelper.load(canvas_url=canvas_url)

        # image_folder_path: Path = Path(r'C:/Users/pho/repos/Spike3DWorkEnv/Spike3D/output/collected_outputs/2025-05-21/gor01_two_2006-6-07_16-40-19_normal_computed_[1, 2]_5.0/ripple/psuedo2D_nan_filled/raw_rgba').resolve()
        image_folder_path: Path = Path(r'C:/Users/pho/repos/Spike3DWorkEnv/Spike3D/output/collected_outputs/2025-05-21/gor01_two_2006-6-07_16-40-19_normal_computed_[1, 2]_5.0/laps/psuedo2D_nan_filled/raw_rgba').resolve()

        target_canvas, _write_status = ObsidianCanvasHelper.add_images_to_canvas(image_folder_path=image_folder_path, image_glob="p_x_given_n*.png", target_canvas=None, write_modified_canvas_path=write_modified_canvas_path, override_write_mode='w')
        # target_canvas, _write_status



    """
    
    @classmethod
    def load(cls, canvas_url: Path) -> Canvas:
        """ 
        
        loaded_canvas: Canvas = ObsidianCanvasHelper.load(canvas_url=existing_canvas_path)
        
        """
        # Load JSON from a string
        with open(canvas_url, 'r', encoding='utf-8') as f:
            # canvas_json = json.load(f)
            canvas_json = f.read()
            
        # Create Canvas from the loaded JSON
        loaded_canvas = Canvas.from_json(json_str=canvas_json)
        return loaded_canvas
    
    @classmethod
    def save(cls, canvas: Canvas, canvas_url: Path, write_mode:str='w'):
        """ Save Canvas back to file 
        
        _status_code
        
        """
        ## INPUTS: active_canvas
        # Save the canvas as JSON
        json_str = canvas.to_json()
        with open(canvas_url, mode=write_mode, encoding='utf-8') as f:
            # canvas_json = json.load(f)
            _status_code = f.write(json_str)
            if _status_code:
                print(f'write to canvas: {_status_code}')
        return _status_code      


    @classmethod
    def group_wrapping_nodes(cls, children_nodes: List, group_name: str='GROUP', group_padding=(50, 30), debug_print=True, **kwargs) -> GroupNode:
        """ given a list of nodes to wrap, builds an appropriately sized (with padding) group of the specified name
        Does not add it to canvas
        
        Usage:
        
            group_node: GroupNode = ObsidianCanvasHelper.group_wrapping_nodes(children_nodes=(laps_group_node, pbes_group_node), group_name=f'{session_name}', group_padding=(100, 90))
            target_canvas.add_node(group_node)


        """
        # (laps_group_node.x, laps_group_node.y, laps_group_node.width, laps_group_node.height)
        # node_shapes = np.vstack([(a_node.x, a_node.y, a_node.width, a_node.height) for i, a_node in enumerate(children_nodes)]) # (n_images, 4)
        
        # extents: (x0, y0, x1, y1)
        node_extents = np.vstack([(a_node.x, a_node.y, (a_node.x + a_node.width),(a_node.y + a_node.height)) for i, a_node in enumerate(children_nodes)]) # (n_images, 4)

        # total_grouped_image_size = np.sum(image_sizes, axis=0)       
        total_grouped_node_extent = (np.min(node_extents[:, 0]), np.min(node_extents[:, 1]), np.max(node_extents[:, 2]), np.max(node_extents[:, 3]))
        
        # total_grouped_node_padded_extent = deepcopy(total_grouped_node_extent)
        # total_grouped_node_padded_extent[2] += 

        total_grouped_node_x_y_width_height = (total_grouped_node_extent[0], total_grouped_node_extent[1], (total_grouped_node_extent[2] - total_grouped_node_extent[0]), (total_grouped_node_extent[3] - total_grouped_node_extent[1]))  ## since being stacked horizontally, use the sum of the widths, but the max of the heights
        total_grouped_node_size = np.array(total_grouped_node_x_y_width_height[2:])
        # total_grouped_images_padding = (int(round(float(x_padding)*float(n_images-1))), 0)
        initial_x, initial_y = total_grouped_node_x_y_width_height[:2]

        group_padding = np.array(group_padding)
        total_group_size = total_grouped_node_size + (2 * group_padding)
        group_offset = np.array((initial_x, initial_y)) - group_padding

        
        if debug_print:
            print(f'image_sizes: {np.shape(node_extents)}, total_grouped_node_x_y_width_height: {total_grouped_node_x_y_width_height}')        

        ## group all elements in a group
        group_node = GroupNode(
            x=group_offset[0],
            y=group_offset[1],
            width=total_group_size[0],
            height=total_group_size[1],
            label=group_name,
            # background="/path/to/background.jpg",
            # backgroundStyle=GroupNodeBackgroundStyle.COVER,
            **kwargs,
        )
        return group_node



    @classmethod 
    def add_images_to_canvas(cls, image_folder_path: Path, image_glob: str = "*.png", target_canvas: Optional[Canvas]=None, write_modified_canvas_path: Path=None,
                                    x_padding: int = 2, canvas_image_node_scale: float=None, image_group_name: str = 'MyGroup', initial_x: int = 0, initial_y: int = 0, max_num_to_add: int = 1000,
                                    obsidian_vault_root_path: Path = Path(r'D:\PhoGlobalObsidian2022'), vault_relative_image_dir_filepath: str = 'z__META\__IMAGES',
                                    override_write_mode='x', debug_print = False):
        """ Adds the images matching the glob in the `image_folder_path` to the canvas, or creates a new canvas, as needed
        
        
        Adds the images to the canvas
        
        """
        def _subfn_get_img_obsidian_global_unique_name(an_img_path: Path) -> str:    
            """ from my personal export path conventions, builds a globally unique image name (which has to be the case for a canvas)"""
            
            img_path_name_parts = an_img_path.parts
            date_part_index = next((i for i, part in enumerate(img_path_name_parts) if re.match(r'^\d{4}-\d{2}-\d{2}', part)), None)
            session_part_index: int = date_part_index + 1
            img_out_context_parts: List[str] = img_path_name_parts[session_part_index:] # ('gor01_two_2006-6-07_16-40-19_normal_computed_[1, 2]_5.0', 'ripple', 'psuedo2D_nan_filled', 'raw_rgba', 'p_x_given_n[9].png')
            return '-'.join(img_out_context_parts) # 'gor01_two_2006-6-07_16-40-19_normal_computed_[1, 2]_5.0-ripple-psuedo2D_nan_filled-raw_rgba-p_x_given_n[9].png'


        # ==================================================================================================================================================================================================================================================================================== #
        # BEGIN FUNCTION BODY                                                                                                                                                                                                                                                                  #
        # ==================================================================================================================================================================================================================================================================================== #
        images_dict: Dict = ImageHelpers.load_png_images_pathlib(image_folder_path, image_glob=image_glob)
        n_images: int = len(images_dict)
        # Print the loaded images
        print(f"Loaded {len(images_dict)} PNG images from '{image_folder_path}'.")

        ## INPUTS: loaded_canvas
        # Create a new canvas
        if target_canvas is None:
            print(f'creating new Canvas as none was provided!')
            write_mode = 'x' # set write mode to create only so it doesn't overwrite an existing cnvas
            target_canvas = Canvas(nodes=[], edges=[])
        else:
            write_mode = 'w' # overwrite
            
        if override_write_mode is not None:
            write_mode = override_write_mode

        ## INPUTS: active_canvas, debug_print
        
        obsidian_canvas_image_link_path: Path = obsidian_vault_root_path.joinpath(vault_relative_image_dir_filepath) #  Path(r'D:\PhoGlobalObsidian2022\z__META\__IMAGES')
        # image path is like "collected_outputs\2025-05-21\gor01_two_2006-6-07_16-40-19_normal_computed_[1, 2]_5.0\ripple\psuedo2D_nan_filled\raw_rgba\p_x_given_n[7].png"

        n_added: int = 0
        
        # text_node = TextNode(x=initial_x, y=initial_y, width=200, height=100, text=f"#{image_group_name}")
        # target_canvas.add_node(text_node)
        if canvas_image_node_scale is None:
            canvas_image_node_scale = 1.0
            
        image_sizes = np.vstack([(int(round(canvas_image_node_scale * float(an_img.size[0]))), int(round(canvas_image_node_scale * float(an_img.size[1])))) for i, (img_name, an_img) in enumerate(images_dict.items())]) # (n_images, 2)
        # if debug_print:
        #     print(f'image_sizes: {np.shape(image_sizes)}, max_img_sizes: {np.max(image_sizes, axis=0)}')

        # total_grouped_image_size = np.sum(image_sizes, axis=0)
        
        if debug_print:
            print(f'max_img_sizes: {np.max(image_sizes, axis=0)}')

        total_grouped_image_size = (np.sum(image_sizes[:, 0], axis=0), np.max(image_sizes[:, 1], axis=0))  ## since being stacked horizontally, use the sum of the widths, but the max of the heights
        total_grouped_images_padding = (int(round(float(x_padding)*float(n_images-1))), 0)

        group_padding = np.array((50, 30))
        total_group_size = total_grouped_image_size + np.array(total_grouped_images_padding) + (2 * group_padding)
        group_offset = np.array((initial_x, initial_y)) - group_padding

        # group_offset.tolist()
        if debug_print:
            print(f'total_group_size: {total_group_size},\ngroup_offset: {group_offset}')
            
        for i, (img_name, an_img) in enumerate(images_dict.items()):
            if i < max_num_to_add:
                an_img_path: Path = image_folder_path.joinpath(f'{img_name}.png')
                assert an_img_path.exists(), f"an_img_path: {an_img_path} does not exist"        
                global_unique_image_filename: str = f"{_subfn_get_img_obsidian_global_unique_name(an_img_path=an_img_path)}"
                an_img_vault_filepath = obsidian_canvas_image_link_path.joinpath(global_unique_image_filename)
                # assert not vault_image_filepath.exists()
                # Copy the file
                shutil.copy2(an_img_path, an_img_vault_filepath)
                if debug_print:
                    print(f'copying image from: "{an_img_path}" to vault_image_filepath: "{an_img_vault_filepath}"...')

                # an_img_height, an_img_width = an_img.size
                an_img_width, an_img_height = an_img.size
                
                if canvas_image_node_scale is not None:
                    an_img_width = int(round(canvas_image_node_scale * float(an_img_width)))
                    an_img_height = int(round(canvas_image_node_scale * float(an_img_height)))
                # node_url_str: str = vault_relative_image_dir_filepath
                node_url_str: str = an_img_vault_filepath.relative_to(obsidian_vault_root_path).as_posix()
                file_node = FileNode(x=initial_x, y=initial_y, width=an_img_width, height=an_img_height, file=node_url_str)
                target_canvas.add_node(file_node)
                initial_x = initial_x + an_img_width + x_padding
                n_added = n_added + 1
                
            else:
                # print(f'skipping because max_num_to_add: {max_num_to_add}')
                pass
            
        # END for i, (img_name, an_i...
        print(f'added {n_added} images to canvas.')
        
        ## group all elements in a group
        group_node = GroupNode(
            x=group_offset[0],
            y=group_offset[1],
            width=total_group_size[0],
            height=total_group_size[1],
            label=image_group_name,
            # background="/path/to/background.jpg",
            # backgroundStyle=GroupNodeBackgroundStyle.COVER,
        )
        target_canvas.add_node(group_node)

        # save the canvas back to a file _____________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________ #
        if write_modified_canvas_path is not None:
            # write_modified_canvas_path: Path = write_modified_canvas_path.with_name(f'_programmatic_test.canvas')
            _write_status = cls.save(canvas=target_canvas, canvas_url=write_modified_canvas_path, write_mode=write_mode)
        else:
            print(f'no write_modified_canvas_path provided, skipping write')
            _write_status = None

        return target_canvas, group_node, _write_status


    @classmethod
    def build_canvas_for_exported_session_posteriors(cls, sessions_export_folder = Path('K:/scratch/collected_outputs/2025-05-22'),
                                                     intra_session_v_spacing: int = 3000, intra_laps_and_pbes_v_spacing: int = 1000, is_single_canvas: bool = True, common_add_images_to_canvas_kwargs = dict(debug_print=False, canvas_image_node_scale=0.2), image_glob="p_x_given_n*.png",
                                                     canvas_folders_url = Path(r"D:/PhoGlobalObsidian2022/🌐🧠 Working Memory/Pho-Kamran Paper 2024/_programmatic_test"), obsidian_vault_root_path: Path = Path(r'D:/PhoGlobalObsidian2022'), 
                                                    #  series_folder_name: str = 'psuedo2D_nan_filled',
                                                    #  series_folder_name: str = 'psuedo2D_ignore',
                                                    # export_full_path: str = 'psuedo2D_ignore/raw_rgba',
                                                    export_session_folder_relative_path: str = 'combined/multi',
                                                     ):
        
        """ Takes an export directory of exported posteriors for each session, and generates either a combined or session-specific Obsidian Canvas

                
        added_groups_dict, write_modified_canvas_path = ObsidianCanvasHelper.build_canvas_for_exported_session_posteriors(sessions_export_folder = Path('K:/scratch/collected_outputs/2025-05-22'),
                                                     intra_session_v_spacing: int = 3000, intra_laps_and_pbes_v_spacing: int = 1000, is_single_canvas: bool = True, common_add_images_to_canvas_kwargs = dict(debug_print=False), image_glob="p_x_given_n*.png",
                                                     canvas_folders_url = Path(r"D:/PhoGlobalObsidian2022/🌐🧠 Working Memory/Pho-Kamran Paper 2024/_programmatic_test"),
                                                     )


        """
        ## INPUTS: intra_session_v_spacing, intra_laps_and_pbes_v_spacing, is_single_canvas

        ## INPUTS: base_path, canvas_folders_url
        added_groups_dict = {}

        if 'obsidian_vault_root_path' not in common_add_images_to_canvas_kwargs:
            common_add_images_to_canvas_kwargs['obsidian_vault_root_path'] = obsidian_vault_root_path
            

        # Create a new canvas
        if is_single_canvas:
            print(f'creating new Canvas as none was provided!')
            target_canvas = Canvas(nodes=[], edges=[])
            initial_x = 0
            initial_y = 0    

        else:
            target_canvas = None
            initial_x = 0
            initial_y = 0
            
        # Iterate through only the directories (folders)
        for session_folder in [item for item in sessions_export_folder.iterdir() if item.is_dir()]:
            print(f"Found folder: {session_folder.name}")
            session_name: str = session_folder.name.removesuffix('_weighted_position_posterior')
            print(f'\tsession_name: {session_name}')
            

            if not is_single_canvas:
                # Do something with each folder
                write_modified_canvas_path: Path = canvas_folders_url.joinpath(f'_programmatic_test_{session_name}.canvas')
                # image_folder_path: Path = Path(r'C:/Users/pho/repos/Spike3DWorkEnv/Spike3D/output/collected_outputs/2025-05-21/gor01_two_2006-6-07_16-40-19_normal_computed_[1, 2]_5.0/ripple/psuedo2D_nan_filled/raw_rgba').resolve()
                target_canvas = None ## start with a blank canvas each time
                
            else:
                ## single_canvas mode: set no save URL so it doesn't write out to file
                write_modified_canvas_path = None
                
            children_nodes = [] 


            laps_group_node = None
            # image_folder_path: Path = session_folder.joinpath(f'laps/{series_folder_name}/{export_format_series_path}').resolve()
            image_folder_path: Path = session_folder.joinpath(f'laps/{export_session_folder_relative_path}').resolve()
            try:
                target_canvas, laps_group_node, _write_status = cls.add_images_to_canvas(image_folder_path=image_folder_path, image_glob=image_glob, target_canvas=target_canvas, write_modified_canvas_path=write_modified_canvas_path, override_write_mode='w',
                                                                                        image_group_name=f'Laps - {session_name}', initial_x = initial_x, initial_y = initial_y, **common_add_images_to_canvas_kwargs)
                if laps_group_node is not None:
                    children_nodes.append(laps_group_node)
            except ValueError as e:
                print(f'\tfailed to export laps to Canvas with error {e}. Skipping and continuing...')
                pass
            except Exception as e:
                raise 


            ## use the existing canvas
            pbes_group_node = None
            initial_y = initial_y + intra_laps_and_pbes_v_spacing
            # image_folder_path: Path = session_folder.joinpath(f'ripple/{series_folder_name}/{export_format_series_path}').resolve()
            image_folder_path: Path = session_folder.joinpath(f'ripple/{export_session_folder_relative_path}').resolve()
            try:
                target_canvas, pbes_group_node, _write_status = cls.add_images_to_canvas(image_folder_path=image_folder_path, image_glob=image_glob, target_canvas=target_canvas, write_modified_canvas_path=write_modified_canvas_path, override_write_mode='w',
                                                                                        image_group_name=f'PBEs - {session_name}', initial_x = initial_x, initial_y=initial_y, **common_add_images_to_canvas_kwargs)
                if pbes_group_node is not None:
                    children_nodes.append(pbes_group_node)

            except ValueError as e:
                print(f'\tfailed to export PBEs to Canvas with error {e}. Skipping and continuing...')
                pass
            except Exception as e:
                raise 



            ## Build session group
            group_node = None
            if len(children_nodes) > 0:
                group_node: GroupNode = cls.group_wrapping_nodes(children_nodes=children_nodes, group_name=f'{session_name}', group_padding=(100, 90))
                target_canvas.add_node(group_node)


            # added_groups_dict[session_name] = group_node
            added_groups_dict[f'{session_name}'] = {'session': group_node, 'laps': laps_group_node, 'pbes': pbes_group_node}
            
            if is_single_canvas:
                initial_x = 0
                initial_y = initial_y + intra_session_v_spacing ## spacing of 5000 between sessions

            else:
                ## reset canvas so new one is created
                target_canvas = None
                ## re-zero
                initial_x = 0
                initial_y = 0    

            # target_canvas, _write_status


        if is_single_canvas:
            ## do final save
            write_modified_canvas_path: Path = canvas_folders_url.joinpath(f'ALL_SESSIONS.canvas') ## session-specific canvas save URL
            _write_status = ObsidianCanvasHelper.save(canvas=target_canvas, canvas_url=write_modified_canvas_path, write_mode='w')
            print(f'Finished writing to "{write_modified_canvas_path.as_posix()}"')
        ## OUTPUTS: added_groups_dict, write_modified_canvas_path

        return added_groups_dict, write_modified_canvas_path
