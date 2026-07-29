"""
Function Demo - Using a periodic implicit expression (a gyroid) to show why
the min/max bounding box argument is not optional in practice.

Function evaluates a math expression (via exprtk) as the signed distance to
a surface. The expression can reference Cartesian (x, y, z), cylindrical
(rho, phic, z), or spherical (r, theta, phis) coordinates -- all of them are
computed for you from x, y, z on every evaluation.

A gyroid is a great illustration of the bounding box requirement: the
expression
    sin(f*x) * cos(f*y) + sin(f*y) * cos(f*z) + sin(f*z) * cos(f*x)
is a triply-periodic minimal surface with zero-crossings everywhere in
space -- on its own it has no "inside" or "outside" of a part, just an
infinite repeating lattice. Function.evaluate() only returns a value for
sample points inside the node's [min, max] box; outside that box it always
returns "no material", regardless of what the expression would otherwise
produce there. So for an unbounded field like this, the bounding box isn't
a rendering/meshing hint -- it *is* what carves a finite part out of the
infinite pattern. If omitted, min/max default to (-10,-10,-10) and
(10,10,10).

The two Function nodes below share the identical expression and differ only
in their bounding box, to show how the box alone reshapes the output: a
cubic block keeps three unit cells in every direction, while a slab keeps
the same X/Y footprint but only a thin sliver in Z.
NOTE: select at least the "high" render preset to see the surface detail.
"""
import math

import pyvcad as pv
import pyvcad_rendering as viz

cell_size = 10.0  # mm, period of one gyroid unit cell
frequency = 2.0 * math.pi / cell_size

gyroid_expr = (
    "sin({f}*x) * cos({f}*y) + "
    "sin({f}*y) * cos({f}*z) + "
    "sin({f}*z) * cos({f}*x)"
).format(f=frequency)

# A 3x3x3 block of unit cells (30mm per side), centered at the origin.
block_extent = 1.5 * cell_size
gyroid_block = pv.Function(
    gyroid_expr,
    pv.Vec3(-block_extent, -block_extent, -block_extent),
    pv.Vec3(block_extent, block_extent, block_extent),
)

# The exact same expression, but the bounding box is a thin slab instead of
# a cube: same X/Y footprint, only +/-3mm of depth in Z. Nothing about the
# expression changed -- only the box -- yet the result is a completely
# different-looking part.
gyroid_slab = pv.Translate(
    3.5 * cell_size, 0.0, 0.0,
    pv.Function(
        gyroid_expr,
        pv.Vec3(-block_extent, -block_extent, -3.0),
        pv.Vec3(block_extent, block_extent, 3.0),
    ),
)

root = pv.Union(gyroid_block, gyroid_slab)

viz.Render(root)
