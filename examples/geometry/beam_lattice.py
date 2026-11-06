"""
BeamLattice Demo - A lattice from shared vertices and indexed beams.

BeamLattice takes one vertex list plus Beam entries that index into it, which
is far more compact than one Strut per edge. A Beam with r1 and r2 tapers
from one end to the other; a Beam without radii uses the lattice radius.
BallMode.All adds a sphere at every vertex a beam ends on.

See examples/lattices/beam_lattice/ for cap modes, clipping and 3MF import.
"""
import pyvcad as pv
import pyvcad_rendering as viz

size = 10.0  # mm, half-width of the cube of nodes
radius = 0.8  # mm, default beam radius

# Eight cube corners plus a centre node.
vertices = [
    pv.Vec3(-size, -size, -size), pv.Vec3(size, -size, -size),
    pv.Vec3(size, size, -size), pv.Vec3(-size, size, -size),
    pv.Vec3(-size, -size, size), pv.Vec3(size, -size, size),
    pv.Vec3(size, size, size), pv.Vec3(-size, size, size),
    pv.Vec3(0.0, 0.0, 0.0),
]

# Twelve cube edges at the lattice radius, and eight diagonals that taper from
# a thick hub at the centre to each corner.
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
beams = [pv.Beam(v1, v2) for v1, v2 in edges]
beams += [pv.Beam(8, corner, r1=1.6, r2=0.5) for corner in range(8)]

lattice = pv.BeamLattice(vertices, beams, radius, ball_mode=pv.BallMode.All, ball_radius=1.6)

root = lattice

viz.Render(root)
