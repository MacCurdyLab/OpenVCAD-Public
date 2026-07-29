"""
Graph Lattice Demo - Compare the built-in lattice unit cell types.

GraphLattice builds a strut-based lattice from a list of edges. Edges can be
supplied directly (List[Tuple[Vec3, Vec3]]), or generated automatically from
a built-in LatticeType preset (Cubic, BodyCenteredCubic, FaceCenteredCubic,
KelvinCell). Each preset produces a single unit cell of the requested size,
centered at the origin; repeat it into a full lattice block with Tile.

This example places one unit cell of each preset side-by-side for comparison.
"""
import pyvcad as pv
import pyvcad_rendering as viz

cell_size = pv.Vec3(10.0, 10.0, 10.0)
strut_radius = 0.6  # mm
spacing = 14.0  # mm between unit cell centers along x

lattice_types = [
    pv.LatticeType.Cubic,
    pv.LatticeType.BodyCenteredCubic,
    pv.LatticeType.FaceCenteredCubic,
    pv.LatticeType.KelvinCell,
]

cells = [pv.GraphLattice(lattice_type, cell_size, strut_radius) for lattice_type in lattice_types]
placed_cells = [pv.Translate(i * spacing, 0.0, 0.0, cell) for i, cell in enumerate(cells)]

root = placed_cells[0]
for cell in placed_cells[1:]:
    root = pv.Union(root, cell)

viz.Render(root)
