"""Grow cells from an inner dome so they end exactly on an off-centre outer surface.

``mm.surface_gap`` casts a ray from every vertex of the inner patch along its normal and
measures the distance to a target -- here an off-centre sphere, so the gap varies across the
dome. Passing that per-vertex array as ``height`` gives a variable-height map whose outer
cells end on the target instead of at one constant thickness.
"""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import disk_surface

INNER_RADIUS = 60.0   # mm, radius of the sphere the inner dome lies on
PATCH_RADIUS = 30.0   # mm, footprint radius of the dome patch


def inner_dome(x, y):
    return math.sqrt(INNER_RADIUS * INNER_RADIUS - x * x - y * y) - INNER_RADIUS


# The inner surface the lattice grows from (normals point up and out).
inner = disk_surface(PATCH_RADIUS, 12, 48, inner_dome)

# The outer target: a larger sphere shifted sideways, so the gap is uneven.
outer = pv.Sphere(pv.Vec3(6.0, 0.0, -INNER_RADIUS), INNER_RADIUS + 9.0)

# Per-vertex distance along each normal to the target.
gap = mm.surface_gap(inner, outer, max_distance=40.0)
print(f"gap from {gap.min():.1f} to {gap.max():.1f} mm")

# Cells grow from the inner dome and end on the outer sphere everywhere.
cell_map = mm.cell_map_from_surface(inner, cells=(10, 10, 2), height=gap)

root = pv.Union(
    mm.gyroid(cell_map, wall_thickness=0.7),
    mm.rim(cell_map, width=1.5),
)

viz.Render(root)
