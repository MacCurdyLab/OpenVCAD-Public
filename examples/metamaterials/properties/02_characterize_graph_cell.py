"""Measure exact coordination, length, and slenderness for an octet cell."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


cell_size = 16.0
beam_radius = 0.8
report = mm.properties.characterize_graph_cell(
    "octet",
    cell_size=cell_size,
    beam_radius=beam_radius,
)
print(report)
print("degree histogram:", report.degree_histogram)
print(
    "strut length range: {:.3f} to {:.3f} mm".format(
        report.minimum_strut_length,
        report.maximum_strut_length,
    )
)

cell_map = mm.rectangular_cell_map(
    (
        pv.Vec3(-cell_size / 2.0, -cell_size / 2.0, -cell_size / 2.0),
        pv.Vec3(cell_size / 2.0, cell_size / 2.0, cell_size / 2.0),
    ),
    cells=(1, 1, 1),
)
root = mm.octet(cell_map, beam_radius=beam_radius)
viz.Render(root)
