"""Turn a random Voronoi foam into a regular Kelvin lattice across a block."""

import pyvcad as pv
import pyvcad_metamaterials as mm
import pyvcad_rendering as viz

CELL_SIZE = 6.0        # mm, edge of the cubic cell that holds two BCC sites
BEAM_THICKNESS = 0.9   # mm
RANDOM_END = -12.0     # mm, the foam is fully random left of this x
REGULAR_START = 12.0   # mm, the lattice is fully regular right of this x
SEED = 4

host = pv.RectPrism.FromMinAndMax(pv.Vec3(-36.0, -12.0, -12.0), pv.Vec3(36.0, 12.0, 12.0))
host.prepare(pv.Vec3(0.4, 0.4, 0.4), 1.0)

# Regularity is 0 where seeds stay random and 1 where they sit on BCC sites. The Voronoi
# cells of BCC sites are Kelvin cells (truncated octahedra), so the right end is a Kelvin
# strut lattice and the middle is a foam that becomes steadily more regular.
regularity = mm.ramp(RANDOM_END, REGULAR_START, axis="x")
root = mm.voronoi_transition(
    host,
    regularity,
    kind="bcc",
    cell_size=CELL_SIZE,
    origin=(-36.0, -12.0, -12.0),  # line the Kelvin cells up with the block faces
    beam_thickness=BEAM_THICKNESS,
    seed=SEED,
)

# Random and regular regions are one Voronoi graph, so the block is a single piece.
print(mm.check_connectivity(root, voxel_size=0.25))
viz.Render(root)
