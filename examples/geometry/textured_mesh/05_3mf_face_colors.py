"""Load a 3MF with per-face color properties at a fixed preparation resolution."""

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
    / "3mf_consortium"
    / "rhombicuboctahedron_color.3mf"
)

root = pv.TexturedMesh(
    str(model_path),
    color_depth=3.0,
    core_color=pv.Vec3(1.0, 1.0, 1.0),
    center=True,
    override_voxel_size=1.0,
)

if EXPORT_INKJET_SLICES:
    output_dir = example_dir / "output" / "3mf_face_colors"
    output_dir.mkdir(parents=True, exist_ok=True)
    compiler = pvc.ColorInkjetCompiler(
        root,
        pv.Vec3(0.8, 0.8, 0.8),
        str(output_dir),
        "slice_",
        "default",
        pvc.ColorInkjetExportMode.DITHERED_3D,
    )
    compiler.compile()

viz.Render(root)
