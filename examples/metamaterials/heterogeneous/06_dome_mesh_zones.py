"""Give a domed triangle-mesh liner three lattice zones joined by overlap bands."""

import math
import sys
from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformal_meshes"))
from _triangle_surface_examples import disk_surface

RADIUS = 32.0       # mm, footprint radius of the dome patch
DOME_HEIGHT = 16.0  # mm, height of the patch at its centre
THICKNESS = 8.0     # mm, lattice height above the patch
CROWN_Z = 21.0      # mm, the crown zone is above this height
RIM_Z = 13.0        # mm, the rim zone is below this height
OVERLAP = 2.0       # mm, half-width of each overlap band


def spherical_cap(x, y):
    r2 = (x * x + y * y) / (RADIUS * RADIUS)
    return DOME_HEIGHT * math.sqrt(max(0.0, 1.0 - 0.75 * r2))


# One conformal map over the mesh patch keeps every zone on the same cell grid.
surface = disk_surface(RADIUS, 12, 48, spherical_cap)
cell_map = mm.cell_map_from_surface(surface, cells=(12, 12, 2), height=THICKNESS)

crown = mm.gyroid(cell_map, wall_thickness=0.7)
middle = mm.octet(cell_map, beam_radius=0.45)
rim = mm.kelvin(cell_map, beam_radius=0.5)

# Regions are ordinary solids. The first matching region wins, so the crown takes
# everything above CROWN_Z, the octet band takes the rest above RIM_Z, and Kelvin cells
# fill the remainder. In "overlap" mode neighbouring zones both continue through a
# 2 * OVERLAP band, so the sheet and beam networks intersect instead of meeting edge-on.
above_crown = pv.RectPrism.FromMinAndMax(pv.Vec3(-50.0, -50.0, CROWN_Z), pv.Vec3(50.0, 50.0, 60.0))
above_rim = pv.RectPrism.FromMinAndMax(pv.Vec3(-50.0, -50.0, RIM_Z), pv.Vec3(50.0, 50.0, 60.0))
root = mm.zones(
    [crown, middle, rim],
    [above_crown, above_rim],
    mode="overlap",
    half_width=OVERLAP,
)

viz.Render(root)
