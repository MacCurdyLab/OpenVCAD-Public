"""Import a detailed dragon OBJ whose color comes from its MTL material."""

from pathlib import Path

import pyvcad as pv
import pyvcad_compilers as pvc
import pyvcad_rendering as viz


EXPORT_INKJET_SLICES = False

example_dir = Path(__file__).resolve().parent
model_path = (
    example_dir.parent.parent
    / "data"
    / "textured_models"
    / "stanford_dragon_sss_test"
    / "Stanford_Dragon_SSS_Test.obj"
)

root = pv.TexturedMesh(
    str(model_path),
    color_depth=2.5,
    core_color=pv.Vec3(0.95, 0.93, 0.86),
    center=True,
    obj_unit_scale=3.0,
    override_voxel_size=0.25,
    disable_validation=True,
)

if EXPORT_INKJET_SLICES:
    output_dir = example_dir / "output" / "dragon_material_color"
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
