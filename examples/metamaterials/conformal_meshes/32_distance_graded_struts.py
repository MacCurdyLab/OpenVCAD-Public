"""Grade strut thickness by distance from another body.

``mm.distance_field(body)`` is a native ``pv.FloatAttribute`` holding the distance in mm to any
node. Mapped through ``map_range`` and ``clamp`` it sets the beam radius, so struts are thick
next to the body and thin away from it -- here a sphere resting under one side of a dome.
"""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import disk_surface

DOME_RADIUS = 60.0


def dome(x, y):
    return math.sqrt(DOME_RADIUS * DOME_RADIUS - x * x - y * y) - DOME_RADIUS


surface = disk_surface(30.0, 12, 48, dome)
cell_map = mm.cell_map_from_surface(surface, cells=(8, 8, 2), height=10.0)

# The body the grading is measured from.
body = pv.Sphere(pv.Vec3(-14.0, 0.0, -14.0), 10.0)

# 1.3 mm struts next to the body, falling to 0.35 mm at 30 mm away.
radius = mm.distance_field(body, bandwidth=40.0).map_range(0.0, 30.0, 1.3, 0.35).clamp(0.35, 1.3)

root = pv.Union(
    mm.bcc(cell_map, beam_radius=radius),
    mm.rim(cell_map, width=1.0),
)

viz.Render(root)
