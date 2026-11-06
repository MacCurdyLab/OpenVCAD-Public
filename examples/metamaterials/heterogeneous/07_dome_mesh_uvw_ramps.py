"""Ramp a TPMS through the thickness and across a domed triangle-mesh map with u/v/w."""

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
THICKNESS = 9.0     # mm, lattice height above the patch
LAYERS = 3          # cells through the thickness


def spherical_cap(x, y):
    r2 = (x * x + y * y) / (RADIUS * RADIUS)
    return DOME_HEIGHT * math.sqrt(max(0.0, 1.0 - 0.75 * r2))


surface = disk_surface(RADIUS, 12, 48, spherical_cap)
cell_map = mm.cell_map_from_surface(surface, cells=(12, 12, LAYERS), height=THICKNESS)

# Logical w runs from 0 on the patch to LAYERS on the outer surface, whatever the shape.
# Passing the map as coordinates ramps in cell units; outside the map the ramp is 0.
through_thickness = mm.ramp(0.5, LAYERS - 0.5, axis="w", coordinates=cell_map)
mixed_cell = pv.ImplicitUnitCell.mixed(
    pv.ImplicitUnitCell.standard("gyroid"),
    pv.ImplicitUnitCell.standard("schwarz_d"),
    through_thickness,
)

# Logical u runs across the patch: walls thicken from one side to the other.
across = mm.ramp(2.0, 10.0, axis="u", coordinates=cell_map, smooth=False)
wall_thickness = across.map_range(0.0, 1.0, 0.45, 1.0)

root = mm.tpms(cell_map, mixed_cell, wall_thickness=wall_thickness)
viz.Render(root)
