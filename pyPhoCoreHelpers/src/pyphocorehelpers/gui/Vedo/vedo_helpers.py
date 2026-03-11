import vedo
from vedo import Mesh, Cone, Plotter, printc, Glyph
from vedo import Rectangle, Lines, Plane, Axes, merge, colorMap # for StaticVedo_3DRasterHelper
from vedo import Volume, ProgressBar, show, settings


class VedoHelpers:
    """docstring for VedoHelpers.
    
    Import with:
    
        from pyphocorehelpers.gui.Vedo.vedo_helpers import VedoHelpers
    
    """

    @classmethod
    def recurrsively_get_use_bounds(cls, assembly_obj):
        """
        # should_use_bounds: a bool value indicating whether the root assembly_obj and all of its actors/children should use bounds or not
        
        Usage:
            print(f'for assembly object with {len(active_window_only_axes.actors)} child actors: assembly UseBounds: {active_window_only_axes.GetUseBounds()} and actors UseBounds: {recurrsively_get_use_bounds(active_window_only_axes)}')
            recurrsively_get_use_bounds(active_window_only_axes) 

        
        """
        return [an_actor.GetUseBounds() for an_actor in assembly_obj.actors]

    @classmethod
    def recurrsively_apply_use_bounds(cls, assembly_obj, should_use_bounds):
        """
        # should_use_bounds: a bool value indicating whether the root assembly_obj and all of its actors/children should use bounds or not
        
        Usage:
            recurrsively_apply_use_bounds(active_window_only_axes, False)
        
        """
        assembly_obj.useBounds(should_use_bounds) # apply to parent object
        # originally_was_use_bounds = [an_actor.GetUseBounds() for an_actor in assembly_obj.actors]
        for an_actor in assembly_obj.actors:
            an_actor.useBounds(should_use_bounds)
            
    @classmethod
    def vedo_get_camera_debug_info(cls, camera, enable_print=False):
        """ Prints the debug info for the passed in camera object.
        
        camera: should be a vedo camera object.
        
        Usage:
            vedo_get_camera_debug_info(spike_raster_plt_3d_vedo.plt.camera)
        
        """
        camera_debug_string = f'Camera:\n\tpos: {camera.GetPosition()}, distance: {camera.GetDistance()}, \n\t\tview_angle: {camera.GetViewAngle()}, roll: {camera.GetRoll()}, \n\t\torientation: {camera.GetOrientation()}'
        if enable_print:
            print(camera_debug_string)
        """ 
        Camera:
            pos: (66.24993092335596, -75.93948792238676, 25.07713824628677), distance: 81.07267779708857, 
                view_angle: 30.0, roll: -42.80457161107933, 
                orientation: (-73.35587868481223, -19.227674343471744, -42.80457161107933)
        """
        return camera_debug_string
    
