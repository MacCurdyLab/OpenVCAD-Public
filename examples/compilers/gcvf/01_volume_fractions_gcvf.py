"""
GCVF Compiler — volume fractions
================================

Builds a thin plaque with a four-corner J750 volume-fraction blend and writes
it as a legacy Stratasys `.gcvf` archive.

This demonstrates the `volume_fractions` backend path inside `GCVFCompiler`.
Because the design uses material fractions, we pass `pv.j750_materials` into
the compiler so the emitted material names match GrabCAD Print's J750 palette.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

materials = pv.j750_materials

plaque_size = 50.0
plaque_thickness = 3.0
half_size = plaque_size / 2.0

u = f"(x + {half_size:.6f}) / {plaque_size:.6f}"
v = f"(y + {half_size:.6f}) / {plaque_size:.6f}"

# Four bilinear weights spanning the plaque corners. These add up to 1.0
# throughout the entire part volume, which makes them valid volume fractions.
cyan_expr = f"(1 - ({u})) * (1 - ({v}))"
magenta_expr = f"({u}) * (1 - ({v}))"
yellow_expr = f"(1 - ({u})) * ({v})"
blue_expr = f"({u}) * ({v})"

plaque = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(plaque_size, plaque_size, plaque_thickness),
)
plaque.set_attribute(
    pv.DefaultAttributes.VOLUME_FRACTIONS,
    pv.VolumeFractionsAttribute(
        [
            (cyan_expr, materials.id("VeroBlack")),
            (magenta_expr, materials.id("VeroPureWht")),
            (yellow_expr, materials.id("VeroYL-V")),
            (blue_expr, materials.id("VeroClear")),
        ]
    ),
)

root = plaque

voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
compiler = pvc.GCVFCompiler(
    root,
    voxel_size,
    "volume_fractions_plaque.gcvf",
    materials,
    {},
    0.0,
)


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, z png count):", compiler.resolution())

viz.Render(root, materials)
