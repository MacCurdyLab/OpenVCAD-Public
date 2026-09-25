"""Load a self-contained textured 3MF model and optionally export inkjet slices."""

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
    / "sphere_logo.3mf"
)

root = pv.TexturedMesh(
    str(model_path),
    color_depth=1.5,
    core_color=pv.Vec3(1.0, 1.0, 1.0),
    center=True,
)

if EXPORT_INKJET_SLICES:
    output_dir = example_dir / "output" / "3mf_texture"
    output_dir.mkdir(parents=True, exist_ok=True)
    compiler = pvc.ColorInkjetCompiler(
        root,
        pv.Vec3(0.3, 0.3, 0.3),
        str(output_dir),
        "slice_",
        "default",
        pvc.ColorInkjetExportMode.DITHERED_3D,
    )
    compiler.compile()

viz.Render(root)
