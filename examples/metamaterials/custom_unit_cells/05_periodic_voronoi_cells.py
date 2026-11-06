import numpy as np

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# Any seeds inside one cell, repeated along U, V and W, divide space into Voronoi cells whose
# edges tile without seams. Seeds are fractional cell coordinates; these eight A15 sites give the
# Weaire-Phelan foam.
a15 = [(0, 0, 0), (0.5, 0.5, 0.5), (0.25, 0.5, 0), (0.75, 0.5, 0),
       (0, 0.25, 0.5), (0, 0.75, 0.5), (0.5, 0, 0.25), (0.5, 0, 0.75)]
weaire_phelan = mm.periodic_voronoi(a15).edges()

# Random seeds give a random foam that still tiles, so it can follow a curved map.
random_foam = mm.periodic_voronoi(np.random.default_rng(4).random((10, 3))).edges()

block = mm.rectangular_cell_map((pv.Vec3(-46, -12, -12), pv.Vec3(-22, 12, 12)), cells=(2, 2, 2))
ring = mm.cylindrical_cell_map(pv.Vec3(20, 0, -12), 14.0, 26.0, 24.0, cells=(10, 2, 1))
root = pv.Union(
    mm.graph_lattice(block, weaire_phelan, beam_radius=0.45),
    mm.graph_lattice(ring, random_foam, beam_radius=0.45),
)

viz.Render(root)
