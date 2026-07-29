"""Wrap a generated skin-microrelief height map around a cylindrical wall."""

from pathlib import Path

import cadquery as cq
import pyvcad as pv
import pyvcad_rendering as viz


data = Path(__file__).resolve().parents[2] / "data"
height_map_path = data / "height_maps" / "skin_microrelief.png"

cylinder = cq.Workplane("XY").cylinder(40.0, 10.0)
model = pv.CADModel.from_cadquery(cylinder)
outer_wall = model.select_faces(surface_type="cylinder")[0]

# The PNG contains polygonal plateaus, primary and secondary furrows, and scattered pores.
# Its left and right edges match so the fitted image closes cleanly around the periodic CAD seam.
skin_height = pv.ImageHeightField(
    str(height_map_path),
    amplitude_mm=0.35,
    channel="luminance",
    mapping="fit",
)
relief = pv.SurfaceReliefVolume(
    outer_wall,
    skin_height,
    embed_mm=0.20,
    edge_falloff_mm=0.8,
)

solid = model.to_node(use_fast_mode=True)
unioned_root = pv.BBoxUnion([solid, relief])

# SurfaceReliefVolume is geometry on its own. Render unioned_root instead to attach it to the
# cylinder.
root = relief
viz.Render(root)
