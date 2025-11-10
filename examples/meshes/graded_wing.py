# A tree that generates a triply periodic gyroid infill pattern for a wing.
# The network makes use of the function() node to generate the gyroidal surface and an
# intersection() node to combine it with the a wing geometry defined in a mesh() node.
# Finally, a fgrade() node is used to cross-grade two materials together along the length
# of the wing. The example demos the ability to grade both materials and geometry.
# See paper for more details.
import pyvcad as pv
import pyvcad_rendering as viz

materials = pv.default_materials
red = materials.id("red")
blue = materials.id("blue")

# Create wing and fill it with gyroid
wing = pv.Mesh("../data/3d_models/wing.stl", red)
gyroid = pv.Function("sin(((2 * pi) / (-0.06304347 * x + 1.55)) * x) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * y) + sin(((2 * pi) / (-0.06304347 * x + 1.55)) * y) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * z) + sin(((2 * pi) / (-0.06304347 * x + 1.55)) * z) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * x)", 
                     red, pv.Vec3(-23, -5, -1), pv.Vec3(23, 5, 3))
filled_wing = pv.Intersection(False, [wing, gyroid])

# Grade material along the wing
fgrade = pv.FGrade(["0.021739 * x + 0.5", "-0.021739 * x + 0.5"],[red, blue], True)
fgrade.set_child(filled_wing)
root = fgrade

viz.Render(root, materials)