"""Fill an imported mesh with a map-first gyroid."""

from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

model_path = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "3d_models"
    / "3DBenchy.stl"
)
benchy = pv.Mesh(str(model_path))
benchy.prepare(pv.Vec3(0.5, 0.5, 0.5), 1.0)
box_min, box_max = benchy.bounding_box()

cell_map = mm.rectangular_cell_map((box_min, box_max), cell_size=6.0)
root = pv.Intersection(benchy, mm.gyroid(cell_map, wall_thickness=1.0))
viz.Render(root)
