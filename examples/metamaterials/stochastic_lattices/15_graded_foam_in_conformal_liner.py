"""Fill a conformal liner volume with a Voronoi foam that is finer next to the head."""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformal_meshes"))
from _triangle_surface_examples import disk_surface

HEAD_RADIUS = 80.0       # mm, a spherical stand-in for a head form
LINER_THICKNESS = 14.0   # mm
CAP_ANGLE = 55.0         # degrees from the crown to the edge of the liner
NEAR_SPACING = 3.0       # mm, seed spacing against the head
FAR_SPACING = 6.0        # mm, seed spacing at the outer surface
BEAM_THICKNESS = 0.8     # mm
RIM_WIDTH = 1.2          # mm
SEED = 11

rim_radius = HEAD_RADIUS * math.sin(math.radians(CAP_ANGLE))


def head_surface(x, y):
    return math.sqrt(max(0.0, HEAD_RADIUS * HEAD_RADIUS - x * x - y * y))


# The liner volume is a conformal map grown outward from a patch of the head surface.
surface = disk_surface(rim_radius, 24, 96, head_surface)
cell_map = mm.cell_map_from_surface(surface, cells=(16, 16, 2), height=LINER_THICKNESS)

# mm.domain turns the map's trimmed volume into a solid host for the foam.
host = mm.domain(cell_map)
host.prepare(pv.Vec3(0.5, 0.5, 0.5), 1.0)

# Seed spacing grows with distance from the head: small cells against the head, large
# cells at the outer surface. The distance field is defined everywhere, including just
# outside the liner where the foam places its closing layer of seeds.
head = pv.Sphere(pv.Vec3(0.0, 0.0, 0.0), HEAD_RADIUS)
from_head = mm.distance_field(head, bandwidth=LINER_THICKNESS + 10.0)
spacing = mm.ramp(0.0, LINER_THICKNESS, coordinates=from_head).map_range(
    0.0, 1.0, NEAR_SPACING, FAR_SPACING
)

foam = mm.voronoi_foam(host, spacing, seed=SEED, beam_thickness=BEAM_THICKNESS)
# A rim seals the cut cells along the liner's edge.
root = pv.Union(foam, mm.rim(cell_map, width=RIM_WIDTH))

# Strut foams have exact distance fields, so empty space can be skipped safely.
print(mm.check_connectivity(root, voxel_size=0.3, cull_far_cells=True))
viz.Render(root)
