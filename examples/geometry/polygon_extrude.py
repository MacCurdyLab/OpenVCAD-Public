"""
PolygonExtrude Demo - Extrude a hexagonal polygon into a 3D prism.

This example creates a regular hexagon in the XY plane and extrudes it 
upward by 10mm, then renders it in the GUI viewer.
"""
import pyvcad as pv
import pyvcad_rendering as viz
import math

# Create a regular polygon (num_sides) centered at the origin in the XY plane
radius = 10.0  # mm
num_sides = 6
height = 10.0
symmetric = True
vertices = []
for i in range(num_sides):
    angle = 2.0 * math.pi * i / num_sides
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    vertices.append(pv.Vec3(x, y, 0))

# Extrude the hexagon upward along its normal (+Z)
root = pv.PolygonExtrude(vertices, height, symmetric)

viz.Render(root)
