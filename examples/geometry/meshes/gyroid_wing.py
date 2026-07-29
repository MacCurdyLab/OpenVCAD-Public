# A tree that generates a triply periodic gyroid infill pattern for a wing.
# The network makes use of the function() node to generate the gyroidal surface and an
# intersection() node to combine it with a wing geometry defined in a mesh() node.
# NOTE: you will need to select at least the "high" render preset to see detail in this example
import pyvcad as pv
import pyvcad_rendering as viz

# Create wing and fill it with gyroid
wing = pv.Mesh("../../data/3d_models/wing.stl")
gyroid = pv.Function("sin(((2 * pi) / (-0.06304347 * x + 1.55)) * x) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * y) + sin(((2 * pi) / (-0.06304347 * x + 1.55)) * y) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * z) + sin(((2 * pi) / (-0.06304347 * x + 1.55)) * z) * cos(((2 * pi) / (-0.06304347 * x + 1.55)) * x)", 
                     pv.Vec3(-23, -5, -1), pv.Vec3(23, 5, 3))
filled_wing = pv.Intersection(wing, gyroid)

root = filled_wing
viz.Render(root)