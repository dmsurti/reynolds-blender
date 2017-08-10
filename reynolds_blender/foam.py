#------------------------------------------------------------------------------
# Reynolds-Blender | The Blender add-on for Reynolds, an OpenFoam toolbox.
#------------------------------------------------------------------------------
# Copyright|
#------------------------------------------------------------------------------
#     Deepak Surti       (dmsurti@gmail.com)
#     Prabhu R           (IIT Bombay, prabhu@aero.iitb.ac.in)
#     Shivasubramanian G (IIT Bombay, sgopalak@iitb.ac.in)
#------------------------------------------------------------------------------
# License
#
#     This file is part of reynolds-blender.
#
#     reynolds-blender is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     reynolds-blender is distributed in the hope that it will be useful, but
#     WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#     Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with reynolds-blender.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

# -----------
# bpy imports
# -----------
import bpy
from bpy.types import (Panel,
                       PropertyGroup)
from bpy.props import StringProperty, BoolProperty


from progress_report import ProgressReport

# ------------------------
# reynolds blender imports
# ------------------------

from reynolds_blender.gui.register import register_classes, unregister_classes
from reynolds_blender.gui.renderer import ReynoldsGUIRenderer

# ---------------
# reynolds imports
# ----------------
from reynolds.foam.start import FoamRunner

class BMDStartOpenFoamOperator(bpy.types.Operator):
    bl_idname = "reynolds.start_of"
    bl_label = "Start OpenFoam"

    def execute(self, context):
        scene = context.scene
        obj = context.active_object

        print("Start openfoam")

        fr = FoamRunner()

        if fr.start():
            self.report({'INFO'}, 'OpenFoam started: SUCCESS')
        else:
            self.report({'INFO'}, 'OpenFoam started: FAILED')

        return{'FINISHED'}

class FoamPanel(Panel):
    bl_idname = "of_foam_panel"
    bl_label = "Open Foam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"
    bl_context = "mesh_edit"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # -------------------------------------
        # Render Foam Panel using YAML GUI Spec
        # -------------------------------------

        gui_renderer = ReynoldsGUIRenderer(scene, layout, 'foam_panel.yaml')
        gui_renderer.render()

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    register_classes(__name__)

def unregister():
    unregister_classes(__name__)

if __name__ == '__main__':
    register()
