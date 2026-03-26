"""
PolygonExtrude Demo - Extrude a hexagonal polygon into a 3D prism.

This example creates a regular hexagon in the XY plane and extrudes it 
upward by 10mm, then renders it in the GUI viewer.
"""
import pyvcad as pv
import pyvcad_rendering as viz
import math

# Load the default material configuration
materials = pv.default_materials

# Create a regular hexagon centered at the origin in the XY plane
radius = 10.0  # mm
num_sides = 6
vertices = []
for i in range(num_sides):
    angle = 2.0 * math.pi * i / num_sides
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    vertices.append(pv.Vec3(x, y, 0))

# Extrude the hexagon 10mm upward along its normal (+Z)
height = 10.0
root = pv.PolygonExtrude(vertices, height, False, materials.id("blue"))

viz.Render(root, materials)  # Render in a pop-up window
