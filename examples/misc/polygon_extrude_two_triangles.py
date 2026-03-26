"""
PolygonExtrude Cube Demo - Two triangles forming a cube.

This example creates two triangular PolygonExtrudes that together form a 
10x10x10 cube. Each triangle covers half of the square cross-section, 
and both are unioned together.
"""
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials

height = 2
size = 10.0  # mm

# Split the square cross-section into two triangles along the diagonal
# Triangle 1: bottom-left triangle
tri1 = [
    pv.Vec3(0, 0, -1),
    pv.Vec3(size, 0, 0),
    pv.Vec3(0, size, 0)
]

# Triangle 2: top-right triangle
tri2 = [
    pv.Vec3(size, 0, 0),
    pv.Vec3(size, size, -1),
    pv.Vec3(0, size, 0)
]

# Extrude both triangles upward by the same height
poly1 = pv.PolygonExtrude(tri1, height, False, materials.id("red"))
poly2 = pv.PolygonExtrude(tri2, height, False, materials.id("blue"))

# Union the two extruded triangles into a single cube
root = pv.Union(0.3, False, [poly1, poly2])

viz.Render(root, materials)
