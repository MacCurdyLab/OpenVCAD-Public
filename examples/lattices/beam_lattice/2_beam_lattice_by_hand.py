"""
Authoring a BeamLattice directly.

BeamLattice is the node behind the 3MF beam lattice importer, and it is just as
usable on its own. It takes a shared vertex list plus a list of Beam entries
that index into it, which is a much more compact description than one Strut per
edge once a lattice has hundreds of members.

Anything a Beam leaves unset falls back to the lattice default, following the
resolution order the specification defines:

  both r1 and r2 given   the beam is a conical frustum
  only r1 given          the beam is a cylinder of radius r1
  neither given          the beam is a cylinder of the lattice radius

Balls are spheres centred on vertices. BallMode.All puts one on every vertex
that terminates a beam, which turns a plain truss into a rod-and-ball lattice.
"""
import pyvcad as pv
import pyvcad_rendering as viz

size = 20.0        # mm, half-width of the cube of nodes
radius = 1.2       # mm, default beam radius
ball_radius = 2.6  # mm

# Eight cube corners plus a centre node.
vertices = [
    pv.Vec3(-size, -size, -size),
    pv.Vec3(size, -size, -size),
    pv.Vec3(size, size, -size),
    pv.Vec3(-size, size, -size),
    pv.Vec3(-size, -size, size),
    pv.Vec3(size, -size, size),
    pv.Vec3(size, size, size),
    pv.Vec3(-size, size, size),
    pv.Vec3(0.0, 0.0, 0.0),
]

# The twelve cube edges inherit the lattice radius.
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]
beams = [pv.Beam(v1, v2) for v1, v2 in edges]

# The eight body diagonals taper from a thick hub down to each corner.
beams += [pv.Beam(8, corner, r1=2.4, r2=0.8) for corner in range(8)]

lattice = pv.BeamLattice(
    vertices,
    beams,
    radius,
    min_length=0.01,
    cap=pv.CapMode.Sphere,
    ball_mode=pv.BallMode.All,
    ball_radius=ball_radius,
)

print(f"beams kept: {lattice.active_beam_count}")
print(f"balls generated: {lattice.active_ball_count}")

root = lattice

viz.Render(root)
