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
import bpy, bmesh

# --------------
# python imports
# --------------
import os
import pathlib
import unittest

# ------------------------
# reynolds_blender imports
# ------------------------
from reynolds_blender import bl_info
from tests.foam_test_case import TestFoamTutorial

class TestFlangeTutorial(TestFoamTutorial):
    def setUp(self):
        super(TestFlangeTutorial, self).setUp()
        self.create_tutorial_case_dir('flange')
        self.scene = bpy.context.scene

    def _add_flange_trisurface(self):
        print(' add flange stl file: ' + os.path.join(self.current_dir, 'tests', 'tutorials', 'resources', 'flange.stl'))
        self.scene.stl_file_path = os.path.join(self.current_dir, 'tests', 'tutorials', 'resources', 'flange.stl')
        bpy.ops.reynolds.import_stl()
        self.assertIsNotNone(self.scene.geometries['Flange'])

    def _add_refine_hole(self):
        self.scene.sphere_name = 'refineHole'
        self.scene.sphere_radius = 0.0030
        self.scene.sphere_location[0] = 0
        self.scene.sphere_location[1] = -0.012
        self.scene.sphere_location[2] = 0
        bpy.ops.reynolds.add_searchable_sphere()

    def _add_blockmesh_to_flange_trisurface(self):
        bpy.ops.object.select_all(False)
        flange_obj = self.scene.objects['Flange']
        self.scene.objects.active = flange_obj
        bpy.ops.reynolds.add_geometry_block()
        self.assertIsNotNone(self.scene.objects['Cube'])
        blockmesh_obj = self.scene.objects['Cube']
        bpy.ops.object.select_all(False)
        self.scene.block_cells_pg.convert_to_meters = 1
        self.set_number_of_cells(20, 20, 20)
        self.set_grading(1, 1, 1)
        patches = {'patch1': (['Back'], 'patch', {'T': {'type': 'zeroGradient'}}),
                   'patch2': (['Front'], 'patch', {'T': {'type': 'fixedValue', 'value': 'uniform 273'}}),
                   'patch3': (['Top', 'Bottom'], 'patch', {'T': {'type': 'zeroGradient'}}),
                   'patch4': (['Left', 'Right'], 'patch', {'T': {'type': 'fixedValue', 'value': 'uniform 573'}})}
        self.select_boundary(blockmesh_obj, patches)
        self.generate_blockmeshdict()
        self.run_blockmesh()

    def _add_flange_trisurface_geometry(self):
        flange_obj = self.scene.objects['Flange']
        self.scene.objects.active = flange_obj
        self.scene.geometry_type = 'triSurfaceMesh'
        self.scene.refinement_type = 'Surface'
        self.scene.refinement_level_min = 2
        self.scene.refinement_level_max = 2
        self.scene.has_features = True
        self.scene.feature_extract_included_angle = 150.0
        self.scene.feature_extract_ref_level = 0
        bpy.ops.shmd_geometries.list_action('INVOKE_DEFAULT', action='ADD')
        bpy.ops.reynolds.assign_shmd_geometry()
        self.assertEqual(self.scene.geometries['Flange']['type'],
                         'triSurfaceMesh')
        self.assertEqual(self.scene.geometries['Flange']['refinement_type'],
                         'Surface')
        self.assertEqual(self.scene.geometries['Flange']['refinementSurface']
                         ['min'], 2)
        self.assertEqual(self.scene.geometries['Flange']['refinementSurface']
                         ['max'], 2)
        self.assertTrue(self.scene.geometries['Flange']['has_features'])
        self.assertEqual(self.scene.geometries['Flange']['included_angle'],
                         150.0)
        self.assertEqual(self.scene.geometries['Flange']['feature_level'], 0)

        # we now add time props for geo patches as well
        patches = {'flange_patch1': {'T': {'type': 'zeroGradient'}},
                   'flange_patch2': {'T': {'type': 'fixedValue', 'value': 'uniform 273'}},
                   'flange_patch3': {'T': {'type': 'zeroGradient'}},
                   'flange_patch4': {'T': {'type': 'fixedValue', 'value': 'uniform 573'}}}
        self._initialize_T()

        # we first load the geo patches and then assign time props
        bpy.ops.reynolds.load_geo_patch_objs()
        # now select one geo patch a time and add time property
        for i in range(len(self.scene.geo_patches.keys())):
            self.scene.geo_patch_rindex = i
            geo_patch = self.scene.geo_patch_objs[self.scene.geo_patch_rindex]
            print(' Will now assign props for geo patch: ' + geo_patch.name)
            time_prop_info = patches[geo_patch.name]
            for prop_type, props in time_prop_info.items():
                print(' Will now assign props for time prop : ' + prop_type)
                print( props )
                self.scene.time_prop_type = prop_type
                for k, val in props.items():
                    if k == 'type':
                        self.scene.time_prop_patch_type = val
                    if k == 'value':
                        self.scene.time_prop_value = val
                if 'value' not in props:
                    self.scene.time_prop_value = ""
                bpy.ops.reynolds.add_geo_patch_time_prop()

        self.generate_time_props()

    def _add_refine_hole_geometry(self):
        self.scene.objects.active = None
        sphere = self.scene.objects['refineHole']
        bpy.context.scene.objects.active = sphere
        self.scene.geometry_type = 'searchableSphere'
        self.scene.refinement_type = 'Region'
        self.scene.refinement_mode = 'inside'
        self.scene.ref_reg_dist = 1e15
        self.scene.ref_reg_level = 3
        self.scene.has_features = False
        bpy.ops.shmd_geometries.list_action('INVOKE_DEFAULT', action='ADD')
        bpy.ops.reynolds.assign_shmd_geometry()
        self.assertIsNotNone(self.scene.geometries['refineHole'])
        self.assertEqual(self.scene.geometries['refineHole']['type'],
                         'searchableSphere')
        self.assertEqual(self.scene.geometries['refineHole']['refinement_type'],
                         'Region')
        self.assertAlmostEqual(self.scene.geometries['refineHole']['radius'],
                               0.00300000014)
        self.assertEqual(self.scene.geometries['refineHole']['refinementRegion']['mode'],
                         'inside')
        self.assertEqual(self.scene.geometries['refineHole']['refinementRegion']['level'], 3)
        self.assertAlmostEqual(self.scene.geometries['refineHole']['refinementRegion']['dist'],
                               999999986991104.0)

    def _mark_location_in_space(self):
        self.scene.location_in_mesh = [-9.23149e-05, -0.0025, -0.0025]

    def _generate_surface_features(self):
        bpy.ops.reynolds.generate_surface_dict()
        bpy.ops.reynolds.extract_surface_features()

    def _set_castellated_mesh_controls(self):
        self.scene.max_local_cells = 100000
        self.scene.max_global_cells = 2000000
        self.scene.min_refinement_cells = 0
        self.scene.max_load_unbalance = 0.0
        self.scene.n_cells_between_levels = 1
        self.scene.resolve_feature_angle = 30
        self.allow_free_standing_zones = True

    def _set_snapping_controls(self):
        self.scene.tolerance = 1
        self.scene.n_smooth_patch_iter = 3
        self.scene.disp_relax_iter = 300
        self.scene.snapping_relax_iter = 5
        self.scene.feature_edge_snapping_iter = 10
        self.scene.implicit_feature_snap = False
        self.scene.explicit_feature_snap = True
        self.scene.multi_region_feature_snap = True

    def _set_layers_controls(self):
        self.scene.relative_sizes = True
        self.scene.layer_name = '"flange_.*"'
        self.scene.n_surface_layers = 1
        bpy.ops.shmd_layers.list_action('INVOKE_DEFAULT', action='ADD')
        bpy.ops.reynolds.assign_layer()
        self.assertIsNotNone(self.scene.add_layers['"flange_.*"'])
        self.assertEqual(self.scene.add_layers['"flange_.*"'], 1)
        self.scene.expansion_ratio = 1
        self.scene.final_layer_thickness = 0.3
        self.scene.min_layer_thickness = 0.25
        self.scene.n_grow_layers = 0
        self.scene.layer_feature_angle = 30
        self.scene.smooth_layer_thickness = 10
        self.scene.max_face_thickness_ratio = 0.5
        self.scene.max_thickness_to_medial_ratio = 0.3
        self.scene.min_median_axis_angle = 90
        self.scene.n_buffer_cells_no_extrude = 0

    def _set_mesh_quality_controls(self):
        self.scene.max_internal_face_skewness = 4
        self.scene.min_pyramid_vol = 1e-13
        self.scene.min_tetrahedral_quality = 1e-15
        self.scene.min_face_twist = 0.02

    def _generate_snappyhexmeshdict(self):
        bpy.ops.reynolds.generate_shmd()

    def _run_snappyhexmesh(self):
        bpy.ops.reynolds.snappy_hexmesh_runner()

    def _generate_fv_schemes(self):
        self.scene.ddt_schemes_default = 'Euler'
        self.scene.grad_schemes_default = 'Gauss linear'
        self.scene.grad_schemes_grad_T = 'Gauss linear'
        self.scene.div_schemes_default = 'none'
        self.scene.lap_schemes_default = 'none'
        self.scene.lap_schemes_dt_t = 'Gauss linear corrected'
        self.scene.interp_schemes_default = 'linear'
        self.scene.sngrad_schemes_default = 'corrected'
        self.scene.flux_required_default = 'no'
        self.scene.flux_required_t = 'no'
        bpy.ops.reynolds.of_fvschemes()

    def _generate_fv_solution(self):
        self.scene.solvers_T_solver = 'PCG'
        self.scene.solvers_T_preconditioner = 'DIC'
        self.scene.solvers_T_tolerance = 1e-06
        self.scene.solvers_T_relTol = 0
        self.scene.simple_nNonOrthogonalCorrectors = 2
        bpy.ops.reynolds.of_fvsolutionop()

    def _generate_controldict(self):
        self.scene.cd_start_from = 'latestTime'
        self.scene.cd_start_time = 0
        self.scene.cd_stop_at = 'endTime'
        self.scene.cd_end_time = 3
        self.scene.cd_delta_time = 0.005
        self.scene.cd_write_control = 'runTime'
        self.scene.cd_write_interval = 0.1
        self.scene.cd_purge_write = 0
        self.scene.cd_write_format = 'ascii'
        self.scene.cd_write_precision = 6
        self.scene.cd_write_compression = 'off'
        self.scene.cd_time_format = 'general'
        self.scene.cd_time_precision = 6
        self.scene.cd_runtime_modifiable = True
        bpy.ops.reynolds.of_controldict()

    def _generate_transport_properties(self):
        self.scene.tp_dt_scalar_elt1 = '[ 0 2 -1 0 0 0 0]'
        self.scene.tp_dt_scalar_elt2 = 4e-05
        bpy.ops.reynolds.of_transportproperties()

    def _initialize_T(self):
        self.scene.time_props_dimensions['T'] = '[ 0 0 0 1 0 0 0 ]'
        self.scene.time_props_internal_field['T'] = 'uniform 273'

    def test_snappyhexmesh_with_flange_tutorial(self):
        # --------------
        # Initialization
        # --------------
        self.check_addon_loaded()
        self.start_openfoam()
        # -------------------
        # Configure case
        # -------------------
        self.select_case_dir(self.temp_tutorial_dir)
        self.set_solver_name('laplacianFoam')
        self._generate_fv_schemes()
        self._generate_fv_solution()
        self._generate_controldict()
        self._generate_transport_properties()
        # -------------------
        # Steps to solve case
        # -------------------
        self._add_flange_trisurface()
        self._add_refine_hole()
        self._add_blockmesh_to_flange_trisurface()
        self._add_flange_trisurface_geometry()
        self._add_refine_hole_geometry()
        self._mark_location_in_space()
        self._generate_surface_features()
        self._set_castellated_mesh_controls()
        self._set_snapping_controls()
        self._set_layers_controls()
        self._generate_snappyhexmeshdict()
        self._run_snappyhexmesh()
        self.solve_case('laplacianFoam');
        self.assertTrue(self.scene.case_solved)
        bpy.ops.wm.save_mainfile()

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFlangeTutorial)
unittest.TextTestRunner().run(suite)
