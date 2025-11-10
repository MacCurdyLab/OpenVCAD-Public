import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")

strut_diameter = 0.1

# Define the edges of the unit cell with a size of 1x1x1 mm
edges = [
    [pv.Vec3(0,0,-0.5), pv.Vec3(0,0,0.5)], # Each edge is defined by two points (start and end)
    [pv.Vec3(0,-0.5,0), pv.Vec3(0,0.5,0)], # The edges are defined in millimeters
    [pv.Vec3(-0.5,0,0), pv.Vec3(0.5,0,0)],
    [pv.Vec3(-0.5,-0.5,-0.5), pv.Vec3(0.5,0.5,0.5)],
    [pv.Vec3(-0.5,0.5,-0.5), pv.Vec3(0.5,-0.5,0.5)],
    [pv.Vec3(0.5,-0.5,-0.5), pv.Vec3(-0.5,0.5,0.5)],
    [pv.Vec3(0.5,0.5,-0.5), pv.Vec3(-0.5,-0.5,0.5)],
]

# Create the custom cell using the defined edges and the strut diameter
custom_cell = pv.GraphLattice(edges, strut_diameter, red)

root = custom_cell
viz.Render(root, materials)