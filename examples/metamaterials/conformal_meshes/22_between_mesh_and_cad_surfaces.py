"""Map a conformal lattice through the gap between a mesh surface and a CAD surface.

This mirrors the paired-face workflow, but across surface *types*: the lower boundary is a triangle
mesh and the upper boundary is a CAD patch authored in CadQuery. ``cell_map_between_surfaces``
accepts either type in either slot, so the graded lattice fills the offset shell between an
undulating mesh floor and a smooth engineered dome above it.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _triangle_surface_examples import indexed_grid

# Lower boundary: an undulating egg-crate mesh -- clearly not a dome.
def wavy_floor(x, y):
    return 6.0 * math.sin(math.pi * x / 16.0) * math.sin(math.pi * y / 16.0)


# The egg-crate waves stretch this patch along its diagonals, so the default (principal-axis)
# chart orientation would run U diagonally while the CAD dome's U runs along world X --
# ``cell_map_between_surfaces`` would then twist the shell by the 45-degree mismatch its discrete
# flip/exchange alignment cannot remove. Pinning the chart U axis to world X keeps both
# parameterizations rotationally in step.
floor_vertices, floor_triangles = indexed_grid(64.0, 64.0, 100, 100, wavy_floor)
floor_surface = pv.TriangleMeshSurface(
    floor_vertices, floor_triangles, u_axis_hint=pv.Vec3(1.0, 0.0, 0.0)
)

# Upper boundary: a smooth engineered dome authored as a CAD patch, well above the floor.
OFFSET = 30.0

TRIM_MODE = pv.TrimMode.boundary


def engineered_dome(u, v):
    x = 64.0 * (u - 0.5)
    y = 64.0 * (v - 0.5)
    z = OFFSET + 18.0 * math.cos(math.pi * x / 78.0) * math.cos(math.pi * y / 78.0)
    return x, y, z


engineered_cad = cq.Workplane("XY").parametricSurface(
    engineered_dome,
    N=24,
    tol=0.02,
    smoothing=None,
)
engineered_surface = pv.CADModel.from_cadquery(engineered_cad).faces[0]

# Create three cell layers through the gap; W runs from the mesh (w=0) to the CAD surface (w=1).
cell_map = mm.cell_map_between_surfaces(
    floor_surface,
    engineered_surface,
    cells=(12, 12, 3),
    trim=TRIM_MODE
)
# Fill the shell with an octet beam lattice.
root = mm.octet(
    cell_map,
    beam_radius=0.65,
)

viz.Render(root)
