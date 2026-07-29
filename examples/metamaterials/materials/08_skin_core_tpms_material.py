"""Assign a tough skin and compliant core through TPMS wall depth."""

from numba import cfunc, types

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

materials = pv.default_materials
cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -16.0, -12.0), pv.Vec3(24.0, 16.0, 12.0)),
    cells=(4, 3, 2),
)
root = mm.gyroid(cell_map, wall_thickness=3.5)

signature = types.float64(types.float64, types.float64, types.float64, types.float64)


@cfunc(signature)
def skin_fraction(x, y, z, d):
    return 1.0 if d > -0.7 else 0.0


@cfunc(signature)
def core_fraction(x, y, z, d):
    return 0.0 if d > -0.7 else 1.0


root.shell.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute([
        (skin_fraction, materials.id("white")),
        (core_fraction, materials.id("red")),
    ]),
)
viz.Render(root, materials)
