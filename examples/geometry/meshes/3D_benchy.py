import pyvcad as pv
import pyvcad_rendering as viz

mesh = pv.Mesh("../../data/3d_models/3DBenchy.stl")

root = mesh
viz.Render(root)