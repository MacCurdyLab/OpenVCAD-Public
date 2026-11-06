"""Grade a domed shell from random Voronoi foam at the rim to Kelvin cells at the crown."""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformal_meshes"))
from _triangle_surface_examples import disk_surface

RADIUS = 80.0          # mm, radius of the inner spherical surface
THICKNESS = 12.0       # mm, shell thickness
CAP_ANGLE = 55.0       # degrees from the pole to the rim
CELLS = (20, 20, 2)    # map cells; about 6 mm cubes
BEAM_THICKNESS = 0.9   # mm
SEED = 7

rim_radius = RADIUS * math.sin(math.radians(CAP_ANGLE))
rim_height = RADIUS * math.cos(math.radians(CAP_ANGLE))


def sphere_cap(x, y):
    return math.sqrt(max(0.0, RADIUS * RADIUS - x * x - y * y))


# A conformal map over the inner surface gives the sites of the regular region: they follow
# the dome instead of a straight grid ("align to graph points").
surface = disk_surface(rim_radius, 24, 96, sphere_cap)
cell_map = mm.cell_map_from_surface(surface, cells=CELLS, height=THICKNESS)

# The host is the solid shell between the two spheres, cut just above the rim.
host = pv.Intersection(
    pv.Difference(
        pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), RADIUS + THICKNESS),
        pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), RADIUS),
    ),
    pv.RectPrism.FromMinAndMax(
        pv.Vec3(-120.0, -120.0, rim_height + 2.0), pv.Vec3(120.0, 120.0, 120.0)
    ),
)
host.prepare(pv.Vec3(0.5, 0.5, 0.5), 1.0)

# Random near the rim, regular above 30 mm over the rim.
regularity = mm.ramp(rim_height + 15.0, rim_height + 30.0, axis="z")
root = mm.voronoi_transition(
    host,
    regularity,
    kind="bcc",
    cell_map=cell_map,
    beam_thickness=BEAM_THICKNESS,
    seed=SEED,
)

# Strut foams have exact distance fields, so empty space can be skipped safely.
print(mm.check_connectivity(root, voxel_size=0.3, cull_far_cells=True))
viz.Render(root)
