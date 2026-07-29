"""Create and tile a custom periodic implicit unit cell."""

import math

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


two_pi = 2.0 * math.pi


def rippled_p(u, v, w):
    """Return the custom periodic scalar field."""
    a = two_pi * u
    b = two_pi * v
    c = two_pi * w
    return (
        math.cos(a)
        + math.cos(b)
        + math.cos(c)
        + 0.35 * math.cos(a + b + c)
    )


def rippled_p_gradient(u, v, w):
    """Return the analytic gradient of the custom scalar field."""
    a = two_pi * u
    b = two_pi * v
    c = two_pi * w
    coupled = -0.35 * two_pi * math.sin(a + b + c)
    return pv.Vec3(
        -two_pi * math.sin(a) + coupled,
        -two_pi * math.sin(b) + coupled,
        -two_pi * math.sin(c) + coupled,
    )


unit_cell = pv.ImplicitUnitCell(
    rippled_p,
    rippled_p_gradient,
    name="rippled_p",
)
assert unit_cell.validate_periodicity()

preview_map = mm.rectangular_cell_map(
    (pv.Vec3(-6.0, -6.0, -6.0), pv.Vec3(6.0, 6.0, 6.0)),
    cells=(1, 1, 1),
)
unit_cell_preview = mm.tpms(
    preview_map,
    unit_cell,
    mode="sheet",
    wall_thickness=0.9,
)

tiled_map = mm.rectangular_cell_map(
    (pv.Vec3(-18.0, -18.0, -18.0), pv.Vec3(18.0, 18.0, 18.0)),
    cells=(3, 3, 3),
)
tiled_lattice = mm.tpms(
    tiled_map,
    unit_cell,
    mode="sheet",
    wall_thickness=0.9,
)

root = tiled_lattice
viz.Render(root)
