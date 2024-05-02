bl_info = {
    "name": "Snail Shell Generator",
    "author": "Timothy Heider",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Mesh Object",
    "category": "Add Mesh",
}

import bpy
import bmesh
import math
import numpy as np
import mathutils
from mathutils import Vector
from bpy.props import FloatProperty, IntProperty

def assign_base_material(obj, material_name="BaseMaterial", color=(0.2, 0.2, 0.8, 1.0)):
    """
    Assigns a material to the given object.

    Parameters:
    - obj: The Blender object to assign the material to.
    - material_name: The name of the material.
    - color: The diffuse color of the material as a tuple (R, G, B, Alpha).
    """
    # Check if the material already exists, otherwise create it
    material = bpy.data.materials.get(material_name)
    if not material:
        material = bpy.data.materials.new(name=material_name)
        material.diffuse_color = color  # Set the material color

    # Assign the material to the object
    if obj.data.materials:
        obj.data.materials[0] = material  # Replace the existing material
    else:
        obj.data.materials.append(material)  # Add new material


class MESH_OT_add_object(bpy.types.Operator):
    bl_idname = "mesh.add_object"
    bl_label = "Snail Shell"
    bl_options = {'REGISTER', 'UNDO'}

    vertical_translation: FloatProperty(name="Vertical Translation", default=10, min=-20.0, max=20.0)
    scale_factor_a: FloatProperty(name="Scale Factor", default=0.08, min=0.0001, max=5)
    growth_rate_b: FloatProperty(name="Growth Rate", default=0.1, min=0.01, max=5)
    theta_max: FloatProperty(name="Theta Max", default=16 * np.pi, min=3 * np.pi, max=32 * np.pi)
    num_spiral_points: IntProperty(name="Spiral Points", default=200, min=100, max=1000)    
    num_circle_points: IntProperty(name="Circle Points", default=24, min=4, max=100)    
    
    def get_spiral_radius(self, theta):
        r = self.scale_factor_a * np.exp(self.growth_rate_b * theta)
        return r
    
    def get_spiral_point(self, theta):
        r = self.get_spiral_radius(theta)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return {'x': x, 'y': y}    

    def create_circle_mesh(self, radius, angle):
        source_circle_mesh = bmesh.new()
        for a in np.arange(0, np.pi * 2, (np.pi * 2) / self.num_circle_points):        
            x = radius * math.cos(a)
            y = 0
            z = radius * math.sin(a)
            bmesh.ops.create_vert(source_circle_mesh, co=(x, y, z))
        source_circle_mesh.verts.ensure_lookup_table()
        rotation_matrix = mathutils.Matrix.Rotation(angle, 4, 'Z')
        bmesh.ops.rotate(source_circle_mesh, cent=(0, 0, 0), matrix=rotation_matrix, verts=source_circle_mesh.verts)
        return source_circle_mesh

    def execute(self, context):
        # Create a new mesh object
        shell_mesh = bpy.data.meshes.new(name="Snail Shell")
        shell_object = bpy.data.objects.new("Snail Shell", shell_mesh)

        # Link the object to the current collection
        bpy.context.collection.objects.link(shell_object)

        # Set the object as the active object
        bpy.context.view_layer.objects.active = shell_object
        shell_object.select_set(True)
        
        # Create a mesh for the snail shell
        snail_shell_mesh = bmesh.new()
        pos = 0

        # create a circle mesh to use as a template.
        delta_angle = self.theta_max / self.num_spiral_points

        # add the first circle.        
        theta = self.theta_max
        theta2 = theta - (2 * np.pi)
        spiral_point2 = self.get_spiral_point(theta2)
        spiral_radius = self.get_spiral_radius(theta)
        spiral_radius2 = self.get_spiral_radius(theta2)
        radius_delta = spiral_radius - spiral_radius2
        circle_radius = radius_delta / 2
        circle_rotation_angle = theta
        # Create a circle source_circle_mesh       
        source_circle_mesh = self.create_circle_mesh(circle_radius, circle_rotation_angle) 
        for v in source_circle_mesh.verts:            
            bmesh.ops.create_vert(snail_shell_mesh, co=(v.co.x + spiral_point2['x'], v.co.y + spiral_point2['y'], v.co.z + self.vertical_translation - (spiral_radius / 3)))
        snail_shell_mesh.verts.ensure_lookup_table() 
        source_circle_mesh.free()
        
        for i in range(1, self.num_spiral_points):
            theta -= delta_angle            
            circle_rotation_angle -= delta_angle
            theta2 = theta - (2 * np.pi)
            spiral_point2 = self.get_spiral_point(theta2)
            spiral_radius = self.get_spiral_radius(theta)
            spiral_radius2 = self.get_spiral_radius(theta2)
            radius_delta = spiral_radius - spiral_radius2
            circle_radius = radius_delta / 2
            source_circle_mesh = self.create_circle_mesh(circle_radius, circle_rotation_angle) 
            for v in source_circle_mesh.verts:            
                bmesh.ops.create_vert(snail_shell_mesh, co=(v.co.x + spiral_point2['x'], v.co.y + spiral_point2['y'], v.co.z + self.vertical_translation - (spiral_radius / 3)))
            snail_shell_mesh.verts.ensure_lookup_table() 
            source_circle_mesh.free()

            # Create faces between the two circles
            circle_verts_length = self.num_circle_points
            for i in range(pos, pos + circle_verts_length - 1):
                p1 = snail_shell_mesh.verts[i]        
                p2 = snail_shell_mesh.verts[i + circle_verts_length]
                p3 = snail_shell_mesh.verts[i + circle_verts_length + 1]
                p4 = snail_shell_mesh.verts[i + 1]
                snail_shell_mesh.faces.new([p1, p2, p3, p4])    
            # Connect the last and first vertices of the circle
            p1 = snail_shell_mesh.verts[pos + circle_verts_length - 1]
            p2 = snail_shell_mesh.verts[pos + circle_verts_length * 2 - 1]
            p3 = snail_shell_mesh.verts[pos + circle_verts_length]
            p4 = snail_shell_mesh.verts[pos]
            snail_shell_mesh.faces.new([p1, p2, p3, p4])

            pos += circle_verts_length
        # Update the mesh with the new data
        snail_shell_mesh.to_mesh(shell_mesh)
        snail_shell_mesh.free()        

        # Create a new mesh object
        assign_base_material(shell_object)
        return {'FINISHED'}
        
def menu_func(self, context):
    self.layout.operator(MESH_OT_add_object.bl_idname)

def register():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    # register
    bpy.utils.register_class(MESH_OT_add_object)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

# def unregister():
#     bpy.utils.unregister_class(MESH_OT_add_object)
#     bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
