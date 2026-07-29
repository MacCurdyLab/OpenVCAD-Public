"""Fill an imported mesh with a native map-first octet lattice."""

from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

model_path = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "3d_models"
    / "utah_teapot_body.3mf"
)
teapot = pv.Mesh(str(model_path))
teapot.prepare(pv.Vec3(0.5, 0.5, 0.5), 1.0)
box_min, box_max = teapot.bounding_box()

cell_map = mm.rectangular_cell_map((box_min, box_max), cell_size=7.0)
root = pv.Intersection(teapot, mm.octet(cell_map, beam_radius=0.9))
viz.Render(root)
