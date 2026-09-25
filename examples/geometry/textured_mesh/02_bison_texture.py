"""Import a detailed textured bison OBJ as a complete colored solid."""

from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz


EXPORT_INKJET_SLICES = False

# Nose-to-tail extent of the source OBJ, in OBJ coordinate units.
BISON_LENGTH_UNITS = 189.44

# Printed nose-to-tail length of the bison, in millimeters.
TARGET_LENGTH_MM = 25.0

example_dir = Path(__file__).resolve().parent
model_path = (
    example_dir.parent.parent
    / "data"
    / "textured_models"
    / "bison_buffalo"
    / "Bison_buffalo.obj"
)

bison = pv.TexturedMesh(
    str(model_path),
    color_depth=2.0,
    core_color=pv.Vec3(0.92, 0.84, 0.70),
    center=True,
    obj_unit_scale=TARGET_LENGTH_MM / BISON_LENGTH_UNITS,
    override_voxel_size=0.3,
    disable_validation=True,
)

# The source OBJ is Y-up with the nose-to-tail axis along Z. This rotation maps
# the mesh's up axis onto +Z so the bison stands on its feet, and its length
# onto X so a view down the Y axis shows the side profile.
root = pv.Rotate(-90.0, -90.0, 0.0, bison)

if EXPORT_INKJET_SLICES:
    output_dir = example_dir / "output" / "bison_texture"
    output_dir.mkdir(parents=True, exist_ok=True)
    compiler = pvc.ColorInkjetCompiler(
        root,
        pv.Vec3(0.5, 0.5, 0.5),
        str(output_dir),
        "slice_",
        "default",
        pvc.ColorInkjetExportMode.DITHERED_3D,
    )
    compiler.compile()

viz.Render(root)
