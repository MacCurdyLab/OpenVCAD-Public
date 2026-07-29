import pyvcad as pv
import pyvcad_rendering as viz

lattice_mesh = pv.Mesh("../data/3d_models/plate_lattice.stl")

# The STL spans z = -24 mm at the bottom to z = +24 mm at the top.
# This creates a linear shore hardness gradient from 90A to 60A.
shore_hardness = pv.FloatAttribute("max(min(75 - 0.625*z, 90), 60)")
lattice_mesh.set_attribute(
    pv.DefaultAttributes.SHORE_HARDNESS,
    shore_hardness
)
root = lattice_mesh

viz.Render(root)