"""Join a random Voronoi foam to a gyroid sheet through a tapered overlap band."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

CELL_SIZE = 6.0     # mm, gyroid cell size; the foam is sampled at a matching density
HALF_WIDTH = 2.0    # mm, the band where both structures exist is 4 mm wide
BEAM = 0.9          # mm, foam beam thickness away from the band
WALL = 0.8          # mm, gyroid wall thickness away from the band
SEED = 3

host = pv.RectPrism.FromMinAndMax(pv.Vec3(-30.0, -12.0, -12.0), pv.Vec3(30.0, 12.0, 12.0))
host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)
cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-30.0, -12.0, -12.0), pv.Vec3(30.0, 12.0, 12.0)), cell_size=CELL_SIZE
)

# Each structure thins to about 70 % as it crosses the band, so the overlap does not
# double the material while every foam strut still meets a gyroid wall.
across_band = mm.ramp(-HALF_WIDTH, HALF_WIDTH, axis="x")
gyroid = mm.gyroid(cell_map, wall_thickness=across_band.map_range(0.0, 1.0, 0.7 * WALL, WALL))
beam_thickness = across_band.map_range(0.0, 1.0, BEAM, 0.7 * BEAM)

# The foam fills the region left of x = 0; the gyroid fills the rest.
foam_side = pv.RectPrism.FromMinAndMax(pv.Vec3(-50.0, -20.0, -20.0), pv.Vec3(0.0, 20.0, 20.0))
root = mm.voronoi_tpms_transition(
    host,
    foam_side,
    gyroid,
    HALF_WIDTH,
    cell_map=cell_map,
    beam_thickness=beam_thickness,
    seed=SEED,
)

# A field blend of these two families would pinch apart; the overlap stays one piece.
print(mm.check_connectivity(root, voxel_size=0.2))
viz.Render(root)
