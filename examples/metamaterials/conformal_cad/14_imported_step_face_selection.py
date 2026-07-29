"""Select a smooth freeform face from an imported STEP file and map a cubic lattice."""

from pathlib import Path

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


model_path = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "3d_models"
    / "conformal_loft.step"
)
# Find the largest smooth B-spline face in the imported part to use as the surface.
model = pv.CADModel.from_step(str(model_path))
curved_faces = model.select_faces(surface_type="bspline")
surface = max(curved_faces, key=lambda face: face.area)

# Place a three-cell-thick cubic lattice along the selected freeform face.
cell_map = mm.cell_map_from_cad_face(
    surface,
    cells=(9, 7, 3),
    height=9.0,
)
root = mm.cubic(cell_map, beam_radius=0.42, node_radius=0.48)

viz.Render(root)
