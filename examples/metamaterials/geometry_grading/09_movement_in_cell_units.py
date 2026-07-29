"""Geometry grading: compare one movement across different cell sizes."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz


small_cells = mm.rectangular_cell_map(
    (pv.Vec3(-28.0, -4.0, -16.0), pv.Vec3(-4.0, 4.0, 16.0)),
    cells=(6, 1, 4),
)
large_cells = mm.rectangular_cell_map(
    (pv.Vec3(4.0, -4.0, -16.0), pv.Vec3(28.0, 4.0, 16.0)),
    cells=(3, 1, 4),
)

# The same one-millimetre X movement crosses 1/4 of a small cell but 1/8 of a large cell.
one_mm_x_step = pv.Vec3Attribute(1.0, 0.0, 0.0)


def radius_for(cell_map):
    step_in_cell_units = cell_map.to_cell_frame(one_mm_x_step)
    fraction_of_cell_crossed = abs(step_in_cell_units.x)
    return (0.2 + 3.6 * fraction_of_cell_crossed).clamp(0.4, 1.1)


small_cell_lattice = mm.cubic(small_cells, beam_radius=radius_for(small_cells))
large_cell_lattice = mm.cubic(large_cells, beam_radius=radius_for(large_cells))
root = pv.Union(small_cell_lattice, large_cell_lattice)
viz.Render(root)
