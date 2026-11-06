"""Render the complete native mapped graph-lattice catalog."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

block = 30.0
spacing = 42.0
columns = 5
lattices = []
for index, name in enumerate(mm.LATTICE_NAMES):
    center_x = (index % columns - (columns - 1) / 2.0) * spacing
    center_y = -(index // columns) * spacing
    # Each map keeps the cell's reference U:V:W proportions, 30 mm along V.
    u, v, w = mm.reference_cell_size(name)
    half = (0.5 * block * u / v, 0.5 * block, 0.5 * block * w / v)
    cell_map = mm.rectangular_cell_map(
        (
            pv.Vec3(center_x - half[0], center_y - half[1], -half[2]),
            pv.Vec3(center_x + half[0], center_y + half[1], half[2]),
        ),
        cells=(3, 3, 3),
    )
    lattices.append(mm.graph_lattice(cell_map, name, beam_radius=0.7))

root = pv.Union(0.0, lattices)
viz.Render(root)
