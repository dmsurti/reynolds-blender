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
from bpy.props import (StringProperty, BoolProperty, FloatProperty,
                       IntVectorProperty, EnumProperty, CollectionProperty,
                       IntProperty)

# --------------
# python imports
# --------------
import yaml
import os

# ------------------------
# reynolds blender imports
# ------------------------
from reynolds_blender.gui.custom_list import ReynoldsListLabel

def load_py_dict_attr(name, props):
    setattr(bpy.types.Scene, name, {})

def load_py_list_attr(name, props):
    setattr(bpy.types.Scene, name, [])

def load_float_attr(name, props):
    float_property = FloatProperty(name=props.get(name, ''),
                                   description=props.get('description', ''),
                                   default=props.get('default', 0.0))
    setattr(bpy.types.Scene, name, float_property)

def load_int_vector_attr(name, props):
    int_vec_property = IntVectorProperty(name=props.get('name', ''),
                                         description=props.get('description',
                                                               ''),
                                         default=tuple(props.get('default',
                                                                [0, 0, 0])),
                                         subtype=props.get('subtype', 'NONE'))
    setattr(bpy.types.Scene, name, int_vec_property)

def load_enum_attr(name, props):
    items = [tuple(e) for e in props.get('items', [])]
    enum_property =  EnumProperty(name=props.get('name', ''),
                                  description=props.get('description', ''),
                                  items=items)
    setattr(bpy.types.Scene, name, enum_property)

def load_ui_list_attrs(name, props):
    coll_data_property = CollectionProperty(type=ReynoldsListLabel)
    coll_index_property = IntProperty()
    setattr(bpy.types.Scene, props.get('coll_data_prop', 'coll_data'),
            coll_data_property)
    setattr(bpy.types.Scene, props.get('coll_data_index', 'coll_index'),
            coll_index_property)

def load_string_attr(name, props):
    string_property = StringProperty(name=props.get('name', ''),
                                     description=props.get('description', ''),
                                     default=props.get('default', ''),
                                     maxlen=props.get('maxlen', 30),
                                     subtype=props.get('subtype', 'NONE'))
    setattr(bpy.types.Scene, name, string_property)

def load_bool_attr(name, props):
    bool_property = BoolProperty(name=props.get('name', ''),
                                 description=props.get('description', ''),
                                 default=props.get('default', False))
    setattr(bpy.types.Scene, name, bool_property)

def load_scene_attr(attr):
    name, props = attr
    if props['type'] == 'String':
        load_string_attr(name, props)
    if props['type'] == 'Bool':
        load_bool_attr(name, props)
    if props['type'] == 'PyDict':
        load_py_dict_attr(name, props)
    if props['type'] == 'PyList':
        load_py_list_attr(name, props)
    if props['type'] == 'Float':
        load_float_attr(name, props)
    if props['type'] == 'IntVector':
        load_int_vector_attr(name, props)
    if props['type'] == 'Enum':
        load_enum_attr(name, props)
    if props['type'] == 'UIList':
        load_ui_list_attrs(name, props)

def set_scene_attrs(attrs_filename):
    current_dir = os.path.realpath(os.path.dirname(__file__))
    attrs_file = os.path.join(current_dir, "../yaml", "attrs", attrs_filename)
    with open(attrs_file) as f:
        d = yaml.load(f)
        for attr in d.items():
            load_scene_attr(attr)

def del_scene_attr(attr):
    name, props = attr
    if props['type'] == 'UIList':
        data_attr = getattr(bpy.types.Scene,
                            props.get('coll_data_prop', 'coll_data'))
        del data_attr
        index_attr = getattr(bpy.types.Scene,
                             props.get('coll_index_prop', 'coll_index'))
        del index_attr
    else:
        a = getattr(bpy.types.Scene, name)
        del a

def del_scene_attrs(attrs_filename):
    current_dir = os.path.realpath(os.path.dirname(__file__))
    attrs_file = os.path.join(current_dir, "../yaml", "attrs", attrs_filename)
    with open(attrs_file) as f:
        d = yaml.load(f)
        for attr in d.items():
            load_scene_attr(attr)
