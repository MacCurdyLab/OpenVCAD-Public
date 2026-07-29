"""
GCVF Compiler — full color
==========================

Builds a thin plaque with a smooth four-corner RGBA field and writes it as a
legacy Stratasys `.gcvf` archive.

This demonstrates the `color_rgba` backend path inside `GCVFCompiler`. The
compiler converts the continuous color field into CMYKW+Clear print channels,
then maps those channels onto J750 material names.
"""
from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz

plaque_size = 80.0
plaque_thickness = 6.0
half_size = plaque_size / 2.0

icc_profiles_dir = Path(pvc.__file__).resolve().parent / "icc_profiles"
if not icc_profiles_dir.is_dir():
    icc_profiles_dir = Path(__file__).resolve().parents[3] / "compilers" / "icc_profiles"
pvc.ColorPipeline.set_icc_resource_path(str(icc_profiles_dir))

u = f"(x + {half_size:.6f}) / {plaque_size:.6f}"
v = f"(y + {half_size:.6f}) / {plaque_size:.6f}"

# Corner colors:
#   bottom-left  = cyan
#   bottom-right = magenta
#   top-left     = yellow
#   top-right    = black
r_expr = f"({u}) * (1 - ({v})) + (1 - ({u})) * ({v})"
g_expr = f"1 - ({u})"
b_expr = f"1 - ({v})"
a_expr = "1.0"

plaque = pv.RectPrism(
    pv.Vec3(0.0, 0.0, 0.0),
    pv.Vec3(plaque_size, plaque_size, plaque_thickness),
)
plaque.set_attribute(
    pv.DefaultAttributes.COLOR_RGBA,
    pv.Vec4Attribute(r_expr, g_expr, b_expr, a_expr),
)

root = plaque

# The mapping is user-controlled. Here we route CMYK to a mixed Agilus/Vero
# J750 loadout while leaving white/clear on their default Vero materials.
channel_material_map = {
    "cyan": "VeroCY-V",
    "magenta": "VeroMGT-V",
    "yellow": "VeroYL-V",
    "black": "VeroBlack",
    "white": "VeroPureWht",
    "clear": "VeroClear",
}

voxel_size = pv.Vec3(0.0423, 0.0846, 0.027)
compiler = pvc.GCVFCompiler(
    root,
    voxel_size,
    "full_color_plaque.gcvf",
    None,
    channel_material_map,
)


def on_progress(progress):
    print("compile progress: {:.1f}%".format(100.0 * progress))


compiler.set_progress_callback(on_progress)
compiler.compile()
print("resolution (x, y, z png count):", compiler.resolution())

viz.Render(root)
