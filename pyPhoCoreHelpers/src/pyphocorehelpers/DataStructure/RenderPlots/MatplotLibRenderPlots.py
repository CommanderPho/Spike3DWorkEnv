from __future__ import annotations # prevents having to specify types for typehinting as strings
from typing import TYPE_CHECKING
from typing import Optional
from collections.abc import Iterable
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure, FigureBase # FigureBase: both Figure and SubFigure
from matplotlib.axes import Axes

from pyphocorehelpers.DataStructure.general_parameter_containers import RenderPlots
from pyphocorehelpers.programming_helpers import metadata_attributes
from pyphocorehelpers.function_helpers import function_attributes
from neuropy.utils.indexing_helpers import wrap_in_container_if_needed, unwrap_single_item, flatten_dict
from neuropy.utils.mixins.print_helpers import BaseFieldPrintingReprMixin


if TYPE_CHECKING:
    ## typehinting only imports here
    from pyphoplacecellanalysis.GUI.PyQtPlot.Widgets.ContainerBased.PhoContainerTool import GenericMatplotlibContainer


class MatplotlibRenderPlots(RenderPlots):
    """Container for holding and accessing Matplotlib-based figures for MatplotlibRenderPlots.
    Usage:
        from pyphocorehelpers.DataStructure.RenderPlots.MatplotLibRenderPlots import MatplotlibRenderPlots
    
    2023-05-30 - Updated to replace subplots.
    
    
    Also see `pyphoplacecellanalysis.GUI.PyQtPlot.Widgets.ContainerBased.PhoContainerTool.PhoBaseContainerTool` for higher-level usage
    
    
    """
    _display_library:str = 'matplotlib'
    
    def __init__(self, name='MatplotlibRenderPlots', figures=[], axes=[], context=None, **kwargs):
        figures = wrap_in_container_if_needed(figures)
        axes = wrap_in_container_if_needed(axes)
        super(MatplotlibRenderPlots, self).__init__(name, figures = figures, axes=axes, context=context, **kwargs)
        

    @property
    def num_figures(self) -> int:
        """The num_figures property."""
        return len(self.figures)

    @property
    def num_axes(self) -> int:
        """The num_axes property."""
        return len(self.axes)
    
    # Singular Accessors _________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________ #
    @property
    def fig(self):
        """The fig property."""
        if self.num_figures > 1:
            print(f'WARN: getting figure with the `a_fig = MatplotlibRenderPlots.fig` shortcut, but container has num_figures: {self.num_figures} figures; WARN: ONLY THE FIRST WILL BE RETURNED!')
        return unwrap_single_item(self.figures)
    @fig.setter
    def fig(self, value):
        num_curr_figures: int = len(self.figures)
        wrapped_fig = wrap_in_container_if_needed(value)
        num_proposed_figures: int = len(wrapped_fig)
        if num_curr_figures > num_proposed_figures:
            raise ValueError(f'tried to set figures with the `MatplotlibRenderPlots.fig = a_fig` shortcut, but already had num_curr_figures: {num_curr_figures} figures, which is longer than num_proposed_figures: {num_proposed_figures}!')
        self.figures = wrapped_fig


    @property
    def ax(self):
        """The ax property."""
        if self.num_axes > 1:
            print(f'WARN: getting axes with the `an_ax = MatplotlibRenderPlots.ax` shortcut, but container has num_axes: {self.num_axes} axes; WARN: ONLY THE FIRST WILL BE RETURNED!')
        return unwrap_single_item(self.axes)
    @ax.setter
    def ax(self, value):
        num_curr_axes: int = self.num_axes
        wrapped_ax = wrap_in_container_if_needed(value)
        num_proposed_axes: int = len(wrapped_ax)
        if num_curr_axes > num_proposed_axes:
            raise ValueError(f'tried to set axes with the `MatplotlibRenderPlots.ax = an_ax` shortcut, but already had num_curr_axes: {num_curr_axes} axes, which is longer than num_proposed_axes: {num_proposed_axes}!')
        self.axes = wrapped_ax



    @classmethod
    def init_from_any_objects(cls, *args, name: Optional[str] = None, **kwargs):
        """ initializes a MatplotlibRenderPlots instance from any list containing Matplotlib objects (figures, axes, artists, contexts, etc).
        
        For the most base functionality we really only need the figures and axes. 

        """
        figures = []
        axes = [] # would make way more sense if we had a list of axes for each figure, and a list of Artists for each axes, etc. But this is a start.
        
        for obj in args:
            #TODO 2024-12-04 11:59: - [ ] Requires a flat object hierarchy
            if isinstance(obj, FigureBase): # .Figure or .SubFigure
                figures.append(obj)
            elif isinstance(obj, Axes):
                axes.append(obj)
            # Add more elif blocks for other types if needed
        return cls(name=name, figures=figures, axes=axes)


    @classmethod
    def init_subplots(cls, *args, **kwargs):
        """ wraps the matplotlib.plt.subplots(...) command to initialize a new object with custom subplots. 
        2023-05-30 - Should this be here ideally? Is there a better class? I remember a MATPLOTLIB
        """
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(*args, **kwargs)
        # check for scalar axes and wrap it in a tuple if needed before setting self.
        return cls(figures=[fig], axes=axes)


    def __add__(self, other):
        
        # Combine figures and axes from self and other MatplotlibRenderPlots instances
        # combined_figures = self.figures + other.figures
        # combined_axes = self.axes + other.axes

        for k, v in other.data_items():
            if k not in self.data_keys:
                # unique to other, add it as a property to self
                self[k] = v 
            else:
                # present in both
                if (self[k] == v):
                    ## v already included, don't double it up
                    pass
                elif isinstance(self[k], Iterable) and (v in self[k]):
                    ## also included
                    pass
                else:
                    self[k] = self[k] + v  ## append or w/e

        return self ## return the updated self
    
    



@function_attributes(short_name=None, tags=['collector', 'figure', 'output', 'matplotlib'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-06-05 17:27', related_items=['plotting.figure_management.PhoActiveFigureManager2D'])
class FigureCollector(BaseFieldPrintingReprMixin):
    """ 2023-12-27 - Very useful context-manger helper for capturing matplotlib figures, axes, and other outputs.
    
    
    from pyphocorehelpers.DataStructure.RenderPlots.MatplotLibRenderPlots import FigureCollector
    
    Specifically a Matplotlib thing: .create_figure(...), .subplots(...), .subplot_mosaic(...) are alternatives to the matplotlib functions of the same names but they keep track of the outputs for later use.
    

    """
    def __init__(self, name='MatplotlibRenderPlots', figures=None, axes=None, axes_dict=None, contexts=None, base_context=None):
        self.name = name
        self.figures = figures or []
        self.axes = axes or []
        self.axes_dict = axes_dict or {} # advanced axes support
        self.contexts = contexts or []
        self.base_context = base_context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Cleanup code, if needed
        pass


    # Main Matplotlib-based Helper Functions _____________________________________________________________________________ #

    def create_figure(self, *args, **kwargs):
        fig = plt.figure(*args, **kwargs)
        self.figures.append(fig)
        return fig
    

    def build_or_reuse_figure(self, fignum=1, fig=None, fig_idx:int=0, **kwargs):
        """ Reuses a Matplotlib figure if it exists, or creates a new one if needed
        Inputs:
            fignum - an int or str that identifies a figure
            fig - an existing Matplotlib figure
            fig_idx:int - an index to identify this figure as part of a series of related figures, e.g. plot_pf_1D[0], plot_pf_1D[1], ... 
            **kwargs - are passed as kwargs to the plt.figure(...) command when creating a new figure
        Outputs:
            fig: a Matplotlib figure object

        History: factored out of `plot_ratemap_2D`

        Usage:
            from neuropy.utils.matplotlib_helpers import build_or_reuse_figure
            
        Example 1:
            ## Figure Setup:
            fig = build_or_reuse_figure(fignum=kwargs.pop('fignum', None), fig=kwargs.pop('fig', None), fig_idx=kwargs.pop('fig_idx', 0), figsize=kwargs.pop('figsize', (10, 4)), dpi=kwargs.pop('dpi', None), constrained_layout=True) # , clear=True
            subfigs = fig.subfigures(actual_num_subfigures, 1, wspace=0.07)
            ##########################

        Example 2:
            
            if fignum is None:
                if f := plt.get_fignums():
                    fignum = f[-1] + 1
                else:
                    fignum = 1

            ## Figure Setup:
            if ax is None:
                fig = build_or_reuse_figure(fignum=fignum, fig=fig, fig_idx=0, figsize=(12, 4.2), dpi=None, clear=True, tight_layout=False)
                gs = GridSpec(1, 1, figure=fig)

                if use_brokenaxes_method:
                    # `brokenaxes` method: DOES NOT YET WORK!
                    from brokenaxes import brokenaxes ## Main brokenaxes import 
                    pad_size: float = 0.1
                    # [(a_tuple.start, a_tuple.stop) for a_tuple in a_test_epoch_df.itertuples(index=False, name="EpochTuple")]
                    lap_start_stop_tuples_list = [((a_tuple.start - pad_size), (a_tuple.stop + pad_size)) for a_tuple in ensure_dataframe(laps_Epoch_obj).itertuples(index=False, name="EpochTuple")]
                    # ax = brokenaxes(xlims=((0, .1), (.4, .7)), ylims=((-1, .7), (.79, 1)), hspace=.05, subplot_spec=gs[0])
                    ax = brokenaxes(xlims=lap_start_stop_tuples_list, hspace=.05, subplot_spec=gs[0])
                else:
                    ax = plt.subplot(gs[0])

            else:
                # otherwise get the figure from the passed axis
                fig = ax.get_figure()
                        
                
        """
        if fignum is None:
            if f := plt.get_fignums():
                fignum = f[-1] + 1
            else:
                fignum = 1

        ## Figure Setup:
        if fig is not None:
            # provided figure
            extant_fig = fig
        else:
            extant_fig = None # is this okay?
            
        if fig is not None:
            # provided figure
            active_fig_id = fig
        else:
            if isinstance(fignum, int):
                # a numeric fignum that can be incremented
                active_fig_id = fignum + fig_idx
            elif isinstance(fignum, str):
                # a string-type fignum.
                # TODO: deal with inadvertant reuse of figure? perhaps by appending f'{fignum}[{fig_ind}]'
                if fig_idx > 0:
                    active_fig_id = f'{fignum}[{fig_idx}]'
                else:
                    active_fig_id = fignum
            else:
                raise NotImplementedError
        
        if extant_fig is None:
            # fig = plt.figure(active_fig_id, **({'dpi': None, 'clear': True} | kwargs)) # , 'tight_layout': False - had to remove 'tight_layout': False because it can't coexist with 'constrained_layout'
            fig = self.create_figure(active_fig_id, **({'dpi': None, 'clear': True} | kwargs))
            #  UserWarning: The Figure parameters 'tight_layout' and 'constrained_layout' cannot be used together.
        else:
            fig = extant_fig
            if fig not in self.figures:
                # if the fig exists but was created externally, add it to the list of figures. Note that we might be missing its existing axes then...
                print(f'fig exists but was created externally, add it to the list of figures')
                self.figures.append(fig)
                for ax in fig.get_axes():
                    if (ax not in self.axes) and (ax not in self.axes.values()):
                        self.axes.append(ax)
                        # not sure if this logic is air-tight

        return fig
                
    def create_subfigures(self, fig, nrows=1, ncols=1, squeeze=True, **kwargs): # -> (NDArray | SubFigure):
        """ replaces fig.subfigures(nrows=1, ncols=4) 
        """
        _subfigures = fig.subfigures(nrows=nrows, ncols=ncols, squeeze=squeeze, **kwargs)
        # for i in range(ncols):
            # for j in range(nrows):
        for a_subfigure in _subfigures:
            self.figures.append(a_subfigure)
        
        return _subfigures
        
            
    def subplots(self, *args, **kwargs):
        """ 
        (function) def subplots(
            nrows: int = 1,
            ncols: int = 1,
            *,
            sharex: bool | Literal['none', 'all', 'row', 'col'] = False,
            sharey: bool | Literal['none', 'all', 'row', 'col'] = False,
            squeeze: bool = True,
            width_ratios: Sequence[float] | None = None,
            height_ratios: Sequence[float] | None = None,
            subplot_kw: dict[str, Any] | None = None,
            gridspec_kw: dict[str, Any] | None = None,
            **fig_kw: Unknown
        ) -> tuple[Figure, Any]

        """    
        fig, axes = plt.subplots(*args, **kwargs) # tuple[Figure, np.ndarray] or tuple[Figure, Axes]

        # fig = figure(**fig_kw)
        # axs = fig.subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey,
        #                 squeeze=squeeze, subplot_kw=subplot_kw,
        #                 gridspec_kw=gridspec_kw, height_ratios=height_ratios,
        #                 width_ratios=width_ratios)

        self.figures.append(fig)
        if isinstance(axes, Axes):
            self.axes.append(axes) # single scalar axis
        else:
            for ax in axes:
                self.axes.append(ax)
        return fig, axes

    def subplot_mosaic(self, *args, extant_fig=None, **kwargs):
        """ emulates matplotlib's fig.subplot_mosaic(...) function
            def subplot_mosaic(
                mosaic: list[HashableList[_T@subplot_mosaic]],
                *,
                sharex: bool = ...,
                sharey: bool = ...,
                width_ratios: ArrayLike | None = ...,
                height_ratios: ArrayLike | None = ...,
                empty_sentinel: _T@subplot_mosaic = ...,
                subplot_kw: dict[str, Any] | None = ...,
                per_subplot_kw: dict[_T@subplot_mosaic | tuple[_T@subplot_mosaic, ...], dict[str, Any]] | None = ...,
                gridspec_kw: dict[str, Any] | None = ...
            ) -> dict[_T@subplot_mosaic, Axes]
            Build a layout of Axes based on ASCII art or nested lists.

            This is a helper function to build complex GridSpec layouts visually.

            See mosaic for an example and full API documentation

            Parameters
            mosaic : list of list of {hashable or nested} or str

                A visual layout of how you want your Axes to be arranged labeled as strings. For example

                x = [['A panel', 'A panel', 'edge'],
                        ['C panel', '.',       'edge']]
                produces 4 Axes:

            'A panel' which is 1 row high and spans the first two columns
            'edge' which is 2 rows high and is on the right edge
            'C panel' which in 1 row and 1 column wide in the bottom left
            a blank space 1 row and 1 column wide in the bottom center
                Any of the entries in the layout can be a list of lists of the same form to create nested layouts.

                If input is a str, then it can either be a multi-line string of the form

                '''
                AAE
                C.E
                '''
                where each character is a column and each line is a row. Or it can be a single-line string where rows are separated by ;:

                'AB;CC'
                The string notation allows only single character Axes labels and does not support nesting but is very terse.

                The Axes identifiers may be str or a non-iterable hashable object (e.g. tuple s may not be used).

            sharex, sharey : bool, default: False
                If True, the x-axis (*sharex*) or y-axis (*sharey*) will be shared among all subplots. In that case, tick label visibility and axis units behave as for subplots. If False, each subplot's x- or y-axis will be independent.

            width_ratios : array-like of length *ncols*, optional
                Defines the relative widths of the columns. Each column gets a relative width of width_ratios[i] / sum(width_ratios). If not given, all columns will have the same width. Equivalent to gridspec_kw={'width_ratios': [...]}. In the case of nested layouts, this argument applies only to the outer layout.

            height_ratios : array-like of length *nrows*, optional
                Defines the relative heights of the rows. Each row gets a relative height of height_ratios[i] / sum(height_ratios). If not given, all rows will have the same height. Equivalent to gridspec_kw={'height_ratios': [...]}. In the case of nested layouts, this argument applies only to the outer layout.

            subplot_kw : dict, optional
                Dictionary with keywords passed to the .Figure.add_subplot call used to create each subplot. These values may be overridden by values in *per_subplot_kw*.

            per_subplot_kw : dict, optional
                A dictionary mapping the Axes identifiers or tuples of identifiers to a dictionary of keyword arguments to be passed to the .Figure.add_subplot call used to create each subplot. The values in these dictionaries have precedence over the values in *subplot_kw*.

                If *mosaic* is a string, and thus all keys are single characters, it is possible to use a single string instead of a tuple as keys; i.e. "AB" is equivalent to ("A", "B").

            gridspec_kw : dict, optional
                Dictionary with keywords passed to the .GridSpec constructor used to create the grid the subplots are placed on. In the case of nested layouts, this argument applies only to the outer layout. For more complex layouts, users should use .Figure.subfigures to create the nesting.

            empty_sentinel : object, optional
                Entry in the layout to mean "leave this space empty". Defaults to '.'. Note, if *layout* is a string, it is processed via inspect.cleandoc to remove leading white space, which may interfere with using white-space as the empty sentinel.

            Returns
            dict[label, Axes]
            A dictionary mapping the labels to the Axes objects. The order of the axes is left-to-right and top-to-bottom of their position in the total layout.
            
        """
        fig_kw = kwargs.pop('fig_kw', dict()) # empty dict by default
        # extant_fig = kwargs.pop('extant_fig', None)
        if extant_fig is None:
            fig = plt.figure(**fig_kw) # layout="constrained"
            self.figures.append(fig)
        else:
            fig = extant_fig
            if fig not in self.figures:
                self.figures.append(fig)

        ## subplot_mosaic
        ax_dict = fig.subplot_mosaic(*args, **kwargs) # dict[label, Axes]
        assert len(self.figures) == 1, f"requires only one figure because self.axes_dict is flat"
        self.axes_dict = ax_dict
        self.axes = [v for k, v in self.axes_dict.items() if isinstance(v, Axes)] # flat axes
        assert len(self.axes) == len(self.axes_dict), f"all axes_dict entries should be of type Axes, so should be added to the flat self.axes."
        return fig, ax_dict

    def post_hoc_append_container(self, a_container: Union[GenericMatplotlibContainer, MatplotlibRenderPlots]):
        return self.post_hoc_append(figs=[a_container.fig], axes=(a_container.ax_dict or a_container.axes), contexts=[(a_container.plots.context or None)])
    

    def post_hoc_append(self, figs, axes, contexts=None):
        """ can be used to add new figures/axes that were generated by a different function after the fact. 

        """
        if isinstance(figs, FigureBase):
            self.figures.append(figs) # single scalar Figure
        else:
            for fig in figs:
                self.figures.append(fig)
                        
        if isinstance(axes, Axes):
            self.axes.append(axes) # single scalar axis
        else:
            if isinstance(axes, dict):
                ## axes dict
                axes_dict = axes
                ## recursively expand self.axes_dict to get flat axes list
                flattened_axes_list = list(flatten_dict(axes_dict).values())
                for ax in flattened_axes_list:
                    self.axes.append(ax)
                if self.axes_dict is None:
                    self.axes_dict = axes_dict
                else:
                    self.axes_dict = self.axes_dict | axes_dict
                    ## TODO: warn about replacing
                    
            else:
                ## list/tuple/etc
                for ax in axes:
                    self.axes.append(ax)
                
        if (contexts is not None) and (not isinstance(contexts, (list, tuple, dict))):
            self.contexts.append(contexts) # single scalar Figure
        else:
            for ctxt in contexts:
                self.contexts.append(ctxt)



# #TODO 2023-12-23 22:01: - [ ] Context-determining figure
# class ContextCollectingFigureCollector(FigureCollector):
#     """ 
#     from pyphocorehelpers.DataStructure.RenderPlots.MatplotLibRenderPlots import FigureCollector
    
    
#     """
#     def __init__(self, name='ContextCollectingFigureCollector', figures=None, axes=None, context=None, context_list=None):
#         ## TODO: store specific properties:
#         self.context_list = context_list or []
#         super().__init__(name=name, figures=figures, axes=axes, context=context)
        

#     def create_figure(self, *args, **kwargs):
#         fig = plt.figure(*args, **kwargs)
#         self.figures.append(fig)
#         return fig
    
#     def subplots(self, *args, **kwargs):
#         sub_name = kwargs.pop('name', None) # 'name' is not a valid argument to plt.subplots anyway.
#         if sub_name is None:
#             # try to get subname from one of the other parameters:
#             num_name = kwargs.get('num', None)
#             sub_name = num_name or ""
               
#         if sub_name is not None:
#             if self.context is not None:
#                 # self.context.
#                 sub_context = self.context.
#             else:
#                 sub_context = IdentifyingContext(sub_name=sub_name)
#                 sub_context.adding_context_if_missing(sub_name=sub_name)
                                
#         fig, axes = plt.subplots(*args, **kwargs) # tuple[Figure, np.ndarray] or tuple[Figure, Axes]
#         self.figures.append(fig)
#         if isinstance(axes, Axes):
#             self.axes.append(axes) # single scalar axis
#         else:
#             for ax in axes:
#                 self.axes.append(ax)
#         return fig, axes
    



#TODO 2023-12-13 00:57: - [ ] Custom Figure (TODO)

@metadata_attributes(short_name=None, tags=['not-yet-implemented', 'matplotlib', 'figure'], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2023-12-13 00:56', related_items=[])
class MatplotlibRenderPlotsFigure(Figure):
    """A figure with emedded data/functions/etc.
    
    
    from pyphocorehelpers.DataStructure.RenderPlots.MatplotLibRenderPlots import MatplotlibRenderPlotsFigure
    
    """

    def __init__(self, *args, name='MatplotlibRenderPlots', figures=[], axes=[], context=None, watermark=None, **kwargs):
        super().__init__(name, *args, figures=figures, axes=axes, context=context, **kwargs) # is this right or do I set them somewhere else?

        # if watermark is not None:
        #     bbox = dict(boxstyle='square', lw=3, ec='gray',
        #                 fc=(0.9, 0.9, .9, .5), alpha=0.5)
        #     self.text(0.5, 0.5, watermark,
        #               ha='center', va='center', rotation=30,
        #               fontsize=40, color='gray', alpha=0.5, bbox=bbox)



"""
from pyphocorehelpers.DataStructure.RenderPlots.MatplotLibRenderPlots import MatplotlibRenderPlotsFigure

x = np.linspace(-3, 3, 201)
y = np.tanh(x) + 0.1 * np.cos(5 * x)

plt.figure(FigureClass=MatplotlibRenderPlotsFigure, watermark='draft')
plt.plot(x, y)
"""

