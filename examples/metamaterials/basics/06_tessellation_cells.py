import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

# Catalog cells built from seeds and tessellations, left to right. Each map uses the cell's
# reference U:V:W proportions (regular hexagons, ideal bond angles, the requested re-entrant
# angle), 2 x 2 x 2 cells with 10 mm along V.
cells = [
    ("weaire_phelan", 0.4),
    ("hex_prism_diamond", 0.55),
    ("hex_prism_laves", 0.4),
    ("reentrant_3d", 0.45),
    ("column", 0.6),
    ("tet_oct_vertex_centroid", 0.45),
]

lattices = []
x = 0.0
for name, beam_radius in cells:
    u, v, w = mm.reference_cell_size(name)
    size = (20.0 * u / v, 20.0, 20.0 * w / v)
    cell_map = mm.rectangular_cell_map(
        (pv.Vec3(x, -10.0, -size[2] / 2), pv.Vec3(x + size[0], 10.0, size[2] / 2)), cells=(2, 2, 2))
    lattices.append(mm.graph_lattice(cell_map, name, beam_radius=beam_radius))
    x += size[0] + 8.0

# The walls of the triangular honeycomb as a face lattice.
u, v, w = mm.reference_cell_size("triangular_honeycomb")
wall_map = mm.rectangular_cell_map((pv.Vec3(x, -10.0, -10.0), pv.Vec3(x + 40.0 * u / v, 10.0, 10.0)),
                                   cells=(4, 2, 2))
lattices.append(mm.triangular_honeycomb(wall_map, wall_thickness=1.0))

center = (x + 20.0 * u / v) / 2.0
root = pv.Union(0.0, lattices)
viz.Render(root)
