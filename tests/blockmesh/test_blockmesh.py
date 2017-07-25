import os
import unittest

import reynolds_blender

import bpy, bmesh

class TestBlockMesh(unittest.TestCase):
    def test_blockmesh_with_cavity_tutorial(self):
        # test if addon got loaded correctly
        # every addon must provide the "bl_info" dict
        self.assertIsNotNone(reynolds_blender.bl_info)

        # -------------
        # get the scene
        # -------------
        scene = bpy.context.scene

        # --------------
        # start openfoam
        # --------------
        bpy.ops.reynolds.start_of()

        # -------------------
        # switch to edit mode
        # -------------------
        obj = scene.objects['Plane']
        scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        # --------------------
        # select case directory
        # --------------------
        case_info_tool = scene.case_info_tool
        # use blender path format, the addon converts to abs path
        case_info_tool.case_dir_path = '//cavity'

        # ------------------
        # set convertToMeters
        # -------------------
        bmd_tool = scene.bmd_tool
        bmd_tool.convert_to_meters = 0.1

        # -------------------------------------------------------------
        # assign vertices with indices: 0, 1, 3, 2, 4, 5, 7, 6 in order
        # -------------------------------------------------------------
        bpy.ops.mesh.select_all(action='DESELECT')

        # ------------------------------------------------
        # Why is ensure_lookup_table() needed?
        # See https://developer.blender.org/rB785b90d7efd0
        # ------------------------------------------------

        bpy.ops.mesh.select_mode(type='VERT')
        for idx in  [0, 1, 3, 2, 4, 5, 7, 6]:
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.verts.ensure_lookup_table()
            vertices = mesh.verts
            vertices[idx].select = True
            bpy.ops.vertices.list_action('EXEC_DEFAULT', action='ADD')
            bpy.ops.reynolds.assign_vertex()
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.verts.ensure_lookup_table()
            vertices = mesh.verts
            vertices[idx].select = False

        # -----------------------------------------------
        # select all vertices in edit mode, assign blocks
        # -----------------------------------------------
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.reynolds.blocks()
        bpy.ops.mesh.select_all(action='DESELECT')

        # -------------------
        # set number of cells
        # -------------------
        scene.bmd_tool.n_cells[0] = 20
        scene.bmd_tool.n_cells[1] = 20
        scene.bmd_tool.n_cells[2] = 1

        # -------------------------
        # set cell expansion ratios
        # -------------------------
        scene.bmd_tool.n_grading[0] = 1
        scene.bmd_tool.n_grading[1] = 1
        scene.bmd_tool.n_grading[2] = 1

        # -----------------------------------------------------------------
        # set boundary
        # 1. select face with index 4 as movingWall, set name, type
        # 2. select face with index 3, 5, 2 as fixedWalls, set name, type
        # 3. select faces with indices 0, 1 as frontAndBack, set name, type
        # -----------------------------------------------------------------
        bpy.ops.mesh.select_mode(type='FACE')
        patches = {'movingWall': ([4], 'wall'),
                    'fixedWalls': ([3, 5, 2], 'wall'),
                    'frontAndBack': ([0, 1], 'empty')}
        for name, (faces, type) in patches.items():
            scene.bmd_tool.region_name = name
            scene.bmd_tool.region_type = type
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.faces.ensure_lookup_table()
            for f in faces:
                mesh.faces[f].select = True
            bpy.ops.regions.list_action('INVOKE_DEFAULT', action='ADD')
            bpy.ops.reynolds.assign_region()
            mesh = bmesh.from_edit_mesh(obj.data)
            mesh.faces.ensure_lookup_table()
            for f in faces:
                mesh.faces[f].select = False

        # ----------------------
        # generate blockMeshDict
        # ----------------------
        bpy.ops.reynolds.generate_bmd()

        # ---------------------
        # run blockMesh command
        # ---------------------
        bpy.ops.reynolds.block_mesh_runner()

        # ---------------
        # set solver name
        # ---------------
        case_info_tool.solver_name = 'icoFoam'

        # ----------
        # solve case
        # ----------
        bpy.ops.reynolds.solve_case()

        self.assertTrue(case_info_tool.case_solved)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestBlockMesh)
unittest.TextTestRunner().run(suite)
