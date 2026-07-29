"""Add a fitted PNG relief to one exact face of an imported STEP solid."""

from pathlib import Path

import pyvcad as pv
import pyvcad_rendering as viz


data = Path(__file__).resolve().parents[2] / "data"
model_path = data / "3d_models" / "bracket.step"
height_map_path = data / "height_maps" / "dotted_checker.png"

model = pv.CADModel.from_step(str(model_path))
face = model.face(20)

height = pv.ImageHeightField(
    str(height_map_path),
    amplitude_mm=1.0,
    channel="luminance",
    mapping="fit",
)
relief = pv.SurfaceReliefVolume(
    face,
    height,
    embed_mm=0.35,
    edge_falloff_mm=1.0,
)

solid = model.to_node(use_fast_mode=True)
root = pv.BBoxUnion([solid, relief])

viz.Render(root)
