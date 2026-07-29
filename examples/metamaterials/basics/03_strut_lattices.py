"""Render the complete native mapped graph-lattice catalog."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

block = 30.0
spacing = 38.0
lattices = []
for index, name in enumerate(mm.LATTICE_NAMES):
    center_x = (index - (len(mm.LATTICE_NAMES) - 1) / 2.0) * spacing
    cell_map = mm.rectangular_cell_map(
        (
            pv.Vec3(center_x - block / 2.0, -block / 2.0, -block / 2.0),
            pv.Vec3(center_x + block / 2.0, block / 2.0, block / 2.0),
        ),
        cells=(3, 3, 3),
    )
    lattices.append(mm.graph_lattice(cell_map, name, beam_radius=0.9))

root = pv.Union(0.0, lattices)
viz.Render(root)
