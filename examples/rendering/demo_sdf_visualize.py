# This script demos using the SDF visualization tool to show a single sliced layer of the signed distance field of a model.
# The slice plane is chosen with the `plane` argument, and `offset` positions the slice along the remaining axis.

import pyvcad as pv
import pyvcad_rendering as viz

def build_model():
    torus_a = pv.Torus(10, 2)
    torus_b = pv.Torus(10, 2)
    return pv.Intersection(pv.Translate(-5,0,0, torus_a), pv.Translate(5,0,0, torus_b))

# The XY plane at Z=0 (the default plane).
viz.VisualizeSDF(build_model(), offset=0, resolution=400, iso_surface=0.0)

# The YZ plane at X=0 cuts through both lobes of the intersection.
viz.VisualizeSDF(build_model(), offset=0, resolution=400, iso_surface=0.0, plane="yz")

# The XZ plane needs an offset to reach a lobe. The two tori meet at Y = +/-sqrt(10^2 - 5^2).
viz.VisualizeSDF(build_model(), offset=8.66, resolution=400, iso_surface=0.0, plane="xz")
