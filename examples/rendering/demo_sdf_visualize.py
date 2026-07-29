# This script demos using the new SDF visualization tool to show a single sliced layer of the signed distance field of a model.

import pyvcad as pv
import pyvcad_rendering as viz

torus_a = pv.Torus(10, 2)
torus_b = pv.Torus(10, 2)

uni = pv.Intersection(pv.Translate(-5,0,0, torus_a), pv.Translate(5,0,0, torus_b))

viz.VisualizeSDF(uni, z_height=0, resolution=400, iso_surface=0.0)