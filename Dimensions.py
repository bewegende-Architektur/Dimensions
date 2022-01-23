bl_info = {
    "name": "Dimensions",
    "description": "Automatically create dimension lines within blender",
    "author": "bewegende Architektur e.U.",
    "version": (0, 0, 1),
    "blender": (3, 0, 0),
    "location": "3D View > Tools",
}

import bpy
import bmesh
from operator import itemgetter
import math

from bpy.props import (IntProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy.types import (Panel, Menu, Operator, PropertyGroup)

def create_dimension_line(v_0, v_1, orientation):
    # calculate distance, rotation and location of text
    if orientation == "aligned":
        r = math.atan2(v_1[1]-v_0[1], v_1[0]-v_0[0])
        d = (((v_1[0] - v_0[0])**2) + ((v_1[1]-v_0[1])**2))**0.5

        text_loc = (v_0 + v_1) * 0.5

    if orientation == "x":
        r = 0
        d = v_1[0] - v_0[0]

        text_loc_x = (v_1[0] + v_0[0]) * 0.5
        text_loc_y = v_0[1]
        text_loc_z = 0
        text_loc = [text_loc_x, text_loc_y, text_loc_z]

    if orientation == "y":
        r = 1.5708
        d = v_1[1] - v_0[1]

        text_loc_x = v_0[0]
        text_loc_y = (v_1[1] + v_0[1]) * 0.5
        text_loc_z = 0
        text_loc = [text_loc_x, text_loc_y, text_loc_z]

    s = [0, 0, 0]
    e = [d, 0, 0]

    # create the Curve Datablock
    name = "<Bemaßungskette>"
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2

    # line between start and end (extended with -0.08 units)
    line_h_s = [s[0]-0.08, s[1], 0, 1]
    line_h_e = [e[0]+0.08, e[1], 0, 1]

    polyline = curve.splines.new("POLY")
    polyline.points.add(1)
    polyline.points[0].co = line_h_s
    polyline.points[1].co = line_h_e

    # vertical and diagonal line at start
    line_v_s_0 = [s[0], s[1]-0.08, 0, 1]
    line_v_s_1 = [s[0], s[1]+0.08, 0, 1]

    polyline = curve.splines.new("POLY")
    polyline.points.add(1)
    polyline.points[0].co = line_v_s_0
    polyline.points[1].co = line_v_s_1

    line_d_s_0 = [s[0]-0.06, s[1]-0.06, 0, 1]
    line_d_s_1 = [s[0]+0.06, s[1]+0.06, 0, 1]

    polyline = curve.splines.new("POLY")
    polyline.points.add(1)
    polyline.points[0].co = line_d_s_0
    polyline.points[1].co = line_d_s_1

    # vertical and diagonal line at end
    line_v_e_0 = [e[0], e[1]-0.08, 0, 1]
    line_v_e_1 = [e[0], e[1]+0.08, 0, 1]

    polyline = curve.splines.new("POLY")
    polyline.points.add(1)
    polyline.points[0].co = line_v_e_0
    polyline.points[1].co = line_v_e_1

    line_d_e_0 = [e[0]-0.06, e[1]-0.06, 0, 1]
    line_d_e_1 = [e[0]+0.06, e[1]+0.06, 0, 1]

    polyline = curve.splines.new("POLY")
    polyline.points.add(1)
    polyline.points[0].co = line_d_e_0
    polyline.points[1].co = line_d_e_1

    # create Object
    obj = bpy.data.objects.new(name, curve)

    # link object to collection
    bpy.context.scene.collection.objects.link(obj)
    #bpy.data.collections["<Dimensions>"].objects.link(obj)

    # set rotaiton of dimension line
    obj.location = v_0
    obj.rotation_euler[2] = r

    # apply extusion to render with freestyle
    obj.data.extrude = 0.001

    # create text
    name = "<Bemaßungstext>"
    text = str(round(d, 2)) + " m"
    curve = bpy.data.curves.new(type="FONT", name=name)
    curve.body = text
    obj = bpy.data.objects.new(name=name, object_data=curve)

    obj.location = text_loc
    obj.rotation_euler[2] = r
    obj.scale = [0.1, 0.1, 0.1]
    obj.data.align_x = 'CENTER'
    obj.data.offset_y = 0.2
    bpy.context.scene.collection.objects.link(obj)
    #bpy.data.collections["<Dimension>"].objects.link(obj)

def get_selected_points():
    # append all selected points to list
    points = []
    for obj in bpy.context.objects_in_mode:
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            if v.select:
                # absolute Position einfügen!
                points.append(v.co)

    return points

def create_multiple_dimensions(orientation):
    points = get_selected_points()
    # sort points via position

    if orientation == "aligned":
        sorted_points = points # works only for two points

    if orientation == "x":
        sorted_points = sorted(points, key=itemgetter(0))

    if orientation == "y":
        sorted_points = sorted(points, key=itemgetter(1))

    # get distance and add dimensions
    for point_id in range(len(sorted_points)):
        if point_id > 0:
            start = sorted_points[point_id-1].copy()
            end = sorted_points[point_id].copy()

            if orientation == "aligned":
                create_dimension_line(start, end, "aligned")

            if orientation == "x":
                start[1] = 10
                end[1] = 10
                create_dimension_line(start, end, "x")

            if orientation == "y":
                start[0] = 1
                end[0] = 1
                create_dimension_line(start, end, "y")

    # overall dimension
    start = sorted_points[0].copy()
    end = sorted_points[len(sorted_points)-1].copy()

    if orientation == "x":
        start[1] = 10 + 0.2
        end[1] = 10 + 0.2
        create_dimension_line(start, end, "x")

    if orientation == "y":
        start[0] = 1 + 0.2
        end[0] = 1 + 0.2
        create_dimension_line(start, end, "y")

class CustomProperties(PropertyGroup):
    scale: IntProperty(
        name = "scale",
        description = "Scale of drawing",
        default = 50,
        min = 1,
        max = 5000
        )

    elitism: IntProperty(
        name = "elitism",
        description="Size of elitism for GA",
        default = 2,
        min = 1,
        max = 100
        )

    forces: EnumProperty(
        name="forces:",
        description="Force types",
        items=[
                ("sigma", "Sigma", ""),
                ("axial", "Axial", ""),
                ("moment_y", "Moment Y", ""),
                ("moment_z", "Moment Z", "")
               ]
        )

class WM_OT_dimension_x(Operator):
    bl_label = "dimension_x"
    bl_idname = "wm.dimension_x"
    bl_description = "Please select multiple vertices in edit-mode"

    def execute(self, context):
        create_multiple_dimensions("x")
        return {"FINISHED"}


class WM_OT_dimension_y(Operator):
    bl_label = "dimension_y"
    bl_idname = "wm.dimension_y"
    bl_description = "Please select multiple vertices in edit-mode"

    def execute(self, context):
        create_multiple_dimensions("y")
        return {"FINISHED"}

class WM_OT_dimension_aligned(Operator):
    bl_label = "dimension_aligned"
    bl_idname = "wm.dimension_aligned"
    bl_description = "Please select multiple vertices in edit-mode"

    def execute(self, context):
        create_multiple_dimensions("aligned")
        return {"FINISHED"}

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "Dimensions"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dimensions"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        dimensions = scene.dimensions

        # define scale
        #box = layout.box()
        #box.label(text="Scale:")
        #box.operator("wm.set_structure", text="Set")

        box = layout.box()
        box.label(text="Dimensions:")
        box.operator("wm.dimension_x", text="x")
        box.operator("wm.dimension_y", text="y")
        box.operator("wm.dimension_aligned", text="aligned")

classes = (
    CustomProperties,

    WM_OT_dimension_x,
    WM_OT_dimension_y,
    WM_OT_dimension_aligned,

    OBJECT_PT_CustomPanel
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.dimensions = PointerProperty(type=CustomProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.dimensions

if __name__ == "__main__":
    register()
