"""Geometry grading: thicken struts toward the rim of a dome with a height ramp."""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformal_meshes"))
from _triangle_surface_examples import disk_surface

RADIUS = 32.0       # mm, footprint radius of the dome patch
DOME_HEIGHT = 16.0  # mm
THICKNESS = 8.0     # mm, lattice height above the patch
RIM_Z = 10.0        # mm, struts are thickest at and below this height
CROWN_Z = 22.0      # mm, struts are thinnest at and above this height


def spherical_cap(x, y):
    r2 = (x * x + y * y) / (RADIUS * RADIUS)
    return DOME_HEIGHT * math.sqrt(max(0.0, 1.0 - 0.75 * r2))


surface = disk_surface(RADIUS, 12, 48, spherical_cap)
cell_map = mm.cell_map_from_surface(surface, cells=(12, 12, 2), height=THICKNESS)

# The ramp is 0 at RIM_Z and 1 at CROWN_Z and clamped outside that band, so the radius
# stays between the two values everywhere, even far from the dome.
height = mm.ramp(RIM_Z, CROWN_Z, axis="z")
beam_radius = height.map_range(0.0, 1.0, 0.75, 0.35)

root = mm.octet(cell_map, beam_radius=beam_radius)
viz.Render(root)
