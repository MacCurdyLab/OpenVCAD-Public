"""Join a Schwarz-P sheet and octet beams by keeping both in an overlap band."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


OVERLAP_HALF_WIDTH = 4.0

# This shared rectangular map aligns the sheet cells and beam cells.
cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -12.0, -8.0), pv.Vec3(24.0, 12.0, 8.0)),
    cells=(6, 3, 2),
)

# These unlike patterns are joined by overlap, not by blending their shapes.
schwarz_p = mm.schwarz_p(cell_map, wall_thickness=1.0)
octet = mm.octet(cell_map, beam_radius=0.55, node_radius=0.65)

# Both source structures remain intact through one full 8 mm cell around x = 0.
tpms_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-30.0, -18.0, -12.0),
    pv.Vec3(OVERLAP_HALF_WIDTH, 18.0, 12.0),
)
graph_region = pv.RectPrism.FromMinAndMax(
    pv.Vec3(-OVERLAP_HALF_WIDTH, -18.0, -12.0),
    pv.Vec3(30.0, 18.0, 12.0),
)
root = pv.Union(
    pv.Intersection(schwarz_p, tpms_region),
    pv.Intersection(octet, graph_region),
)
viz.Render(root)
