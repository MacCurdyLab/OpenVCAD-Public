"""Map a folded plate lattice between two curved CAD face patches."""

import math

import cadquery as cq

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

use_triangulated = True


def lower_surface(u, v):
    x = 48.0 * (u - 0.5)
    y = 36.0 * (v - 0.5)
    z = 8.0 * math.sin(math.pi * (u - 0.5)) * math.sin(math.pi * (v - 0.5))
    return x, y, z


def upper_surface(u, v):
    x = 48.0 * (u - 0.5)
    y = 36.0 * (v - 0.5)
    z = 18.0 + 12.0 * math.cos(math.pi * (u - 0.5)) * math.cos(math.pi * (v - 0.5))
    return x, y, z


# The surfaces use the same X/Y footprint but differ strongly in curvature: an
# 8 mm saddle below and a 12 mm dome above.
lower_cad = cq.Workplane("XY").parametricSurface(
    lower_surface,
    N=24,
    tol=0.02,
    smoothing=None,
)
upper_cad = cq.Workplane("XY").parametricSurface(
    upper_surface,
    N=24,
    tol=0.02,
    smoothing=None,
)
lower = pv.CADModel.from_cadquery(lower_cad).faces[0]
upper = pv.CADModel.from_cadquery(upper_cad).faces[0]

cell_map = mm.cell_map_between_cad_faces(
    lower,
    upper,
    cells=(8, 6, 4),
    linear=False,
)
root = mm.plate_lattice(
    cell_map,
    wall_thickness=0.8,
    eccentricity=0.82,
    surface_mode="triangulated" if use_triangulated else "bilinear",
    surface_tolerance=0.04,
)

viz.Render(root)
