from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from typing_extensions import TypeAlias
import nptyping as ND
from nptyping import NDArray
import neuropy.utils.type_aliases as types

import numpy as np
import pandas as pd
from copy import deepcopy

# from function_helpers import function_attributes

class HairyLinePlot:
    """ 

    """
    @classmethod
    def _perform_plot_hairy_overlayed_position(cls, x: NDArray, y: NDArray, ax, normal_x=None, normal_y=None, hair_length:float=1.0, linewidth: float=1.3, color='red', alpha:Optional[float]=None, should_draw_reference_line: bool=False, reference_line_kwargs=None, **kwargs):
        """ plots only the extremely confident context periods on the position trajectory over time (red when sure it's Long, blue when sure it's Short)


            For a given plotted line plot, draws thin line segments called "hairs" normal to the line's path to indicate values at that x-value. 
            Each hair can have the following properties:
                - height - the length of the hair extending from the line's location (e.g. the hair's root) normally outwards
                - thickness
                - color - the color of the hair
                - opacity - the alpha of the hair


            should_draw_reference_line: whether to the draw the background (position) line

        -  I have a line that's already plotted on a matplotlib axes based on two df columns: ['t', 'x_meas']. I want to draw a "glow" effect over it using the two new df columns (P_Long_Score, P_Long_Opacity) the follows the line perfectly and only draws when the threshold is exceeded. Higher P_Long values should be bolder, meaning more thick or more opaque
        - determine render thickness and opacity by how much greater ['P_Long'] is than the threshold value (0.8)

        #TODO 2025-05-05 15:02: - [ ] Increasing `extreme_threshold` should not have an effect on the thicknesses, only the masked/unmasked regions extreme_threshold=0.9, thickness_ramping_multiplier=50
            - fix the mapping functions here and I think it would be a lot better



        History:
            Originally from `pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions._perform_plot_hairy_overlayed_position` -> `pyphocorehelpers.plotting.hairy_lines_plot._perform_plot_hairy_overlayed_position`

        Usage:

            from pyphocorehelpers.plotting.hairy_lines_plot import HairyLinePlot

            ## INPUTS: a_decoded_marginal_posterior_df

            ## plot the basic lap-positions (measured) over time figure:
            _out = dict()
            _out['_display_grid_bin_bounds_validation'] = curr_active_pipeline.display(display_function='_display_grid_bin_bounds_validation', active_session_configuration_context=None, include_includelist=[], save_figure=False) # _display_grid_bin_bounds_validation
            fig = _out['_display_grid_bin_bounds_validation'].figures[0]
            out_axes_list =_out['_display_grid_bin_bounds_validation'].axes
            out_plot_data =_out['_display_grid_bin_bounds_validation'].plot_data

            ## get the lines2D object to turn off the default position lines:
            position_lines_2D = out_plot_data['position_lines_2D']
            ## hide all inactive lines:
            for a_line in position_lines_2D:
                a_line.set_visible(False)


            an_pos_line_artist, df_viz = HairyLinePlot._perform_plot_hairy_overlayed_position(df=deepcopy(a_decoded_marginal_posterior_df), ax=out_axes_list[0], extreme_threshold=0.7) # , thickness_ramping_multiplier=5
            df_viz

            _out

        Usage 2:
                        hairs_line_collection, pos_line_artist = cls._perform_plot_hairy_overlayed_position(x = df_viz[t_bin_col_name].values, y = df_viz['x_meas'].values,
                                                                                                                linewidth = df_viz[f'{a_var_name}_Score'].values[:-1],
                                                                                                                alpha = df_viz[f'{a_var_name}_Opacity'].values[:-1],
                                                                  )



        """
        from matplotlib.collections import LineCollection
        from matplotlib.colors import to_rgba
        ## determine render thickness and opacity by how much greater ['P_Long'] is than the threshold value (0.8)

        assert ax is not None, f"this function does not create its own figure or axes. pass one in."

        ## build plot
        num_points: int = len(x)
        
        # Create individual disconnected line segments normal to the reference line
        segments = []
        a_normal_x = []
        a_normal_y = []

        for i in range(num_points):

            if (normal_x is not None) and (normal_y is not None):
                ## NEW-WORKING REPLACEMENT use these pre-computed arrays to build the segments
                pass
                assert len(normal_x) == len(normal_y)
                assert len(normal_x) == num_points
                # ---------- preferred path: use pre-computed normals -------------
                if (normal_x is not None) and (normal_y is not None):
                    assert (len(normal_x) == len(normal_y) == num_points), ("normal_x / normal_y must match x, y length")

                    # Decide this segment’s actual length
                    if np.ndim(hair_length) == 0:        # scalar
                        curr_len = hair_length
                    else:                                # array-like
                        curr_len = hair_length[i]

                    # Start at the curve point, go OUTWARD only
                    x_start, y_start = x[i], y[i]
                    x_end   = x_start + normal_x[i] * curr_len
                    y_end   = y_start + normal_y[i] * curr_len

                    segments.append([[x_start, y_start], [x_end, y_end]])
                
            else:
                ## BAD, Manual
                # Calculate tangent direction at this point
                if i == 0 and len(x) > 1:
                    # First point: use tangent to next point
                    dx = x[1] - x[i]
                    dy = y[1] - y[i]
                elif i == len(x) - 1 and len(x) > 1:
                    # Last point: use tangent from previous point
                    dx = x[i] - x[i-1]
                    dy = y[i] - y[i-1]
                elif len(x) > 2:
                    # Middle points: use average of adjacent tangents
                    dx = (x[i+1] - x[i-1]) / 2
                    dy = (y[i+1] - y[i-1]) / 2
                else:
                    # Single point or two points: default to vertical
                    dx, dy = 1, 0
                
                # Calculate normal direction (perpendicular to tangent)
                # Rotate tangent 90 degrees: (dx, dy) -> (dy, -dx)
                # norm = np.sqrt(dx*dx + dy*dy)
                # if norm > 0:
                #     ## here is where they're being set to floats
                #     normal_x = dy / norm
                #     normal_y = -dx / norm
                # else:
                #     normal_x, normal_y = 0, 1  # Default to vertical
                
                # # Create hair segment normal to the line
                # hair_length = linewidth[i] if hasattr(linewidth, '__len__') else linewidth
                # half_length = hair_length / 2
                
                # segments.append([
                #     [x[i] - normal_x * half_length, y[i] - normal_y * half_length],
                #     [x[i] + normal_x * half_length, y[i] + normal_y * half_length]
                # ])
                
                # Compute local normal
                norm = np.hypot(dx, dy)
                if norm > 0:
                    nx = dy / norm
                    ny = -dx / norm
                else:
                    nx, ny = 0, 1

                # Create hair segment normal to the line
                # Use local nx, ny (don’t overwrite function args)
                hair_length_i = linewidth[i] if hasattr(linewidth, '__len__') else linewidth
                half_length = hair_length_i / 2

                segments.append([
                    [x[i] - nx * half_length, y[i] - ny * half_length],
                    [x[i] + nx * half_length, y[i] + ny * half_length]
                ])
                a_normal_x.append(nx)
                a_normal_y.append(ny)
                
        ## end for i in ...
        
        segments = np.array(segments)
        a_normal_x = np.array(a_normal_x)
        a_normal_y = np.array(a_normal_y)
        normal_x = deepcopy(a_normal_x)
        normal_y = deepcopy(a_normal_y)


        # Compute attributes for each segment (use start of segment)
        if isinstance(linewidth, (float, int)):
            linewidths = np.full((num_points,), fill_value=linewidth)
        else:
            linewidths = deepcopy(linewidth)
            
        assert len(linewidths) == num_points, f"num_points: {num_points}, len(linewidths): {len(linewidths)}, linewidths: {linewidths}"
        
        ## build the appropriate colors
        if not isinstance(color, NDArray):
            base_rgba = np.array(to_rgba(color))  # converts color name to RGBA
        else:
            base_rgba = deepcopy(color)
            ## TODO: assumes that color is scalar

        assert np.ndim(np.squeeze(base_rgba)) == 1, f"#TODO 2025-07-30 10:52: - [ ] expect a scalar color like color='red' for now, easy to implement but not yet done 2025-07-29.\nbase_rgba: {base_rgba}"

        if alpha is None:
            ## extract the alpha from the color, in case the user provided the alpha in the color
            alpha = base_rgba[3] # get just the alpha component

        if isinstance(alpha, (float, int)):
            alphas = np.full((num_points,), fill_value=alpha)
        else:
            alphas = deepcopy(alpha)
            
        assert len(alphas) == num_points, f"num_points: {num_points}, len(alphas): {len(alphas)}, alphas: {alphas}"
        base_rgba = base_rgba[:3]  # strip alpha, we'll set it per-segment
        colors = np.tile(base_rgba, (len(alphas), 1)) # (1956, 3)
        colors = np.hstack([colors, alphas[:, None]])  # append alphas column-wise (1956, 4)

        markersize: float = kwargs.get('markersize', 5) ## translate the marker size to the hair length? 5 is the default
        # Use a fixed linewidth for the hair thickness since we're creating vertical hairs
        hair_linewidth = 1.0  # Fixed width for the hair lines themselves
        hairs_line_collection: LineCollection = LineCollection(segments, linewidths=hair_linewidth, colors=colors, facecolors='none', zorder=kwargs.get('zorder', 2)) ## don't pass kwargs by default, they won't work
        ax.add_collection(hairs_line_collection)

        ## draw a constant-thickness solid black lines for position - do only once, post-hoc:
        if should_draw_reference_line:
            reference_line_kwargs = dict(color='black', linewidth=1, zorder=10) | reference_line_kwargs
            pos_line_artist = ax.plot(x, y, reference_line_kwargs)
        else:
            pos_line_artist = None

        return hairs_line_collection, pos_line_artist





    @classmethod
    def plot_hairy_overlayed_position(cls, df: pd.DataFrame, ax, extreme_threshold: float=0.9, opacity_max:float=0.7, thickness_ramping_multiplier:float=35.0, prob_to_thickness_ramping_function=None, a_var_name_to_color_map = {'P_Long': 'red', 'P_Short': 'blue'},
            pos_col_name='x_meas', t_bin_col_name: Optional[str]=None, **kwargs):
        """ plots only the extremely confident context periods on the position trajectory over time (red when sure it's Long, blue when sure it's Short)


            For a given plotted line plot, draws thin line segments called "hairs" normal to the line's path to indicate values at that x-value. 
            Each hair can have the following properties:
                - height - the length of the hair extending from the line's location (e.g. the hair's root) normally outwards
                - thickness
                - color - the color of the hair
                - opacity - the alpha of the hair


        -  I have a line that's already plotted on a matplotlib axes based on two df columns: ['t', 'x_meas']. I want to draw a "glow" effect over it using the two new df columns (P_Long_Score, P_Long_Opacity) the follows the line perfectly and only draws when the threshold is exceeded. Higher P_Long values should be bolder, meaning more thick or more opaque
        - determine render thickness and opacity by how much greater ['P_Long'] is than the threshold value (0.8)

        #TODO 2025-05-05 15:02: - [ ] Increasing `extreme_threshold` should not have an effect on the thicknesses, only the masked/unmasked regions extreme_threshold=0.9, thickness_ramping_multiplier=50
            - fix the mapping functions here and I think it would be a lot better



        History:
            Originally from `pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions._perform_plot_hairy_overlayed_position` -> `pyphocorehelpers.plotting.hairy_lines_plot._perform_plot_hairy_overlayed_position`

        Usage:

            from pyphocorehelpers.plotting.hairy_lines_plot import HairyLinePlot

            ## INPUTS: a_decoded_marginal_posterior_df

            ## plot the basic lap-positions (measured) over time figure:
            _out = dict()
            _out['_display_grid_bin_bounds_validation'] = curr_active_pipeline.display(display_function='_display_grid_bin_bounds_validation', active_session_configuration_context=None, include_includelist=[], save_figure=False) # _display_grid_bin_bounds_validation
            fig = _out['_display_grid_bin_bounds_validation'].figures[0]
            out_axes_list =_out['_display_grid_bin_bounds_validation'].axes
            out_plot_data =_out['_display_grid_bin_bounds_validation'].plot_data

            ## get the lines2D object to turn off the default position lines:
            position_lines_2D = out_plot_data['position_lines_2D']
            ## hide all inactive lines:
            for a_line in position_lines_2D:
                a_line.set_visible(False)


            an_pos_line_artist, df_viz = _perform_plot_hairy_overlayed_position(df=deepcopy(a_decoded_marginal_posterior_df), ax=out_axes_list[0], extreme_threshold=0.7) # , thickness_ramping_multiplier=5
            df_viz

            _out



            NOTE: Interesting thickness/opacity modulators:


            interesting_hair_parameter_kwarg_dict = {
                'defaults': dict(extreme_threshold=0.8, opacity_max=0.7, thickness_ramping_multiplier=35),
                '50_sec_window_scale': dict(extreme_threshold=0.5, thickness_ramping_multiplier=50),
            }


            #  prob_to_thickness_ramping_function= lambda p: max(0.0, (p - 0.5) * 15),
            #  extreme_threshold=0.9, prob_to_thickness_ramping_function= lambda p: 6.0, ## constant for all probabilities
            extreme_threshold=0.1, prob_to_thickness_ramping_function= lambda p: (5.0 * p), 


        """
        from matplotlib.collections import LineCollection
        from matplotlib.colors import to_rgba
        from matplotlib.lines import Line2D
        from neuropy.core.epoch import Epoch, TimeColumnAliasesProtocol, subdivide_epochs, ensure_dataframe, ensure_Epoch
        ## determine render thickness and opacity by how much greater ['P_Long'] is than the threshold value (0.8)
        ## INPUTS: a_decoded_marginal_posterior_df


        assert ax is not None, f"this function does not create its own figure or axes. pass one in."

        ## add plotting utility columns:
        df_viz: pd.DataFrame = deepcopy(df)


        if prob_to_thickness_ramping_function is None:
            prob_to_thickness_ramping_function = lambda p: max(0.0, (p - extreme_threshold) * thickness_ramping_multiplier)
        else:
            print(f'using custom `prob_to_thickness_ramping_function` provided, and ignoring `thickness_ramping_multiplier`')


        for a_var_name in a_var_name_to_color_map:
            if thickness_ramping_multiplier is None:
                df_viz[f'{a_var_name}_Score'] = df_viz[a_var_name].apply(lambda p: max(0.0, p)) ## How the THICKNESS of the overlay line ramps with value
            else:
                ## normal ramping function applied:
                df_viz[f'{a_var_name}_Score'] = df_viz[a_var_name].apply(prob_to_thickness_ramping_function) ## How the THICKNESS of the overlay line ramps with value    

            df_viz[f'{a_var_name}_Opacity'] = df_viz[a_var_name].apply(lambda p: 0.0 if p < extreme_threshold else min(opacity_max, (p - extreme_threshold) * 20)) ## OPACITY of the line ramps with value


        if (t_bin_col_name is not None):
            if t_bin_col_name in df_viz:
                pass
            else:
                print(f't_bin_col_name: "{t_bin_col_name}" was not found in df_viz: {list(df_viz.columns)}. Trying defaults')
                t_bin_col_name = None # set to None

        if t_bin_col_name is None:
            t_bin_col_name: str = TimeColumnAliasesProtocol.find_first_extant_suitable_columns_name(df=df_viz, col_connonical_name='t', required_columns_synonym_dict={'t':['t','t_bin_center']}, should_raise_exception_on_fail=True)

        for a_var_name, a_colors in a_var_name_to_color_map.items():

            # # Extract full segments before masking
            # points = np.array([df_viz[t_bin_col_name].values, df_viz[pos_col_name].values]).T
            # segments = np.stack([points[:-1], points[1:]], axis=1)

            # Compute attributes for each segment (use start of segment)
            prob_var_values = df_viz[f'{a_var_name}'].values
            mask = (prob_var_values[:-1] > extreme_threshold) & (prob_var_values[1:] > extreme_threshold) ## if the values don't exceed the `extreme_threshold`, they aren't drawn (nothing is drawn there)

            # linewidths = df_viz[f'{a_var_name}_Score'].values[:-1][mask]
            # alphas = df_viz[f'{a_var_name}_Opacity'].values[:-1][mask]
            # ## build the appropriate colors
            # # inside loop
            # base_rgba = np.array(to_rgba(a_colors))  # converts color name to RGBA
            # base_rgba = base_rgba[:3]  # strip alpha, we'll set it per-segment
            # colors = np.tile(base_rgba, (len(alphas), 1))
            # colors = np.hstack([colors, alphas[:, None]])  # append alphas column-wise
            hairs_line_collection, pos_line_artist = cls._perform_plot_hairy_overlayed_position(x = df_viz[t_bin_col_name].values[:-1][mask], y = df_viz[pos_col_name].values[:-1][mask],
                                                                                                    linewidth = df_viz[f'{a_var_name}_Score'].values[:-1][mask],
                                                                                                    color=a_colors,
                                                                                                    alpha = df_viz[f'{a_var_name}_Opacity'].values[:-1][mask], 
                                                                                                    should_draw_reference_line=False, ax=ax, **kwargs
                                                        )

            # # Apply mask to segments
            # segments = segments[mask]
            # lc = LineCollection(segments, linewidths=linewidths, colors=colors)
            # ax.add_collection(lc)


        ## draw a constant-thickness solid black lines for position - do only once, post-hoc:
        pos_line_artist = ax.plot(df_viz[t_bin_col_name].values,
                df_viz['x_meas'].values,
                color='black', linewidth=1, zorder=10)


        legend_handles = [Line2D([0], [0], color=color, lw=3, label=label.replace('P_', '')) for label, color in a_var_name_to_color_map.items()]
        ax.legend(handles=legend_handles, loc='upper right')

        return pos_line_artist, df_viz



# @function_attributes(short_name=None, tags=['figure', 'hairly-plot', 'matplotlib', 'confidence', 'position', 'laps'], input_requires=[], output_provides=[], uses=[], used_by=['_display_decoded_trackID_marginal_hairy_position'], creation_date='2025-05-03 15:44', related_items=[])
def _perform_plot_hairy_overlayed_position(df: pd.DataFrame, ax, extreme_threshold: float=0.9, opacity_max:float=0.7, thickness_ramping_multiplier:float=35.0, prob_to_thickness_ramping_function=None, a_var_name_to_color_map = {'P_Long': 'red', 'P_Short': 'blue'}, **kwargs):
    """ plots only the extremely confident context periods on the position trajectory over time (red when sure it's Long, blue when sure it's Short)


        For a given plotted line plot, draws thin line segments called "hairs" normal to the line's path to indicate values at that x-value. 



    -  I have a line that's already plotted on a matplotlib axes based on two df columns: ['t', 'x_meas']. I want to draw a "glow" effect over it using the two new df columns (P_Long_Score, P_Long_Opacity) the follows the line perfectly and only draws when the threshold is exceeded. Higher P_Long values should be bolder, meaning more thick or more opaque
    - determine render thickness and opacity by how much greater ['P_Long'] is than the threshold value (0.8)

    #TODO 2025-05-05 15:02: - [ ] Increasing `extreme_threshold` should not have an effect on the thicknesses, only the masked/unmasked regions extreme_threshold=0.9, thickness_ramping_multiplier=50
        - fix the mapping functions here and I think it would be a lot better



    History:
        Originally from `pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions._perform_plot_hairy_overlayed_position` -> `pyphocorehelpers.plotting.hairy_lines_plot._perform_plot_hairy_overlayed_position`

    Usage:

        from pyphoplacecellanalysis.General.Pipeline.Stages.ComputationFunctions.EpochComputationFunctions import _perform_plot_hairy_overlayed_position

        ## INPUTS: a_decoded_marginal_posterior_df

        ## plot the basic lap-positions (measured) over time figure:
        _out = dict()
        _out['_display_grid_bin_bounds_validation'] = curr_active_pipeline.display(display_function='_display_grid_bin_bounds_validation', active_session_configuration_context=None, include_includelist=[], save_figure=False) # _display_grid_bin_bounds_validation
        fig = _out['_display_grid_bin_bounds_validation'].figures[0]
        out_axes_list =_out['_display_grid_bin_bounds_validation'].axes
        out_plot_data =_out['_display_grid_bin_bounds_validation'].plot_data

        ## get the lines2D object to turn off the default position lines:
        position_lines_2D = out_plot_data['position_lines_2D']
        ## hide all inactive lines:
        for a_line in position_lines_2D:
            a_line.set_visible(False)


        an_pos_line_artist, df_viz = _perform_plot_hairy_overlayed_position(df=deepcopy(a_decoded_marginal_posterior_df), ax=out_axes_list[0], extreme_threshold=0.7) # , thickness_ramping_multiplier=5
        df_viz

        _out



        NOTE: Interesting thickness/opacity modulators:


        interesting_hair_parameter_kwarg_dict = {
            'defaults': dict(extreme_threshold=0.8, opacity_max=0.7, thickness_ramping_multiplier=35),
            '50_sec_window_scale': dict(extreme_threshold=0.5, thickness_ramping_multiplier=50),
        }


        #  prob_to_thickness_ramping_function= lambda p: max(0.0, (p - 0.5) * 15),
        #  extreme_threshold=0.9, prob_to_thickness_ramping_function= lambda p: 6.0, ## constant for all probabilities
        extreme_threshold=0.1, prob_to_thickness_ramping_function= lambda p: (5.0 * p), 


    """
    return HairyLinePlot.plot_hairy_overlayed_position(df=df, ax=ax, extreme_threshold=extreme_threshold, opacity_max=opacity_max, thickness_ramping_multiplier=thickness_ramping_multiplier, prob_to_thickness_ramping_function=prob_to_thickness_ramping_function, a_var_name_to_color_map=a_var_name_to_color_map, **kwargs)
    


