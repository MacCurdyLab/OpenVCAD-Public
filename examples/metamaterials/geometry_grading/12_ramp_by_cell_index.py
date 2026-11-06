"""Geometry grading: give each layer of a dome lattice its own wall thickness."""

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
LAYERS = 3          # cells through the thickness
THICKNESS = 9.0     # mm, lattice height above the patch
INNER_WALL = 1.1    # mm, wall thickness of the layer on the patch
OUTER_WALL = 0.4    # mm, wall thickness of the outermost layer


def spherical_cap(x, y):
    r2 = (x * x + y * y) / (RADIUS * RADIUS)
    return DOME_HEIGHT * math.sqrt(max(0.0, 1.0 - 0.75 * r2))


surface = disk_surface(RADIUS, 12, 48, spherical_cap)
cell_map = mm.cell_map_from_surface(surface, cells=(12, 12, LAYERS), height=THICKNESS)

# cell_index.w is 0, 1, 2 for the three layers and constant inside each layer, so a linear
# ramp over it gives one wall thickness per layer: a stepped, not smooth, grading.
layer = mm.ramp(0.0, LAYERS - 1, axis="w", coordinates=cell_map.cell_index, smooth=False)
wall_thickness = layer.map_range(0.0, 1.0, INNER_WALL, OUTER_WALL)

root = mm.gyroid(cell_map, wall_thickness=wall_thickness)
viz.Render(root)
