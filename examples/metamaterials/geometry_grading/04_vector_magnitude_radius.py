"""Geometry grading: use distance from the center to drive strut radius."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cell_map = mm.rectangular_cell_map(
    (pv.Vec3(-24.0, -4.0, -24.0), pv.Vec3(24.0, 4.0, 24.0)),
    cells=(6, 1, 6),
)
planar_position = pv.Vec3Attribute("x / 24", "0", "z / 24")
radial_distance = planar_position.magnitude().clamp(0.0, 1.0)
beam_radius = radial_distance.map_range(0.0, 1.0, 0.25, 1.25)

# A one-cell-deep panel keeps the thin center struts visible from the outside.
root = mm.cubic(cell_map, beam_radius=beam_radius)
viz.Render(root)
