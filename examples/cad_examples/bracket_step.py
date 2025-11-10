import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")

# The CAD node can be used in two modes: "exact" and "fast"
# "exact" uses an exact computation for the geometry. Using this mode
# results in better accuracy, but at the cost of computation time. This
# mode works well when you are using the toolpaths compiler, but will
# take too long for large-volume inkjet systems.
# "fast" this mode first converts the CAD file to a triangulated mesh. 
# This improves the speed of this node, at the cost of accuracy.
# Fast mode is enabled by setting the second parameter to "True"
cad_node = pv.CAD("../data/3d_models/bracket.step", True, red)
root = cad_node

viz.Render(root, materials)